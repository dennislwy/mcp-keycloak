from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# User Federation/Storage Management via Components API


@mcp.tool()
async def list_components(
    name: Optional[str] = None,
    parent: Optional[str] = None,
    type: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all components in the realm.

    Args:
        name: Filter by component name
        parent: Filter by parent component ID
        type: Filter by component type (e.g., "org.keycloak.storage.UserStorageProvider")
        realm: Target realm (uses default if not specified)

    Returns:
        List of component objects
    """
    params = {}
    if name:
        params["name"] = name
    if parent:
        params["parent"] = parent
    if type:
        params["type"] = type

    return await client._make_request("GET", "/components", params=params, realm=realm)


@mcp.tool()
async def get_component(
    component_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific component by ID.

    Args:
        component_id: The component's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Component object
    """
    return await client._make_request("GET", f"/components/{component_id}", realm=realm)


@mcp.tool()
async def create_component(
    name: str,
    provider_id: str,
    provider_type: str,
    config: Optional[Dict[str, List[str]]] = None,
    parent_id: Optional[str] = None,
    sub_type: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new component (e.g., user storage provider).

    Args:
        name: Component name
        provider_id: Provider ID (e.g., "ldap", "kerberos")
        provider_type: Provider type (e.g., "org.keycloak.storage.UserStorageProvider")
        config: Component configuration (values must be lists)
        parent_id: Parent component ID (usually realm ID)
        sub_type: Component sub-type
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    component_data = {
        "name": name,
        "providerId": provider_id,
        "providerType": provider_type,
    }

    if config:
        component_data["config"] = config
    if parent_id:
        component_data["parentId"] = parent_id
    if sub_type:
        component_data["subType"] = sub_type

    await client._make_request("POST", "/components", data=component_data, realm=realm)
    return {
        "status": "created",
        "message": f"Component '{name}' created successfully",
    }


@mcp.tool()
async def update_component(
    component_id: str,
    name: Optional[str] = None,
    config: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing component.

    Args:
        component_id: The component's ID
        name: New component name
        config: Updated configuration (values must be lists)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current component data
    current_component = await client._make_request(
        "GET", f"/components/{component_id}", realm=realm
    )

    # Update only provided fields
    if name is not None:
        current_component["name"] = name
    if config is not None:
        if "config" not in current_component:
            current_component["config"] = {}
        current_component["config"].update(config)

    await client._make_request(
        "PUT", f"/components/{component_id}", data=current_component, realm=realm
    )
    return {
        "status": "updated",
        "message": f"Component {component_id} updated successfully",
    }


@mcp.tool()
async def delete_component(
    component_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete a component.

    Args:
        component_id: The component's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/components/{component_id}", realm=realm)
    return {
        "status": "deleted",
        "message": f"Component {component_id} deleted successfully",
    }


@mcp.tool()
async def get_component_sub_types(
    component_id: str,
    type: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get available sub-component types for a component.

    Args:
        component_id: The parent component's ID
        type: Filter by type
        realm: Target realm (uses default if not specified)

    Returns:
        List of available sub-component types
    """
    params = {}
    if type:
        params["type"] = type

    return await client._make_request(
        "GET",
        f"/components/{component_id}/sub-component-types",
        params=params,
        realm=realm,
    )


# User Storage Provider Management


@mcp.tool()
async def list_user_storage_providers(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all user storage providers in the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of user storage provider components
    """
    return await list_components(
        type="org.keycloak.storage.UserStorageProvider",
        realm=realm,
    )


@mcp.tool()
async def create_ldap_user_storage(
    name: str,
    connection_url: str,
    users_dn: str,
    bind_dn: Optional[str] = None,
    bind_credential: Optional[str] = None,
    vendor: str = "other",
    edit_mode: str = "READ_ONLY",
    sync_registrations: bool = False,
    import_enabled: bool = True,
    enabled: bool = True,
    priority: int = 0,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create an LDAP user storage provider (convenience function).

    Args:
        name: Provider name
        connection_url: LDAP connection URL (e.g., ldap://ldap.example.com:389)
        users_dn: Users DN (e.g., ou=users,dc=example,dc=com)
        bind_dn: Bind DN for connection
        bind_credential: Bind password
        vendor: LDAP vendor (ad, rhds, tivoli, edirectory, other)
        edit_mode: Edit mode (READ_ONLY, WRITABLE, UNSYNCED)
        sync_registrations: Sync new user registrations to LDAP
        import_enabled: Import users from LDAP
        enabled: Whether the provider is enabled
        priority: Provider priority (lower = higher priority)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "connectionUrl": [connection_url],
        "usersDn": [users_dn],
        "vendor": [vendor],
        "editMode": [edit_mode],
        "syncRegistrations": [str(sync_registrations).lower()],
        "importEnabled": [str(import_enabled).lower()],
        "enabled": [str(enabled).lower()],
        "priority": [str(priority)],
    }

    if bind_dn:
        config["bindDn"] = [bind_dn]
    if bind_credential:
        config["bindCredential"] = [bind_credential]

    return await create_component(
        name=name,
        provider_id="ldap",
        provider_type="org.keycloak.storage.UserStorageProvider",
        config=config,
        realm=realm,
    )


@mcp.tool()
async def create_kerberos_user_storage(
    name: str,
    kerberos_realm: str,
    server_principal: str,
    keytab: str,
    enabled: bool = True,
    priority: int = 0,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a Kerberos user storage provider (convenience function).

    Args:
        name: Provider name
        kerberos_realm: Kerberos realm
        server_principal: Server principal
        keytab: Keytab file location
        enabled: Whether the provider is enabled
        priority: Provider priority (lower = higher priority)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "kerberosRealm": [kerberos_realm],
        "serverPrincipal": [server_principal],
        "keyTab": [keytab],
        "enabled": [str(enabled).lower()],
        "priority": [str(priority)],
    }

    return await create_component(
        name=name,
        provider_id="kerberos",
        provider_type="org.keycloak.storage.UserStorageProvider",
        config=config,
        realm=realm,
    )


# User Credential Type Management


@mcp.tool()
async def get_user_storage_credential_types(
    user_id: str,
    realm: Optional[str] = None,
) -> List[str]:
    """
    Get credential types provided by user storage for a user.

    Returns credential types like "password", "otp", etc.
    Returns empty list for local users not backed by user storage.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of credential type strings
    """
    return await client._make_request(
        "GET", f"/users/{user_id}/configured-user-storage-credential-types", realm=realm
    )


# Component Configuration Helpers


@mcp.tool()
async def get_ldap_mappers(
    storage_provider_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get LDAP attribute mappers for a user storage provider.

    Args:
        storage_provider_id: The user storage provider's component ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of LDAP mapper components
    """
    return await list_components(
        parent=storage_provider_id,
        type="org.keycloak.storage.ldap.mappers.LDAPStorageMapper",
        realm=realm,
    )


@mcp.tool()
async def create_ldap_attribute_mapper(
    name: str,
    storage_provider_id: str,
    ldap_attribute: str,
    user_model_attribute: str,
    read_only: bool = True,
    always_read_value_from_ldap: bool = False,
    is_mandatory_in_ldap: bool = False,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create an LDAP attribute mapper.

    Args:
        name: Mapper name
        storage_provider_id: Parent user storage provider ID
        ldap_attribute: LDAP attribute name
        user_model_attribute: User model attribute name
        read_only: Whether the attribute is read-only
        always_read_value_from_ldap: Always read from LDAP
        is_mandatory_in_ldap: Whether the attribute is mandatory
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "ldap.attribute": [ldap_attribute],
        "user.model.attribute": [user_model_attribute],
        "read.only": [str(read_only).lower()],
        "always.read.value.from.ldap": [str(always_read_value_from_ldap).lower()],
        "is.mandatory.in.ldap": [str(is_mandatory_in_ldap).lower()],
    }

    return await create_component(
        name=name,
        provider_id="user-attribute-ldap-mapper",
        provider_type="org.keycloak.storage.ldap.mappers.LDAPStorageMapper",
        parent_id=storage_provider_id,
        config=config,
        realm=realm,
    )


@mcp.tool()
async def create_ldap_full_name_mapper(
    name: str,
    storage_provider_id: str,
    ldap_full_name_attribute: str = "cn",
    read_only: bool = True,
    write_only: bool = False,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create an LDAP full name mapper.

    Args:
        name: Mapper name
        storage_provider_id: Parent user storage provider ID
        ldap_full_name_attribute: LDAP attribute containing full name
        read_only: Whether the attribute is read-only
        write_only: Whether the attribute is write-only
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "ldap.full.name.attribute": [ldap_full_name_attribute],
        "read.only": [str(read_only).lower()],
        "write.only": [str(write_only).lower()],
    }

    return await create_component(
        name=name,
        provider_id="full-name-ldap-mapper",
        provider_type="org.keycloak.storage.ldap.mappers.LDAPStorageMapper",
        parent_id=storage_provider_id,
        config=config,
        realm=realm,
    )
