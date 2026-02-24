from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_clients(
    client_id: Optional[str] = None,
    viewable_only: bool = False,
    first: Optional[int] = None,
    max: Optional[int] = None,
    q: Optional[str] = None,
    search: bool = False,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List clients in the realm with advanced filtering options.

    Args:
        client_id: Filter by client ID (partial match unless search=True)
        viewable_only: Only return viewable clients
        first: Pagination offset
        max: Maximum results size
        q: Query parameter for advanced filtering
        search: Whether this is a search query (true) or getClientById query (false)
        realm: Target realm (uses default if not specified)

    Returns:
        List of client objects
    """
    params = {}
    if client_id:
        params["clientId"] = client_id
    if viewable_only:
        params["viewableOnly"] = "true"
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if q:
        params["q"] = q
    if search:
        params["search"] = "true"

    return await client._make_request("GET", "/clients", params=params, realm=realm)


@mcp.tool()
async def get_client(id: str, realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a specific client by database ID.

    Args:
        id: The client's database ID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        Client object
    """
    return await client._make_request("GET", f"/clients/{id}", realm=realm)


@mcp.tool()
async def get_client_by_clientid(
    client_id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific client by client ID.

    Args:
        client_id: The client's client_id
        realm: Target realm (uses default if not specified)

    Returns:
        Client object
    """
    clients = await client._make_request(
        "GET", "/clients", params={"clientId": client_id}, realm=realm
    )
    if clients and len(clients) > 0:
        # Find exact match
        for c in clients:
            if c.get("clientId") == client_id:
                return c
    raise Exception(f"Client with client_id '{client_id}' not found")


@mcp.tool()
async def create_client(
    client_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    enabled: bool = True,
    always_display_in_console: bool = False,
    root_url: Optional[str] = None,
    base_url: Optional[str] = None,
    admin_url: Optional[str] = None,
    redirect_uris: Optional[List[str]] = None,
    web_origins: Optional[List[str]] = None,
    protocol: str = "openid-connect",
    public_client: bool = False,
    bearer_only: bool = False,
    service_accounts_enabled: bool = False,
    authorization_services_enabled: bool = False,
    direct_access_grants_enabled: bool = False,
    implicit_flow_enabled: bool = False,
    standard_flow_enabled: bool = True,
    full_scope_allowed: bool = True,
    consent_required: bool = False,
    client_authenticator_type: str = "client-secret",
    frontchannel_logout: bool = False,
    attributes: Optional[Dict[str, str]] = None,
    default_client_scopes: Optional[List[str]] = None,
    optional_client_scopes: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new client with comprehensive configuration options.

    Args:
        client_id: Client ID (unique identifier)
        name: Display name
        description: Client description
        enabled: Whether the client is enabled
        always_display_in_console: Always display in account console
        root_url: Root URL for relative URLs
        base_url: Base URL for the client
        admin_url: Admin URL for callbacks and management
        redirect_uris: Valid redirect URIs
        web_origins: Allowed CORS origins
        protocol: Protocol (openid-connect or saml)
        public_client: Public client (no secret)
        bearer_only: Bearer-only client
        service_accounts_enabled: Enable service accounts
        authorization_services_enabled: Enable authorization services
        direct_access_grants_enabled: Enable direct access grants (password flow)
        implicit_flow_enabled: Enable implicit flow
        standard_flow_enabled: Enable standard flow (authorization code)
        full_scope_allowed: Whether client can access all roles (true = all roles, false = only assigned scopes)
        consent_required: Whether user consent is required
        client_authenticator_type: Type of client authenticator (e.g., 'client-secret', 'client-jwt')
        frontchannel_logout: Enable front-channel logout
        attributes: Custom attributes as key-value pairs
        default_client_scopes: List of default client scope names
        optional_client_scopes: List of optional client scope names
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with client creation confirmation
    """
    client_data = {
        "clientId": client_id,
        "enabled": enabled,
        "alwaysDisplayInConsole": always_display_in_console,
        "protocol": protocol,
        "publicClient": public_client,
        "bearerOnly": bearer_only,
        "serviceAccountsEnabled": service_accounts_enabled,
        "authorizationServicesEnabled": authorization_services_enabled,
        "directAccessGrantsEnabled": direct_access_grants_enabled,
        "implicitFlowEnabled": implicit_flow_enabled,
        "standardFlowEnabled": standard_flow_enabled,
        "fullScopeAllowed": full_scope_allowed,
        "consentRequired": consent_required,
        "clientAuthenticatorType": client_authenticator_type,
        "frontchannelLogout": frontchannel_logout,
    }

    if name:
        client_data["name"] = name
    if description:
        client_data["description"] = description
    if root_url:
        client_data["rootUrl"] = root_url
    if base_url:
        client_data["baseUrl"] = base_url
    if admin_url:
        client_data["adminUrl"] = admin_url
    if redirect_uris:
        client_data["redirectUris"] = redirect_uris
    if web_origins:
        client_data["webOrigins"] = web_origins
    if attributes:
        client_data["attributes"] = attributes
    if default_client_scopes:
        client_data["defaultClientScopes"] = default_client_scopes
    if optional_client_scopes:
        client_data["optionalClientScopes"] = optional_client_scopes

    await client._make_request("POST", "/clients", data=client_data, realm=realm)
    return {"status": "created", "message": f"Client {client_id} created successfully"}


@mcp.tool()
async def update_client(
    id: str,
    client_id: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
    redirect_uris: Optional[List[str]] = None,
    web_origins: Optional[List[str]] = None,
    public_client: Optional[bool] = None,
    service_accounts_enabled: Optional[bool] = None,
    direct_access_grants_enabled: Optional[bool] = None,
    # Priority 1: Parameters from create_client
    standard_flow_enabled: Optional[bool] = None,
    implicit_flow_enabled: Optional[bool] = None,
    bearer_only: Optional[bool] = None,
    authorization_services_enabled: Optional[bool] = None,
    always_display_in_console: Optional[bool] = None,
    root_url: Optional[str] = None,
    base_url: Optional[str] = None,
    admin_url: Optional[str] = None,
    protocol: Optional[str] = None,
    # Priority 2: Critical OAuth2/OIDC parameters
    full_scope_allowed: Optional[bool] = None,
    consent_required: Optional[bool] = None,
    client_authenticator_type: Optional[str] = None,
    frontchannel_logout: Optional[bool] = None,
    # Priority 3: Advanced configuration
    surrogate_auth_required: Optional[bool] = None,
    not_before: Optional[int] = None,
    node_reregistration_timeout: Optional[int] = None,
    attributes: Optional[Dict[str, str]] = None,
    authentication_flow_binding_overrides: Optional[Dict[str, str]] = None,
    default_client_scopes: Optional[List[str]] = None,
    optional_client_scopes: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing client with commonly used parameters.

    Args:
        id: The client's database ID
        client_id: New client ID
        name: New display name
        description: New description
        enabled: Whether the client is enabled
        redirect_uris: New redirect URIs
        web_origins: New CORS origins
        public_client: Whether client is public
        service_accounts_enabled: Enable service accounts
        direct_access_grants_enabled: Enable direct access grants
        standard_flow_enabled: Enable standard flow (authorization code)
        implicit_flow_enabled: Enable implicit flow
        bearer_only: Bearer-only client
        authorization_services_enabled: Enable authorization services
        always_display_in_console: Always display in account console
        root_url: Root URL for relative URLs
        base_url: Base URL for the client
        admin_url: Admin URL for the client
        protocol: Protocol (openid-connect or saml)
        full_scope_allowed: Whether client can access all roles (false = only assigned scopes)
        consent_required: Whether user consent is required
        client_authenticator_type: Type of client authenticator (e.g., 'client-secret', 'client-jwt')
        frontchannel_logout: Enable front-channel logout
        surrogate_auth_required: Whether surrogate authentication is required
        not_before: Not before timestamp
        node_reregistration_timeout: Timeout for node re-registration
        attributes: Custom attributes as key-value pairs
        authentication_flow_binding_overrides: Authentication flow overrides
        default_client_scopes: List of default client scope names
        optional_client_scopes: List of optional client scope names
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current client data
    current_client = await client._make_request("GET", f"/clients/{id}", realm=realm)

    # Update only provided fields
    if client_id is not None:
        current_client["clientId"] = client_id
    if name is not None:
        current_client["name"] = name
    if description is not None:
        current_client["description"] = description
    if enabled is not None:
        current_client["enabled"] = enabled
    if redirect_uris is not None:
        current_client["redirectUris"] = redirect_uris
    if web_origins is not None:
        current_client["webOrigins"] = web_origins
    if public_client is not None:
        current_client["publicClient"] = public_client
    if service_accounts_enabled is not None:
        current_client["serviceAccountsEnabled"] = service_accounts_enabled
    if direct_access_grants_enabled is not None:
        current_client["directAccessGrantsEnabled"] = direct_access_grants_enabled

    # Priority 1: Parameters from create_client
    if standard_flow_enabled is not None:
        current_client["standardFlowEnabled"] = standard_flow_enabled
    if implicit_flow_enabled is not None:
        current_client["implicitFlowEnabled"] = implicit_flow_enabled
    if bearer_only is not None:
        current_client["bearerOnly"] = bearer_only
    if authorization_services_enabled is not None:
        current_client["authorizationServicesEnabled"] = authorization_services_enabled
    if always_display_in_console is not None:
        current_client["alwaysDisplayInConsole"] = always_display_in_console
    if root_url is not None:
        current_client["rootUrl"] = root_url
    if base_url is not None:
        current_client["baseUrl"] = base_url
    if admin_url is not None:
        current_client["adminUrl"] = admin_url
    if protocol is not None:
        current_client["protocol"] = protocol

    # Priority 2: Critical OAuth2/OIDC parameters
    if full_scope_allowed is not None:
        current_client["fullScopeAllowed"] = full_scope_allowed
    if consent_required is not None:
        current_client["consentRequired"] = consent_required
    if client_authenticator_type is not None:
        current_client["clientAuthenticatorType"] = client_authenticator_type
    if frontchannel_logout is not None:
        current_client["frontchannelLogout"] = frontchannel_logout

    # Priority 3: Advanced configuration
    if surrogate_auth_required is not None:
        current_client["surrogateAuthRequired"] = surrogate_auth_required
    if not_before is not None:
        current_client["notBefore"] = not_before
    if node_reregistration_timeout is not None:
        current_client["nodeReRegistrationTimeout"] = node_reregistration_timeout
    if attributes is not None:
        current_client["attributes"] = attributes
    if authentication_flow_binding_overrides is not None:
        current_client["authenticationFlowBindingOverrides"] = (
            authentication_flow_binding_overrides
        )
    if default_client_scopes is not None:
        current_client["defaultClientScopes"] = default_client_scopes
    if optional_client_scopes is not None:
        current_client["optionalClientScopes"] = optional_client_scopes

    await client._make_request(
        "PUT", f"/clients/{id}", data=current_client, realm=realm
    )
    return {"status": "updated", "message": f"Client {id} updated successfully"}


@mcp.tool()
async def update_client_advanced(
    id: str,
    client_representation: Dict[str, Any],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a client with full control using raw ClientRepresentation object.

    This is an advanced tool for power users who need to update client properties
    not covered by the standard update_client tool. The provided client_representation
    will be merged with the current client configuration.

    Args:
        id: The client's database ID
        client_representation: Partial or full ClientRepresentation object as a dict
        realm: Target realm (uses default if not specified)

    Returns:
        Status message

    Example client_representation:
        {
            "fullScopeAllowed": false,
            "attributes": {
                "custom.attribute": "value"
            },
            "protocolMappers": [...],
            "authorizationSettings": {...}
        }

    See Keycloak ClientRepresentation documentation for all available properties:
    https://www.keycloak.org/docs-api/latest/rest-api/index.html
    """
    # Get current client data
    current_client = await client._make_request("GET", f"/clients/{id}", realm=realm)

    # Merge the provided representation with current client
    # This allows partial updates while preserving unspecified fields
    current_client.update(client_representation)

    await client._make_request(
        "PUT", f"/clients/{id}", data=current_client, realm=realm
    )
    return {
        "status": "updated",
        "message": f"Client {id} updated successfully with advanced configuration",
    }


@mcp.tool()
async def delete_client(id: str, realm: Optional[str] = None) -> Dict[str, str]:
    """
    Delete a client.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/clients/{id}", realm=realm)
    return {"status": "deleted", "message": f"Client {id} deleted successfully"}


@mcp.tool()
async def get_client_secret(id: str, realm: Optional[str] = None) -> Dict[str, str]:
    """
    Get the client secret.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Client secret object
    """
    return await client._make_request(
        "GET", f"/clients/{id}/client-secret", realm=realm
    )


@mcp.tool()
async def regenerate_client_secret(
    id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Regenerate the client secret.

    When client secret rotation is enabled via client policies, this operation
    will preserve the old secret as a "rotated secret" that remains valid for
    a grace period. This allows seamless secret rotation without downtime.

    The old secret can be retrieved via get_client_secret_rotated() and
    invalidated via delete_client_secret_rotated().

    Note: Secret rotation behavior is controlled by realm-level client policies.
    If rotation policies are not configured, the old secret is immediately
    invalidated.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        New client secret object

    See Also:
        - get_client_secret_rotated() - Retrieve the previous secret
        - delete_client_secret_rotated() - Invalidate the previous secret
    """
    return await client._make_request(
        "POST", f"/clients/{id}/client-secret", realm=realm
    )


@mcp.tool()
async def get_client_secret_rotated(
    id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the rotated client secret (the previous secret after rotation).

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Rotated client secret credential object containing the previous secret
    """
    return await client._make_request(
        "GET", f"/clients/{id}/client-secret/rotated", realm=realm
    )


@mcp.tool()
async def delete_client_secret_rotated(
    id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Invalidate the rotated client secret.

    This removes the previous secret that was kept after rotation,
    forcing all clients to use only the current secret.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/clients/{id}/client-secret/rotated", realm=realm
    )
    return {
        "status": "deleted",
        "message": f"Rotated client secret for client {id} invalidated successfully",
    }


@mcp.tool()
async def get_client_service_account(
    id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get service account user for a client.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Service account user object
    """
    return await client._make_request(
        "GET", f"/clients/{id}/service-account-user", realm=realm
    )


@mcp.tool()
async def list_client_default_client_scopes(
    id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List default client scopes for a client.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of default client scope objects
    """
    return await client._make_request(
        "GET", f"/clients/{id}/default-client-scopes", realm=realm
    )


@mcp.tool()
async def update_client_default_client_scope(
    id: str, client_scope_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Add a default client scope to a client.

    Args:
        id: The client's database ID
        client_scope_id: The client scope ID to add as default
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/clients/{id}/default-client-scopes/{client_scope_id}", realm=realm
    )
    return {
        "status": "updated",
        "message": f"Client scope {client_scope_id} added as default to client {id}",
    }


@mcp.tool()
async def delete_client_default_client_scope(
    id: str, client_scope_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Remove a default client scope from a client.

    Args:
        id: The client's database ID
        client_scope_id: The client scope ID to remove from defaults
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/clients/{id}/default-client-scopes/{client_scope_id}", realm=realm
    )
    return {
        "status": "deleted",
        "message": f"Client scope {client_scope_id} removed from client {id} defaults",
    }


@mcp.tool()
async def get_client_management_permissions(
    id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get management permissions for a client.

    Returns whether client authorization permissions have been initialized
    and provides a reference to the resource server managing these permissions.

    Args:
        id: The client's database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Management permission reference object with 'enabled' status and
        'resource' information if permissions are initialized
    """
    return await client._make_request(
        "GET", f"/clients/{id}/management/permissions", realm=realm
    )


@mcp.tool()
async def update_client_management_permissions(
    id: str, enabled: bool, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enable or disable management permissions for a client.

    When enabled, Keycloak creates a resource server that allows fine-grained
    authorization control over who can manage this client. This is useful for
    delegating client management to non-admin users.

    Args:
        id: The client's database ID
        enabled: Whether to enable (True) or disable (False) management permissions
        realm: Target realm (uses default if not specified)

    Returns:
        Updated management permission reference object with 'enabled' status
        and 'resource' information if permissions are enabled
    """
    return await client._make_request(
        "PUT",
        f"/clients/{id}/management/permissions",
        data={"enabled": enabled},
        realm=realm,
    )
