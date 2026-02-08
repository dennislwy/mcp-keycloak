from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_groups(
    first: Optional[int] = None,
    max: Optional[int] = None,
    search: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all groups in the realm.

    Args:
        first: Pagination offset
        max: Maximum results size
        search: Search string
        realm: Target realm (uses default if not specified)

    Returns:
        List of groups
    """
    params = {}
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if search:
        params["search"] = search

    return await client._make_request("GET", "/groups", params=params, realm=realm)


@mcp.tool()
async def get_group(group_id: str, realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a specific group by ID.

    Args:
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        Group object
    """
    return await client._make_request("GET", f"/groups/{group_id}", realm=realm)


@mcp.tool()
async def create_group(
    name: str,
    path: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new group.

    Args:
        name: Group name
        path: Group path
        attributes: Group attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    group_data = {"name": name}

    if path:
        group_data["path"] = path
    if attributes:
        group_data["attributes"] = attributes

    await client._make_request("POST", "/groups", data=group_data, realm=realm)
    return {"status": "created", "message": f"Group {name} created successfully"}


@mcp.tool()
async def update_group(
    group_id: str,
    name: Optional[str] = None,
    path: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a group.

    Args:
        group_id: Group ID
        name: New group name
        path: New group path
        attributes: New group attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current group
    current_group = await client._make_request(
        "GET", f"/groups/{group_id}", realm=realm
    )

    # Update only provided fields
    if name is not None:
        current_group["name"] = name
    if path is not None:
        current_group["path"] = path
    if attributes is not None:
        current_group["attributes"] = attributes

    await client._make_request(
        "PUT", f"/groups/{group_id}", data=current_group, realm=realm
    )
    return {"status": "updated", "message": f"Group {group_id} updated successfully"}


@mcp.tool()
async def delete_group(group_id: str, realm: Optional[str] = None) -> Dict[str, str]:
    """
    Delete a group.

    Args:
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/groups/{group_id}", realm=realm)
    return {"status": "deleted", "message": f"Group {group_id} deleted successfully"}


@mcp.tool()
async def get_group_members(
    group_id: str,
    first: Optional[int] = None,
    max: Optional[int] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get members of a group.

    Args:
        group_id: Group ID
        first: Pagination offset
        max: Maximum results size
        realm: Target realm (uses default if not specified)

    Returns:
        List of group members
    """
    params = {}
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max

    return await client._make_request(
        "GET", f"/groups/{group_id}/members", params=params, realm=realm
    )


@mcp.tool()
async def add_user_to_group(
    user_id: str, group_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Add a user to a group.

    Args:
        user_id: User ID
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "PUT", f"/users/{user_id}/groups/{group_id}", realm=realm
    )
    return {"status": "added", "message": f"User {user_id} added to group {group_id}"}


@mcp.tool()
async def remove_user_from_group(
    user_id: str, group_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Remove a user from a group.

    Args:
        user_id: User ID
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/users/{user_id}/groups/{group_id}", realm=realm
    )
    return {
        "status": "removed",
        "message": f"User {user_id} removed from group {group_id}",
    }


@mcp.tool()
async def get_user_groups(
    user_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all groups for a user.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of groups the user belongs to
    """
    return await client._make_request("GET", f"/users/{user_id}/groups", realm=realm)


# Group Role Mappings


@mcp.tool()
async def get_group_role_mappings(
    group_id: str,
    brief: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get all role mappings for a group.

    Returns both realm roles and client roles that are assigned to the group.

    Args:
        group_id: Group ID
        brief: If False, return roles with their attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Role mappings object containing realm and client roles
    """
    params = {"briefRepresentation": brief}
    return await client._make_request(
        "GET", f"/groups/{group_id}/role-mappings", params=params, realm=realm
    )


@mcp.tool()
async def get_group_realm_roles(
    group_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get realm roles assigned to a group.

    Args:
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of realm roles assigned to the group
    """
    return await client._make_request(
        "GET", f"/groups/{group_id}/role-mappings/realm", realm=realm
    )


@mcp.tool()
async def add_realm_roles_to_group(
    group_id: str,
    role_names: List[str],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Assign realm roles to a group.

    Args:
        group_id: Group ID
        role_names: List of realm role names to assign
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get role representations by name
    from . import role_tools

    roles_data = []
    for role_name in role_names:
        role_data = await role_tools.get_realm_role(role_name, realm=realm)
        roles_data.append(role_data)

    await client._make_request(
        "POST", f"/groups/{group_id}/role-mappings/realm", data=roles_data, realm=realm
    )

    return {
        "status": "assigned",
        "group_id": group_id,
        "roles": role_names,
        "message": f"Assigned {len(role_names)} realm roles to group {group_id}",
    }


@mcp.tool()
async def remove_realm_roles_from_group(
    group_id: str,
    role_names: List[str],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove realm roles from a group.

    Args:
        group_id: Group ID
        role_names: List of realm role names to remove
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get role representations by name
    from . import role_tools

    roles_data = []
    for role_name in role_names:
        role_data = await role_tools.get_realm_role(role_name, realm=realm)
        roles_data.append(role_data)

    await client._make_request(
        "DELETE",
        f"/groups/{group_id}/role-mappings/realm",
        data=roles_data,
        realm=realm,
    )

    return {
        "status": "removed",
        "group_id": group_id,
        "roles": role_names,
        "message": f"Removed {len(role_names)} realm roles from group {group_id}",
    }


@mcp.tool()
async def get_group_available_realm_roles(
    group_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get realm roles that can be assigned to a group.

    Returns realm roles that are not currently assigned to the group.

    Args:
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of available realm roles
    """
    return await client._make_request(
        "GET", f"/groups/{group_id}/role-mappings/realm/available", realm=realm
    )


@mcp.tool()
async def get_group_effective_realm_roles(
    group_id: str,
    brief: bool = True,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get effective realm roles for a group (including composite roles).

    Returns all realm roles that are effectively assigned to the group,
    including roles that are part of composite roles.

    Args:
        group_id: Group ID
        brief: If False, return roles with their attributes
        realm: Target realm (uses default if not specified)

    Returns:
        List of effective realm roles
    """
    params = {"briefRepresentation": brief}
    return await client._make_request(
        "GET",
        f"/groups/{group_id}/role-mappings/realm/composite",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_group_client_roles(
    group_id: str,
    client_uuid: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get client roles assigned to a group.

    Args:
        group_id: Group ID
        client_uuid: Client UUID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        List of client roles assigned to the group
    """
    return await client._make_request(
        "GET", f"/groups/{group_id}/role-mappings/clients/{client_uuid}", realm=realm
    )


@mcp.tool()
async def add_client_roles_to_group(
    group_id: str,
    client_uuid: str,
    role_names: List[str],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Assign client roles to a group.

    Args:
        group_id: Group ID
        client_uuid: Client UUID (not client_id)
        role_names: List of client role names to assign
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get role representations by name
    from . import role_tools

    roles_data = []
    for role_name in role_names:
        role_data = await role_tools.get_client_role(
            client_uuid, role_name, realm=realm
        )
        roles_data.append(role_data)

    await client._make_request(
        "POST",
        f"/groups/{group_id}/role-mappings/clients/{client_uuid}",
        data=roles_data,
        realm=realm,
    )

    return {
        "status": "assigned",
        "group_id": group_id,
        "client_uuid": client_uuid,
        "roles": role_names,
        "message": f"Assigned {len(role_names)} client roles to group {group_id}",
    }


@mcp.tool()
async def remove_client_roles_from_group(
    group_id: str,
    client_uuid: str,
    role_names: List[str],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove client roles from a group.

    Args:
        group_id: Group ID
        client_uuid: Client UUID (not client_id)
        role_names: List of client role names to remove
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get role representations by name
    from . import role_tools

    roles_data = []
    for role_name in role_names:
        role_data = await role_tools.get_client_role(
            client_uuid, role_name, realm=realm
        )
        roles_data.append(role_data)

    await client._make_request(
        "DELETE",
        f"/groups/{group_id}/role-mappings/clients/{client_uuid}",
        data=roles_data,
        realm=realm,
    )

    return {
        "status": "removed",
        "group_id": group_id,
        "client_uuid": client_uuid,
        "roles": role_names,
        "message": f"Removed {len(role_names)} client roles from group {group_id}",
    }


@mcp.tool()
async def get_group_available_client_roles(
    group_id: str,
    client_uuid: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get client roles that can be assigned to a group.

    Returns client roles that are not currently assigned to the group.

    Args:
        group_id: Group ID
        client_uuid: Client UUID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        List of available client roles
    """
    return await client._make_request(
        "GET",
        f"/groups/{group_id}/role-mappings/clients/{client_uuid}/available",
        realm=realm,
    )


@mcp.tool()
async def get_group_effective_client_roles(
    group_id: str,
    client_uuid: str,
    brief: bool = True,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get effective client roles for a group (including composite roles).

    Returns all client roles that are effectively assigned to the group,
    including roles that are part of composite roles.

    Args:
        group_id: Group ID
        client_uuid: Client UUID (not client_id)
        brief: If False, return roles with their attributes
        realm: Target realm (uses default if not specified)

    Returns:
        List of effective client roles
    """
    params = {"briefRepresentation": brief}
    return await client._make_request(
        "GET",
        f"/groups/{group_id}/role-mappings/clients/{client_uuid}/composite",
        params=params,
        realm=realm,
    )


# Convenience Functions


@mcp.tool()
async def get_group_all_roles(
    group_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get all roles (realm and client) assigned to a group.

    Convenience function that returns a comprehensive view of all
    roles assigned to the group across all clients.

    Args:
        group_id: Group ID
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary with realm roles and client roles
    """
    # Get all role mappings
    mappings = await get_group_role_mappings(group_id, brief=False, realm=realm)

    # Get realm roles
    realm_roles = mappings.get("realmMappings", [])

    # Get client roles
    client_mappings = mappings.get("clientMappings", {})

    result = {
        "group_id": group_id,
        "realm_roles": realm_roles,
        "client_roles": {},
        "total_roles": len(realm_roles),
    }

    # Process client roles
    for client_id, client_data in client_mappings.items():
        client_roles = client_data.get("mappings", [])
        result["client_roles"][client_id] = client_roles
        result["total_roles"] += len(client_roles)

    return result


@mcp.tool()
async def copy_group_roles(
    source_group_id: str,
    target_group_id: str,
    include_client_roles: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Copy all role assignments from one group to another.

    Copies realm roles and optionally client roles from the source
    group to the target group.

    Args:
        source_group_id: ID of the group to copy roles from
        target_group_id: ID of the group to copy roles to
        include_client_roles: Whether to copy client roles (default: True)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with copy details
    """
    # Get all roles from source group
    source_roles = await get_group_all_roles(source_group_id, realm=realm)

    copied_roles = 0

    # Copy realm roles
    if source_roles["realm_roles"]:
        realm_role_names = [role["name"] for role in source_roles["realm_roles"]]
        await add_realm_roles_to_group(target_group_id, realm_role_names, realm=realm)
        copied_roles += len(realm_role_names)

    # Copy client roles
    if include_client_roles:
        for client_id, client_roles in source_roles["client_roles"].items():
            if client_roles:
                client_role_names = [role["name"] for role in client_roles]
                await add_client_roles_to_group(
                    target_group_id, client_id, client_role_names, realm=realm
                )
                copied_roles += len(client_role_names)

    return {
        "status": "copied",
        "source_group": source_group_id,
        "target_group": target_group_id,
        "copied_roles": copied_roles,
        "message": f"Copied {copied_roles} roles from group {source_group_id} to {target_group_id}",
    }
