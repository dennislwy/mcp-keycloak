from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_client_scopes(realm: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all client scopes in the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of client scope objects
    """
    return await client._make_request("GET", "/client-scopes", realm=realm)


@mcp.tool()
async def create_client_scope(
    name: str,
    description: Optional[str] = None,
    protocol: str = "openid-connect",
    attributes: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new client scope.

    Args:
        name: Name of the client scope
        description: Description of the client scope
        protocol: Protocol (e.g., 'openid-connect', 'saml')
        attributes: Additional attributes as key-value pairs
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
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
    return {"status": "created", "message": f"Client scope {name} created successfully"}


@mcp.tool()
async def get_client_scope(
    client_scope_id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific client scope by ID.

    Args:
        client_scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Client scope object
    """
    return await client._make_request(
        "GET", f"/client-scopes/{client_scope_id}", realm=realm
    )


@mcp.tool()
async def update_client_scope(
    client_scope_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    protocol: Optional[str] = None,
    attributes: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing client scope.

    Args:
        client_scope_id: The client scope's ID
        name: New name
        description: New description
        protocol: New protocol
        attributes: New attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current scope data
    current_scope = await client._make_request(
        "GET", f"/client-scopes/{client_scope_id}", realm=realm
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
        "PUT", f"/client-scopes/{client_scope_id}", data=current_scope, realm=realm
    )
    return {
        "status": "updated",
        "message": f"Client scope {client_scope_id} updated successfully",
    }


@mcp.tool()
async def delete_client_scope(
    client_scope_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Delete a client scope.

    Args:
        client_scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/client-scopes/{client_scope_id}", realm=realm
    )
    return {
        "status": "deleted",
        "message": f"Client scope {client_scope_id} deleted successfully",
    }
