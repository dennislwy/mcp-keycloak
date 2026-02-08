from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Realm Import/Export Operations


@mcp.tool()
async def create_realm(
    realm_name: str,
    display_name: Optional[str] = None,
    enabled: bool = True,
    realm_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Create a new realm.

    Creates a new Keycloak realm with the specified configuration.
    This is equivalent to importing a realm from a JSON representation.

    Args:
        realm_name: Name of the new realm (must be unique)
        display_name: Human-readable display name for the realm
        enabled: Whether the realm should be enabled (default: True)
        realm_config: Additional realm configuration options

    Returns:
        Status message with realm creation details
    """
    # Build realm representation
    realm_data = {
        "realm": realm_name,
        "enabled": enabled,
    }

    if display_name:
        realm_data["displayName"] = display_name

    # Merge additional configuration
    if realm_config:
        realm_data.update(realm_config)

    await client._make_request("POST", "/", data=realm_data, skip_realm=True)

    return {
        "status": "created",
        "realm": realm_name,
        "message": f"Realm '{realm_name}' created successfully",
    }


@mcp.tool()
async def delete_realm(
    realm_name: str,
    confirm: bool = False,
) -> Dict[str, str]:
    """
    Delete an existing realm.

    WARNING: This permanently deletes the realm and all its data including
    users, clients, roles, and configurations. This action cannot be undone.

    Args:
        realm_name: Name of the realm to delete
        confirm: Must be True to confirm the destructive operation

    Returns:
        Status message
    """
    if not confirm:
        return {
            "status": "cancelled",
            "message": "Realm deletion cancelled. Set confirm=True to proceed with deletion.",
            "warning": "This operation permanently deletes ALL realm data and cannot be undone.",
        }

    await client._make_request("DELETE", "/", realm=realm_name)

    return {
        "status": "deleted",
        "realm": realm_name,
        "message": f"Realm '{realm_name}' deleted successfully",
    }


@mcp.tool()
async def import_realm(
    realm_data: Dict[str, Any],
    skip_if_exists: bool = False,
) -> Dict[str, str]:
    """
    Import a realm from JSON representation.

    Creates a new realm from a complete realm representation (JSON).
    The realm name in the data must be unique unless skip_if_exists is True.

    Args:
        realm_data: Complete realm representation as dictionary
        skip_if_exists: If True, skip import if realm already exists

    Returns:
        Status message with import details
    """
    realm_name = realm_data.get("realm", "unknown")

    try:
        await client._make_request("POST", "/", data=realm_data, skip_realm=True)

        return {
            "status": "imported",
            "realm": realm_name,
            "message": f"Realm '{realm_name}' imported successfully",
        }
    except Exception as e:
        error_msg = str(e).lower()
        if skip_if_exists and ("conflict" in error_msg or "exists" in error_msg):
            return {
                "status": "skipped",
                "realm": realm_name,
                "message": f"Realm '{realm_name}' already exists, skipped import",
            }
        raise


@mcp.tool()
async def export_realm(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export a realm configuration.

    Returns the complete realm representation including all configurations,
    but excluding users and client credentials for security.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Complete realm representation
    """
    return await client._make_request("GET", "/", realm=realm)


@mcp.tool()
async def partial_export_realm(
    export_clients: bool = True,
    export_groups_and_roles: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export selected parts of a realm configuration.

    Performs a partial export of the realm, allowing you to specify
    which components to include in the export.

    Args:
        export_clients: Include clients in the export
        export_groups_and_roles: Include groups and roles in the export
        realm: Target realm (uses default if not specified)

    Returns:
        Partial realm representation with selected components
    """
    params = {
        "exportClients": export_clients,
        "exportGroupsAndRoles": export_groups_and_roles,
    }

    return await client._make_request(
        "POST", "/partial-export", params=params, realm=realm
    )


@mcp.tool()
async def partial_import_realm(
    import_data: Dict[str, Any],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Import selected components into an existing realm.

    Performs a partial import into an existing realm. This allows you to
    import specific components (users, clients, roles, etc.) without
    replacing the entire realm configuration.

    Args:
        import_data: Partial realm data to import
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with import details
    """
    await client._make_request("POST", "/partialImport", data=import_data, realm=realm)

    return {
        "status": "imported",
        "message": "Partial import completed successfully",
        "realm": realm or client.realm_name,
    }


# Realm Management Operations


@mcp.tool()
async def list_realms(
    brief: bool = False,
) -> List[Dict[str, Any]]:
    """
    List all accessible realms.

    Returns a list of all realms that the current user has access to view.

    Args:
        brief: If True, returns only basic realm information

    Returns:
        List of realm representations
    """
    params = {"briefRepresentation": brief} if brief else {}

    return await client._make_request("GET", "/", params=params, skip_realm=True)


@mcp.tool()
async def duplicate_realm(
    source_realm: str,
    target_realm_name: str,
    include_users: bool = False,
) -> Dict[str, str]:
    """
    Duplicate an existing realm with a new name.

    Creates a copy of an existing realm with all its configurations,
    optionally including users.

    Args:
        source_realm: Name of the realm to copy
        target_realm_name: Name for the new realm copy
        include_users: Whether to copy users (default: False for security)

    Returns:
        Status message with duplication details
    """
    # Export source realm
    source_data = await export_realm(realm=source_realm)

    # Modify realm name and ID
    source_data["realm"] = target_realm_name
    source_data["id"] = target_realm_name
    if "displayName" in source_data:
        source_data["displayName"] = f"{source_data['displayName']} (Copy)"

    # Remove users if not requested (for security)
    if not include_users:
        source_data.pop("users", None)
        source_data.pop("federatedUsers", None)

    # Remove sensitive data that shouldn't be copied
    sensitive_keys = ["keycloakVersion", "adminPermissionsEnabled"]
    for key in sensitive_keys:
        source_data.pop(key, None)

    # Import as new realm
    await import_realm(source_data)

    return {
        "status": "duplicated",
        "source_realm": source_realm,
        "target_realm": target_realm_name,
        "message": f"Realm '{source_realm}' duplicated as '{target_realm_name}'",
        "included_users": include_users,
    }


# Convenience Functions


@mcp.tool()
async def backup_realm(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a complete backup of a realm.

    Exports the complete realm configuration for backup purposes.
    Use this before making significant changes to a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Complete realm backup data with metadata
    """
    import datetime

    backup_data = await export_realm(realm=realm)

    # Add backup metadata
    backup_info = {
        "backup_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "backup_realm": realm or client.realm_name,
        "backup_version": "1.0",
        "keycloak_version": backup_data.get("keycloakVersion", "unknown"),
    }

    return {
        "backup_info": backup_info,
        "realm_data": backup_data,
    }


@mcp.tool()
async def restore_realm_backup(
    backup_data: Dict[str, Any],
    target_realm_name: Optional[str] = None,
    overwrite_existing: bool = False,
) -> Dict[str, str]:
    """
    Restore a realm from backup data.

    Restores a realm from backup data created by backup_realm().
    Can optionally restore to a different realm name.

    Args:
        backup_data: Backup data from backup_realm()
        target_realm_name: New realm name (uses original if not specified)
        overwrite_existing: Whether to delete existing realm first

    Returns:
        Status message with restoration details
    """
    realm_data = backup_data.get("realm_data", backup_data)
    original_realm = realm_data.get("realm")

    # Use target name or keep original
    if target_realm_name:
        realm_data["realm"] = target_realm_name
        realm_data["id"] = target_realm_name

    final_realm_name = realm_data.get("realm", original_realm)

    # Handle existing realm
    if overwrite_existing:
        try:
            await delete_realm(final_realm_name, confirm=True)
        except Exception:
            # Ignore error if realm doesn't exist
            pass

    # Import realm
    await import_realm(realm_data, skip_if_exists=not overwrite_existing)

    backup_info = backup_data.get("backup_info", {})
    return {
        "status": "restored",
        "original_realm": original_realm,
        "restored_realm": final_realm_name,
        "backup_timestamp": backup_info.get("backup_timestamp", "unknown"),
        "message": f"Realm restored as '{final_realm_name}'",
    }
