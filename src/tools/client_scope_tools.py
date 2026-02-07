from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Client Scope Management Tools


@mcp.tool()
async def list_client_scopes(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get client scopes belonging to the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of client scope objects
    """
    return await client._make_request("GET", "/client-scopes", realm=realm)


@mcp.tool()
async def get_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get representation of a specific client scope.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Client scope object
    """
    return await client._make_request("GET", f"/client-scopes/{scope_id}", realm=realm)


@mcp.tool()
async def create_client_scope(
    name: str,
    description: Optional[str] = None,
    protocol: str = "openid-connect",
    attributes: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new client scope. Client scope's name must be unique!

    Args:
        name: Client scope name (must be unique)
        description: Client scope description
        protocol: Protocol (openid-connect or saml)
        attributes: Additional attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with created scope ID
    """
    scope_data = {
        "name": name,
        "protocol": protocol,
    }

    if description:
        scope_data["description"] = description
    if attributes:
        scope_data["attributes"] = attributes

    await client._make_request("POST", "/client-scopes", data=scope_data, realm=realm)
    return {
        "status": "created",
        "message": f"Client scope '{name}' created successfully",
    }


@mcp.tool()
async def update_client_scope(
    scope_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    protocol: Optional[str] = None,
    attributes: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a client scope.

    Args:
        scope_id: The client scope's ID
        name: New client scope name
        description: New description
        protocol: New protocol
        attributes: New attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current scope data
    current_scope = await client._make_request(
        "GET", f"/client-scopes/{scope_id}", realm=realm
    )

    # Update only provided fields
    if name is not None:
        current_scope["name"] = name
    if description is not None:
        current_scope["description"] = description
    if protocol is not None:
        current_scope["protocol"] = protocol
    if attributes is not None:
        current_scope["attributes"] = attributes

    await client._make_request(
        "PUT", f"/client-scopes/{scope_id}", data=current_scope, realm=realm
    )
    return {
        "status": "updated",
        "message": f"Client scope {scope_id} updated successfully",
    }


@mcp.tool()
async def delete_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete a client scope.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/client-scopes/{scope_id}", realm=realm)
    return {
        "status": "deleted",
        "message": f"Client scope {scope_id} deleted successfully",
    }


# Default Client Scopes Management


@mcp.tool()
async def get_realm_default_client_scopes(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get realm default client scopes. Only name and IDs are returned.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of default client scope objects
    """
    return await client._make_request(
        "GET", "/default-default-client-scopes", realm=realm
    )


@mcp.tool()
async def add_realm_default_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Set a client scope as a default client scope for the realm.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/default-default-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "added",
        "message": f"Client scope {scope_id} added as realm default",
    }


@mcp.tool()
async def remove_realm_default_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove a client scope from the default client scopes for the realm.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/default-default-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "removed",
        "message": f"Client scope {scope_id} removed from realm defaults",
    }


@mcp.tool()
async def get_realm_optional_client_scopes(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get realm optional client scopes. Only name and IDs are returned.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of optional client scope objects
    """
    return await client._make_request(
        "GET", "/default-optional-client-scopes", realm=realm
    )


@mcp.tool()
async def add_realm_optional_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Set a client scope as an optional client scope for the realm.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/default-optional-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "added",
        "message": f"Client scope {scope_id} added as realm optional",
    }


@mcp.tool()
async def remove_realm_optional_client_scope(
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove a client scope from the optional client scopes for the realm.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/default-optional-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "removed",
        "message": f"Client scope {scope_id} removed from realm optional",
    }


# Client-specific Scope Management


@mcp.tool()
async def get_client_default_scopes(
    client_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get default client scopes for a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        List of default client scope objects
    """
    return await client._make_request(
        "GET", f"/clients/{client_id}/default-client-scopes", realm=realm
    )


@mcp.tool()
async def add_client_default_scope(
    client_id: str,
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Add a default client scope to a client.

    Args:
        client_id: The client's database ID (not client_id)
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/clients/{client_id}/default-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "added",
        "message": f"Client scope {scope_id} added as default to client",
    }


@mcp.tool()
async def remove_client_default_scope(
    client_id: str,
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove a default client scope from a client.

    Args:
        client_id: The client's database ID (not client_id)
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/clients/{client_id}/default-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "removed",
        "message": f"Client scope {scope_id} removed from client defaults",
    }


@mcp.tool()
async def get_client_optional_scopes(
    client_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get optional client scopes for a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        List of optional client scope objects
    """
    return await client._make_request(
        "GET", f"/clients/{client_id}/optional-client-scopes", realm=realm
    )


@mcp.tool()
async def add_client_optional_scope(
    client_id: str,
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Add an optional client scope to a client.

    Args:
        client_id: The client's database ID (not client_id)
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/clients/{client_id}/optional-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "added",
        "message": f"Client scope {scope_id} added as optional to client",
    }


@mcp.tool()
async def remove_client_optional_scope(
    client_id: str,
    scope_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove an optional client scope from a client.

    Args:
        client_id: The client's database ID (not client_id)
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/clients/{client_id}/optional-client-scopes/{scope_id}", realm=realm
    )
    return {
        "status": "removed",
        "message": f"Client scope {scope_id} removed from client optional",
    }
