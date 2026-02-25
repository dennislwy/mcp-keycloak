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
            raise ValueError("Code and redirect_uri are required for authorization_code grant")
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


@mcp.tool()
async def get_userinfo(
    access_token: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get user information from the UserInfo endpoint.

    Returns user claims as described in the OpenID Connect specification.
    Requires a valid access token obtained through the authorization flow.

    Args:
        access_token: Valid OAuth2 access token
        realm: Target realm (uses default if not specified)

    Returns:
        User information containing claims such as:
        - sub: Subject identifier
        - name: Full name
        - given_name: Given name
        - family_name: Family name
        - preferred_username: Preferred username
        - email: Email address
        - email_verified: Email verification status
        - Additional custom claims based on token scopes

    Example:
        get_userinfo(access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
    """
    # UserInfo endpoint requires Bearer token authentication
    # We need to make the request directly with the access token
    target_realm = realm if realm is not None else client.realm_name
    url = f"{client.server_url}/realms/{target_realm}/protocol/openid-connect/userinfo"

    httpx_client = await client._ensure_client()
    response = await httpx_client.get(url, headers={"Authorization": f"Bearer {access_token}"})
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def revoke_token(
    token: str,
    client_id: str,
    client_secret: Optional[str] = None,
    token_type_hint: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Revoke an OAuth2 token (access token or refresh token).

    Invalidates tokens to prevent further use. Compliant with RFC 7009.
    Requires client authentication.

    Args:
        token: The token to revoke (access_token or refresh_token)
        client_id: OAuth2 client ID performing the revocation
        client_secret: Client secret (required for confidential clients)
        token_type_hint: Hint about token type ('access_token' or 'refresh_token')
        realm: Target realm (uses default if not specified)

    Returns:
        Empty dict on success (endpoint returns 200 with no content)

    Example:
        revoke_token(token="refresh_token_value", client_id="my-client",
                    client_secret="secret", token_type_hint="refresh_token")
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

    # Make request to the revocation endpoint
    return await client._make_request(
        "POST",
        "/protocol/openid-connect/revoke",
        data=form_data,
        realm=realm,
        content_type="application/x-www-form-urlencoded",
        require_auth=False,  # Public endpoint, no authentication required
    )


@mcp.tool()
async def logout(
    refresh_token: str,
    client_id: str,
    client_secret: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Logout and invalidate the user session.

    Performs logout by invalidating the refresh token and ending the user's session.
    This is the OIDC logout endpoint that requires a refresh token.

    Args:
        refresh_token: The refresh token to invalidate
        client_id: OAuth2 client ID
        client_secret: Client secret (required for confidential clients)
        realm: Target realm (uses default if not specified)

    Returns:
        Empty dict on success (endpoint returns 204 or 200 with no content)

    Example:
        logout(refresh_token="refresh_token_value", client_id="my-client",
              client_secret="secret")
    """
    # Build form data
    form_data = {
        "client_id": client_id,
        "refresh_token": refresh_token,
    }

    # Add client secret if provided
    if client_secret:
        form_data["client_secret"] = client_secret

    # Make request to the logout endpoint
    return await client._make_request(
        "POST",
        "/protocol/openid-connect/logout",
        data=form_data,
        realm=realm,
        content_type="application/x-www-form-urlencoded",
        require_auth=False,  # Public endpoint, no authentication required
    )


@mcp.tool()
async def exchange_token(
    subject_token: str,
    client_id: str,
    client_secret: Optional[str] = None,
    audience: Optional[str] = None,
    subject_token_type: str = "urn:ietf:params:oauth:token-type:access_token",
    requested_token_type: str = "urn:ietf:params:oauth:token-type:access_token",
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Exchange an OAuth2 token for another token using RFC 8693 Token Exchange.

    Performs a Standard Token Exchange, allowing a client to exchange a token
    issued for one audience/service for a token targeting a different audience.
    Requires the exchanging client to have 'Standard Token Exchange' enabled and
    the subject token must include the exchanging client in its audience.

    Args:
        subject_token: The token to exchange (typically an access token)
        client_id: OAuth2 client ID performing the exchange (must have token exchange enabled)
        client_secret: Client secret (required for confidential clients)
        audience: Target client or resource for the new token (e.g., 'vds')
        subject_token_type: Token type of subject_token (default: access_token URN)
        requested_token_type: Desired token type for the result (default: access_token URN)
        scope: Optional scope to request on the new token
        realm: Target realm (uses default if not specified)

    Returns:
        Token response containing access_token, token_type, expires_in,
        issued_token_type, and other token metadata

    Example:
        exchange_token(
            subject_token="eyJhbGci...",
            client_id="eca-central-service",
            client_secret="secret",
            audience="vds"
        )
    """
    form_data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "client_id": client_id,
        "subject_token": subject_token,
        "subject_token_type": subject_token_type,
        "requested_token_type": requested_token_type,
    }

    if client_secret:
        form_data["client_secret"] = client_secret

    if audience:
        form_data["audience"] = audience

    if scope:
        form_data["scope"] = scope

    return await client._make_request(
        "POST",
        "/protocol/openid-connect/token",
        data=form_data,
        realm=realm,
        content_type="application/x-www-form-urlencoded",
        require_auth=False,
    )


@mcp.tool()
async def get_certs(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the JSON Web Key Set (JWKS) for the realm.

    Returns the public keys used by the realm to sign tokens, encoded as
    JSON Web Keys (JWK). Clients use these keys to verify JWT signatures.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        JWKS object containing:
        - keys: Array of JWK objects with public key information
          - kid: Key ID
          - kty: Key type (RSA, EC, etc.)
          - alg: Algorithm
          - use: Key usage (sig for signature)
          - n: RSA public key modulus (for RSA keys)
          - e: RSA public key exponent (for RSA keys)
          - Additional key-specific parameters

    Example:
        get_certs()  # Returns all public keys for signature verification
    """
    return await client._make_request(
        "GET",
        "/protocol/openid-connect/certs",
        realm=realm,
        require_auth=False,  # Public endpoint
    )


@mcp.tool()
async def get_openid_configuration(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the OpenID Connect discovery document (well-known configuration).

    Returns the OIDC provider metadata as specified in OpenID Connect Discovery.
    This document describes the realm's OpenID Connect configuration including
    all available endpoints, supported features, and capabilities.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        OpenID Connect configuration containing:
        - issuer: The issuer identifier
        - authorization_endpoint: OAuth2 authorization endpoint
        - token_endpoint: Token endpoint
        - token_introspection_endpoint: Token introspection endpoint
        - userinfo_endpoint: UserInfo endpoint
        - end_session_endpoint: Logout endpoint
        - jwks_uri: JSON Web Key Set endpoint
        - check_session_iframe: Session check endpoint
        - grant_types_supported: Supported OAuth2 grant types
        - response_types_supported: Supported response types
        - subject_types_supported: Subject identifier types
        - id_token_signing_alg_values_supported: Signing algorithms
        - scopes_supported: Available scopes
        - claims_supported: Available claims
        - Additional metadata about realm capabilities

    Example:
        get_openid_configuration()  # Get full OIDC discovery document
    """
    # Discovery endpoint is at /realms/{realm}/.well-known/openid-configuration
    # It's a public endpoint, not under /admin/
    target_realm = realm if realm is not None else client.realm_name
    url = f"{client.server_url}/realms/{target_realm}/.well-known/openid-configuration"

    httpx_client = await client._ensure_client()
    response = await httpx_client.get(url)
    response.raise_for_status()
    return response.json()
