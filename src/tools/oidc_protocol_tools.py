from typing import Dict, Any, Optional
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def request_token(
    grant_type: str,
    client_id: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    client_secret: Optional[str] = None,
    code: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    refresh_token: Optional[str] = None,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Request OAuth2/OIDC tokens using various grant types.

    Supports multiple OAuth2 grant types including password, authorization_code,
    refresh_token, and client_credentials. This is a public endpoint that does
    not require admin authentication.

    Args:
        grant_type: OAuth2 grant type (password, authorization_code, refresh_token, client_credentials)
        client_id: OAuth2 client ID
        username: Username (required for password grant)
        password: Password (required for password grant)
        client_secret: Client secret (required for confidential clients)
        code: Authorization code (required for authorization_code grant)
        redirect_uri: Redirect URI (required for authorization_code grant)
        refresh_token: Refresh token (required for refresh_token grant)
        scope: OAuth2 scope (optional, e.g., 'openid profile email')
        realm: Target realm (uses default if not specified)

    Returns:
        Token response containing access_token, refresh_token (if applicable),
        token_type, expires_in, and other token metadata

    Examples:
        Password grant:
            request_token(grant_type="password", client_id="my-client",
                         username="user", password="pass", scope="openid")

        Client credentials:
            request_token(grant_type="client_credentials", client_id="my-client",
                         client_secret="secret", scope="openid")

        Refresh token:
            request_token(grant_type="refresh_token", client_id="my-client",
                         refresh_token="refresh_token_value")
    """
    # Build form data based on grant type
    form_data = {
        "grant_type": grant_type,
        "client_id": client_id,
    }

    # Add client secret if provided
    if client_secret:
        form_data["client_secret"] = client_secret

    # Add scope if provided
    if scope:
        form_data["scope"] = scope

    # Add grant-specific parameters
    if grant_type == "password":
        if not username or not password:
            raise ValueError("Username and password are required for password grant")
        form_data["username"] = username
        form_data["password"] = password

    elif grant_type == "authorization_code":
        if not code or not redirect_uri:
            raise ValueError(
                "Code and redirect_uri are required for authorization_code grant"
            )
        form_data["code"] = code
        form_data["redirect_uri"] = redirect_uri

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise ValueError("Refresh token is required for refresh_token grant")
        form_data["refresh_token"] = refresh_token

    elif grant_type == "client_credentials":
        if not client_secret:
            raise ValueError("Client secret is required for client_credentials grant")

    # Make request to the public token endpoint
    # Note: This is a public endpoint, not an admin endpoint
    return await client._make_request(
        "POST",
        "/protocol/openid-connect/token",
        data=form_data,
        realm=realm,
        content_type="application/x-www-form-urlencoded",
        require_auth=False,  # Public endpoint, no authentication required
    )


@mcp.tool()
async def introspect_token(
    token: str,
    client_id: str,
    client_secret: Optional[str] = None,
    token_type_hint: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Introspect an OAuth2 token to validate its state and retrieve metadata.

    Validates tokens and returns their associated metadata including expiration,
    scope, username, client_id, and permissions. Compliant with RFC 7662.
    Requires client authentication.

    Args:
        token: The token to introspect (access_token or refresh_token)
        client_id: OAuth2 client ID performing the introspection
        client_secret: Client secret (required for confidential clients)
        token_type_hint: Hint about token type ('access_token' or 'refresh_token')
        realm: Target realm (uses default if not specified)

    Returns:
        Introspection response containing:
        - active: Boolean indicating if token is active
        - exp: Token expiration timestamp
        - iat: Token issued at timestamp
        - scope: Token scopes
        - username: Associated username (if applicable)
        - client_id: Client that requested the token
        - token_type: Type of token (Bearer, etc.)
        - Additional claims depending on token configuration

    Examples:
        Basic introspection:
            introspect_token(token="access_token_value", client_id="my-client",
                           client_secret="secret")

        With type hint:
            introspect_token(token="token_value", client_id="my-client",
                           client_secret="secret", token_type_hint="access_token")
    """
    # Build form data
    form_data = {
        "token": token,
        "client_id": client_id,
    }

    # Add client secret if provided
    if client_secret:
        form_data["client_secret"] = client_secret

    # Add token type hint if provided
    if token_type_hint:
        form_data["token_type_hint"] = token_type_hint

    # Make request to the public token introspection endpoint
    return await client._make_request(
        "POST",
        "/protocol/openid-connect/token/introspect",
        data=form_data,
        realm=realm,
        content_type="application/x-www-form-urlencoded",
        require_auth=False,  # Public endpoint, no authentication required
    )
