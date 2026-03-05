import httpx
from typing import Dict, Any, Optional
from ..common.config import KEYCLOAK_CFG
from ..common.const import DEFAULT_REALM, DEFAULT_REQUEST_TIMEOUT


class KeycloakClient:
    def __init__(self):
        self.server_url = KEYCLOAK_CFG["server_url"]
        self.username = KEYCLOAK_CFG["username"]
        self.password = KEYCLOAK_CFG["password"]
        self.realm_name = (
            KEYCLOAK_CFG["realm_name"] if KEYCLOAK_CFG["realm_name"] else DEFAULT_REALM
        )
        self.client_id = KEYCLOAK_CFG["client_id"]
        self.client_secret = KEYCLOAK_CFG["client_secret"]
        self.token = None
        self.refresh_token = None
        self._client = None

    async def _ensure_client(self):
        """Ensure httpx async client exists and is usable"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=DEFAULT_REQUEST_TIMEOUT)
        return self._client

    async def _get_token(self) -> str:
        """Get admin access token from realm 'master'"""
        # token endpoint is always in master realm for admin operations
        token_url = f"{self.server_url}/realms/master/protocol/openid-connect/token"

        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": "admin-cli",  # Using admin-cli for admin operations
        }

        client = await self._ensure_client()
        response = await client.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")

        return self.token

    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token"""
        if not self.token:
            await self._get_token()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        skip_realm: bool = False,
        realm: Optional[str] = None,
        content_type: str = "application/json",
        require_auth: bool = True,
    ) -> Any:
        """Make authenticated request to Keycloak API

        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: Request data (JSON or form data)
            params: Query parameters
            skip_realm: Skip realm in URL path
            realm: Target realm (uses default if not specified)
            content_type: Content type for request (application/json or application/x-www-form-urlencoded)
            require_auth: Whether authentication is required (False for public endpoints)
        """
        # Build URL based on endpoint type
        if endpoint.startswith("/protocol/"):
            # Public OIDC/SAML endpoints (no /admin prefix)
            target_realm = realm if realm is not None else self.realm_name
            url = f"{self.server_url}/realms/{target_realm}{endpoint}"
        elif skip_realm:
            # Admin endpoints without realm
            url = f"{self.server_url}/admin{endpoint}"
        else:
            # Standard admin endpoints with realm
            target_realm = realm if realm is not None else self.realm_name
            url = f"{self.server_url}/admin/realms/{target_realm}{endpoint}"

        try:
            client = await self._ensure_client()

            # Prepare headers
            if require_auth:
                headers = await self._get_headers()
                headers["Content-Type"] = content_type
            else:
                headers = {"Content-Type": content_type}

            # Prepare request kwargs
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
            }

            # Add data based on content type
            if data:
                if content_type == "application/x-www-form-urlencoded":
                    request_kwargs["data"] = data
                else:
                    request_kwargs["json"] = data

            response = await client.request(**request_kwargs)

            # If token expired and auth is required, refresh and retry
            if response.status_code == 401 and require_auth:
                await self._get_token()
                headers = await self._get_headers()
                headers["Content-Type"] = content_type
                request_kwargs["headers"] = headers
                response = await client.request(**request_kwargs)

            response.raise_for_status()

            if response.content:
                return response.json()
            return None

        except httpx.HTTPStatusError as e:
            # Include response body in error for debugging
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = f" - {error_body}"
            except Exception:
                error_detail = f" - {e.response.text}"
            raise Exception(
                f"Keycloak API request failed: {e.response.status_code} {e.response.reason_phrase}{error_detail}"
            )
        except httpx.RequestError as e:
            raise Exception(f"Keycloak API request failed: {str(e)}")

    async def close(self):
        """Close the httpx client"""
        if self._client:
            await self._client.aclose()
            self._client = None
