from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_available_client_role_mappings(
    group_id: str, client_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List available client-level roles that can be mapped to a group.

    Args:
        group_id: The group's ID
        client_id: The client's database ID (not clientId)
        realm: Target realm (uses default if not specified)

    Returns:
        List of available client role objects
    """
    return await client._make_request(
        "GET",
        f"/groups/{group_id}/role-mappings/clients/{client_id}/available",
        realm=realm,
    )


@mcp.tool()
async def list_composite_client_role_mappings(
    group_id: str,
    client_id: str,
    brief_representation: bool = True,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List effective client-level role mappings for a group (includes composite roles).

    Args:
        group_id: The group's ID
        client_id: The client's database ID (not clientId)
        brief_representation: If false, return roles with their attributes
        realm: Target realm (uses default if not specified)

    Returns:
        List of effective client role objects (recursively includes composite roles)
    """
    params = {"briefRepresentation": str(brief_representation).lower()}
    return await client._make_request(
        "GET",
        f"/groups/{group_id}/role-mappings/clients/{client_id}/composite",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_client_role_mappings(
    group_id: str, client_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get client-level role mappings for a group.

    Args:
        group_id: The group's ID
        client_id: The client's database ID (not clientId)
        realm: Target realm (uses default if not specified)

    Returns:
        List of client role mappings
    """
    return await client._make_request(
        "GET", f"/groups/{group_id}/role-mappings/clients/{client_id}", realm=realm
    )


@mcp.tool()
async def add_client_role_mappings(
    group_id: str,
    client_id: str,
    roles: List[Dict[str, Any]],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Add client-level roles to a group's role mapping.

    Args:
        group_id: The group's ID
        client_id: The client's database ID (not clientId)
        roles: List of role objects to add (each with 'id' and 'name' fields)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/groups/{group_id}/role-mappings/clients/{client_id}",
        data=roles,
        realm=realm,
    )
    return {
        "status": "added",
        "message": f"{len(roles)} client roles added to group {group_id}",
    }


@mcp.tool()
async def delete_client_role_mappings(
    group_id: str,
    client_id: str,
    roles: List[Dict[str, Any]],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete client-level roles from a group's role mapping.

    Args:
        group_id: The group's ID
        client_id: The client's database ID (not clientId)
        roles: List of role objects to remove (each with 'id' and 'name' fields)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/groups/{group_id}/role-mappings/clients/{client_id}",
        data=roles,
        realm=realm,
    )
    return {
        "status": "deleted",
        "message": f"{len(roles)} client roles removed from group {group_id}",
    }
