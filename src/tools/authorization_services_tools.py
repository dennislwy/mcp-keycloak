"""
Keycloak Authorization Services Management Tools

This module provides comprehensive tools for managing Keycloak Authorization Services,
enabling fine-grained authorization for applications.

Authorization Services Overview:
- Resource Servers: Clients that act as resource servers with authorization enabled
- Resources: Protected entities (APIs, files, pages, etc.)
- Scopes: Actions that can be performed on resources (read, write, delete, etc.)
- Policies: Conditions that must be satisfied for access (role-based, user-based, time-based, etc.)
- Permissions: Links between resources/scopes and policies

Common Workflow:
1. Enable authorization services on a client
2. Create resources and scopes
3. Define policies (role, user, group, time, etc.)
4. Create permissions linking resources to policies
5. Test authorization using policy evaluation

Note: All operations require the client UUID (database ID). The tools accept either
the clientId string or UUID and will handle conversion automatically.

Phase 3.4: Authorization Services (Core Features)
"""

from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# ============================================================================
# Helper Functions
# ============================================================================


async def _get_client_uuid(client_id: str, realm: Optional[str] = None) -> str:
    """
    Convert clientId to UUID for API calls.

    Authorization Services API requires the client's database UUID, not the clientId string.
    This helper accepts either and returns the UUID.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        realm: Target realm (uses default if not specified)

    Returns:
        Client UUID

    Raises:
        Exception: If client not found
    """
    # If it looks like a UUID, return as-is
    if len(client_id) == 36 and client_id.count("-") == 4:
        return client_id

    # Otherwise, look up by clientId
    clients = await client._make_request(
        "GET", "/clients", params={"clientId": client_id}, realm=realm
    )

    if not clients or len(clients) == 0:
        raise ValueError(f"Client '{client_id}' not found")

    return clients[0]["id"]


# ============================================================================
# Phase 1: Resource Server Settings (3 tools)
# ============================================================================


@mcp.tool()
async def get_resource_server_settings(
    client_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get authorization services settings for a resource server.

    Returns the configuration for authorization services on a client, including
    policy enforcement mode, decision strategy, and other settings.

    Use this to verify that authorization services are enabled and to review
    the current configuration.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        realm: Target realm (uses default if not specified)

    Returns:
        Resource server configuration including:
        - id: Resource server ID
        - clientId: Associated client ID
        - policyEnforcementMode: "ENFORCING", "PERMISSIVE", or "DISABLED"
        - decisionStrategy: "UNANIMOUS", "AFFIRMATIVE", or "CONSENSUS"
        - allowRemoteResourceManagement: Whether remote resource management is enabled

    Example:
        ```python
        settings = await get_resource_server_settings("my-api-client")
        print(f"Policy enforcement: {settings['policyEnforcementMode']}")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)
    return await client._make_request(
        "GET", f"/clients/{uuid}/authz/resource-server", realm=realm
    )


@mcp.tool()
async def enable_authorization_services(
    client_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Enable authorization services on a client.

    This enables the authorization services feature for a confidential client,
    allowing it to act as a resource server with fine-grained permissions.

    Prerequisites:
    - Client must be confidential (not public)
    - Service accounts must be enabled on the client

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message confirming authorization services were enabled

    Example:
        ```python
        result = await enable_authorization_services("my-api-client")
        print(result["message"])
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    # Get current client configuration
    client_data = await client._make_request("GET", f"/clients/{uuid}", realm=realm)

    # Enable authorization services
    client_data["authorizationServicesEnabled"] = True
    client_data["serviceAccountsEnabled"] = True  # Required for authz

    await client._make_request("PUT", f"/clients/{uuid}", data=client_data, realm=realm)

    return {
        "status": "enabled",
        "client_id": client_id,
        "message": f"Authorization services enabled for client '{client_id}'",
    }


@mcp.tool()
async def update_resource_server_settings(
    client_id: str,
    policy_enforcement_mode: Optional[str] = None,
    decision_strategy: Optional[str] = None,
    allow_remote_resource_management: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update authorization services settings for a resource server.

    Configure how the resource server enforces policies and makes authorization decisions.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        policy_enforcement_mode: Policy enforcement mode (optional)
            - "ENFORCING": Requests are denied by default unless a permission grants access
            - "PERMISSIVE": Requests are allowed by default unless a permission denies access
            - "DISABLED": No policy enforcement, all requests allowed
        decision_strategy: How to evaluate multiple policies (optional)
            - "UNANIMOUS": All policies must grant access
            - "AFFIRMATIVE": At least one policy must grant access
            - "CONSENSUS": Majority of policies must grant access
        allow_remote_resource_management: Allow remote management of resources (optional)
        realm: Target realm (uses default if not specified)

    Returns:
        Updated resource server settings

    Example:
        ```python
        settings = await update_resource_server_settings(
            "my-api-client",
            policy_enforcement_mode="ENFORCING",
            decision_strategy="AFFIRMATIVE"
        )
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    # Get current settings
    current = await client._make_request(
        "GET", f"/clients/{uuid}/authz/resource-server", realm=realm
    )

    # Update specified fields
    if policy_enforcement_mode is not None:
        current["policyEnforcementMode"] = policy_enforcement_mode
    if decision_strategy is not None:
        current["decisionStrategy"] = decision_strategy
    if allow_remote_resource_management is not None:
        current["allowRemoteResourceManagement"] = allow_remote_resource_management

    return await client._make_request(
        "PUT", f"/clients/{uuid}/authz/resource-server", data=current, realm=realm
    )


# ============================================================================
# Phase 2: Resource Management (8 tools)
# ============================================================================


@mcp.tool()
async def list_resources(
    client_id: str,
    name: Optional[str] = None,
    uri: Optional[str] = None,
    owner: Optional[str] = None,
    resource_type: Optional[str] = None,
    scope: Optional[str] = None,
    first: Optional[int] = None,
    max: Optional[int] = None,
    deep: bool = False,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List authorization resources for a resource server.

    Resources represent the protected entities that require authorization.
    This can be APIs, files, pages, or any other protected asset.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        name: Filter by resource name (optional)
        uri: Filter by resource URI (optional)
        owner: Filter by owner user ID (optional)
        resource_type: Filter by resource type (optional)
        scope: Filter by associated scope name (optional)
        first: Pagination offset (optional)
        max: Maximum results to return (optional)
        deep: Include detailed information (optional, default: False)
        realm: Target realm (uses default if not specified)

    Returns:
        List of resources, each containing:
        - _id: Resource ID
        - name: Resource name
        - type: Resource type
        - uris: List of URIs
        - scopes: List of associated scopes
        - owner: Resource owner
        - ownerManagedAccess: Whether owner can manage access

    Example:
        ```python
        # List all resources
        resources = await list_resources("my-api-client")

        # Find resources by type
        api_resources = await list_resources("my-api-client", resource_type="urn:api:endpoint")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    params = {}
    if name:
        params["name"] = name
    if uri:
        params["uri"] = uri
    if owner:
        params["owner"] = owner
    if resource_type:
        params["type"] = resource_type
    if scope:
        params["scope"] = scope
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if deep:
        params["deep"] = "true"

    return await client._make_request(
        "GET", f"/clients/{uuid}/authz/resource-server/resource", params=params, realm=realm
    )


@mcp.tool()
async def search_resources(
    client_id: str,
    name: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search for resources by name.

    Convenience function for name-based resource search.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        name: Resource name to search for
        realm: Target realm (uses default if not specified)

    Returns:
        List of matching resources

    Example:
        ```python
        resources = await search_resources("my-api-client", "user-profile")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    return await client._make_request(
        "GET",
        f"/clients/{uuid}/authz/resource-server/resource/search",
        params={"name": name},
        realm=realm,
    )


@mcp.tool()
async def get_resource(
    client_id: str,
    resource_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific authorization resource.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        resource_id: Resource ID
        realm: Target realm (uses default if not specified)

    Returns:
        Resource details including ID, name, type, URIs, scopes, and owner

    Example:
        ```python
        resource = await get_resource("my-api-client", "resource-uuid")
        print(f"Resource: {resource['name']}")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    return await client._make_request(
        "GET", f"/clients/{uuid}/authz/resource-server/resource/{resource_id}", realm=realm
    )


@mcp.tool()
async def create_resource(
    client_id: str,
    name: str,
    resource_type: Optional[str] = None,
    uris: Optional[List[str]] = None,
    scopes: Optional[List[str]] = None,
    icon_uri: Optional[str] = None,
    owner_managed_access: bool = False,
    display_name: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new authorization resource.

    Resources represent protected entities that require authorization.
    Each resource can have multiple URIs, scopes, and metadata.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        name: Unique resource name
        resource_type: Resource type identifier (optional, e.g., "urn:api:endpoint")
        uris: List of URIs associated with this resource (optional)
        scopes: List of scope names associated with this resource (optional)
        icon_uri: Icon URI for UI display (optional)
        owner_managed_access: Enable user-managed access (UMA) (default: False)
        display_name: Human-readable display name (optional)
        attributes: Custom attributes as key-value pairs (optional)
        realm: Target realm (uses default if not specified)

    Returns:
        Created resource with ID

    Example:
        ```python
        resource = await create_resource(
            "my-api-client",
            name="user-profile-api",
            resource_type="urn:api:endpoint",
            uris=["/api/users/*"],
            scopes=["read", "write"]
        )
        print(f"Created resource: {resource['_id']}")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    data = {
        "name": name,
        "ownerManagedAccess": owner_managed_access,
    }

    if resource_type:
        data["type"] = resource_type
    if uris:
        data["uris"] = uris
    if scopes:
        # Scopes can be scope names or scope objects
        data["scopes"] = [{"name": s} if isinstance(s, str) else s for s in scopes]
    if icon_uri:
        data["icon_uri"] = icon_uri
    if display_name:
        data["displayName"] = display_name
    if attributes:
        data["attributes"] = attributes

    return await client._make_request(
        "POST", f"/clients/{uuid}/authz/resource-server/resource", data=data, realm=realm
    )


@mcp.tool()
async def update_resource(
    client_id: str,
    resource_id: str,
    name: Optional[str] = None,
    resource_type: Optional[str] = None,
    uris: Optional[List[str]] = None,
    scopes: Optional[List[str]] = None,
    icon_uri: Optional[str] = None,
    owner_managed_access: Optional[bool] = None,
    display_name: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an authorization resource.

    Updates the specified resource with new values. Only provided fields are updated.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        resource_id: Resource ID to update
        name: New resource name (optional)
        resource_type: New resource type (optional)
        uris: New list of URIs (optional)
        scopes: New list of scope names (optional)
        icon_uri: New icon URI (optional)
        owner_managed_access: Enable/disable user-managed access (optional)
        display_name: New display name (optional)
        attributes: New custom attributes (optional)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message

    Example:
        ```python
        await update_resource(
            "my-api-client",
            "resource-uuid",
            uris=["/api/users/*", "/api/profiles/*"],
            scopes=["read", "write", "delete"]
        )
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    # Get current resource
    current = await client._make_request(
        "GET", f"/clients/{uuid}/authz/resource-server/resource/{resource_id}", realm=realm
    )

    # Update specified fields
    if name is not None:
        current["name"] = name
    if resource_type is not None:
        current["type"] = resource_type
    if uris is not None:
        current["uris"] = uris
    if scopes is not None:
        current["scopes"] = [{"name": s} if isinstance(s, str) else s for s in scopes]
    if icon_uri is not None:
        current["icon_uri"] = icon_uri
    if owner_managed_access is not None:
        current["ownerManagedAccess"] = owner_managed_access
    if display_name is not None:
        current["displayName"] = display_name
    if attributes is not None:
        current["attributes"] = attributes

    await client._make_request(
        "PUT",
        f"/clients/{uuid}/authz/resource-server/resource/{resource_id}",
        data=current,
        realm=realm,
    )

    return {
        "status": "updated",
        "resource_id": resource_id,
        "message": f"Resource '{resource_id}' updated successfully",
    }


@mcp.tool()
async def delete_resource(
    client_id: str,
    resource_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete an authorization resource.

    Warning: This will also delete all permissions associated with this resource.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        resource_id: Resource ID to delete
        realm: Target realm (uses default if not specified)

    Returns:
        Status message

    Example:
        ```python
        await delete_resource("my-api-client", "resource-uuid")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    await client._make_request(
        "DELETE", f"/clients/{uuid}/authz/resource-server/resource/{resource_id}", realm=realm
    )

    return {
        "status": "deleted",
        "resource_id": resource_id,
        "message": f"Resource '{resource_id}' deleted successfully",
    }


@mcp.tool()
async def get_resource_permissions(
    client_id: str,
    resource_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get permissions associated with a resource.

    Returns all permissions that reference this resource, helping you understand
    what policies are protecting it.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        resource_id: Resource ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of permissions that reference this resource

    Example:
        ```python
        permissions = await get_resource_permissions("my-api-client", "resource-uuid")
        for perm in permissions:
            print(f"Permission: {perm['name']}")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    return await client._make_request(
        "GET",
        f"/clients/{uuid}/authz/resource-server/resource/{resource_id}/permissions",
        realm=realm,
    )


@mcp.tool()
async def get_resource_scopes(
    client_id: str,
    resource_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get scopes associated with a resource.

    Convenience function to retrieve all scopes defined for a specific resource.

    Args:
        client_id: Client ID string (e.g., "my-app") or UUID
        resource_id: Resource ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of scopes for the resource

    Example:
        ```python
        scopes = await get_resource_scopes("my-api-client", "resource-uuid")
        print(f"Available actions: {[s['name'] for s in scopes]}")
        ```
    """
    uuid = await _get_client_uuid(client_id, realm)

    return await client._make_request(
        "GET",
        f"/clients/{uuid}/authz/resource-server/resource/{resource_id}/scopes",
        realm=realm,
    )
