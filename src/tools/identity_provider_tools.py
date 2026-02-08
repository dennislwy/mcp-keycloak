from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Identity Provider Management Tools


@mcp.tool()
async def list_identity_providers(
    brief_representation: bool = False,
    first: Optional[int] = None,
    max: Optional[int] = None,
    search: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all identity providers in the realm.

    Args:
        brief_representation: Return brief representations (default: False)
        first: Pagination offset
        max: Maximum results size
        search: Filter providers by name (supports prefix*, *contains*, "exact")
        realm: Target realm (uses default if not specified)

    Returns:
        List of identity provider objects
    """
    params = {}
    if brief_representation:
        params["briefRepresentation"] = "true"
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if search:
        params["search"] = search

    return await client._make_request(
        "GET", "/identity-provider/instances", params=params, realm=realm
    )


@mcp.tool()
async def get_identity_provider(
    alias: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific identity provider by alias.

    Args:
        alias: The identity provider's alias
        realm: Target realm (uses default if not specified)

    Returns:
        Identity provider object
    """
    return await client._make_request(
        "GET", f"/identity-provider/instances/{alias}", realm=realm
    )


@mcp.tool()
async def create_identity_provider(
    alias: str,
    provider_id: str,
    enabled: bool = True,
    display_name: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new identity provider.

    Args:
        alias: Unique alias for the identity provider
        provider_id: Provider type (e.g., "google", "facebook", "oidc", "saml")
        enabled: Whether the provider is enabled
        display_name: Display name for the provider
        config: Provider-specific configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    idp_data = {
        "alias": alias,
        "providerId": provider_id,
        "enabled": enabled,
    }

    if display_name:
        idp_data["displayName"] = display_name
    if config:
        idp_data["config"] = config

    await client._make_request(
        "POST", "/identity-provider/instances", data=idp_data, realm=realm
    )
    return {
        "status": "created",
        "message": f"Identity provider '{alias}' created successfully",
    }


@mcp.tool()
async def update_identity_provider(
    alias: str,
    enabled: Optional[bool] = None,
    display_name: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    trust_email: Optional[bool] = None,
    store_token: Optional[bool] = None,
    add_read_token_role_on_create: Optional[bool] = None,
    link_only: Optional[bool] = None,
    first_broker_login_flow_alias: Optional[str] = None,
    post_broker_login_flow_alias: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing identity provider.

    Args:
        alias: The identity provider's alias
        enabled: Whether the provider is enabled
        display_name: New display name
        config: Updated provider configuration
        trust_email: Trust email from identity provider
        store_token: Store tokens from identity provider
        add_read_token_role_on_create: Add read token role on create
        link_only: Link only (don't create new users)
        first_broker_login_flow_alias: First broker login flow
        post_broker_login_flow_alias: Post broker login flow
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current provider data
    current_idp = await client._make_request(
        "GET", f"/identity-provider/instances/{alias}", realm=realm
    )

    # Update only provided fields
    if enabled is not None:
        current_idp["enabled"] = enabled
    if display_name is not None:
        current_idp["displayName"] = display_name
    if config is not None:
        if "config" not in current_idp:
            current_idp["config"] = {}
        current_idp["config"].update(config)
    if trust_email is not None:
        current_idp["trustEmail"] = trust_email
    if store_token is not None:
        current_idp["storeToken"] = store_token
    if add_read_token_role_on_create is not None:
        current_idp["addReadTokenRoleOnCreate"] = add_read_token_role_on_create
    if link_only is not None:
        current_idp["linkOnly"] = link_only
    if first_broker_login_flow_alias is not None:
        current_idp["firstBrokerLoginFlowAlias"] = first_broker_login_flow_alias
    if post_broker_login_flow_alias is not None:
        current_idp["postBrokerLoginFlowAlias"] = post_broker_login_flow_alias

    await client._make_request(
        "PUT", f"/identity-provider/instances/{alias}", data=current_idp, realm=realm
    )
    return {
        "status": "updated",
        "message": f"Identity provider '{alias}' updated successfully",
    }


@mcp.tool()
async def delete_identity_provider(
    alias: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete an identity provider.

    Args:
        alias: The identity provider's alias
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/identity-provider/instances/{alias}", realm=realm
    )
    return {
        "status": "deleted",
        "message": f"Identity provider '{alias}' deleted successfully",
    }


@mcp.tool()
async def export_identity_provider(
    alias: str,
    format: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export public broker configuration for identity provider.

    Args:
        alias: The identity provider's alias
        format: Export format (if applicable)
        realm: Target realm (uses default if not specified)

    Returns:
        Exported configuration
    """
    params = {}
    if format:
        params["format"] = format

    return await client._make_request(
        "GET",
        f"/identity-provider/instances/{alias}/export",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def import_identity_provider_config(
    config: Dict[str, Any],
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Import identity provider configuration from JSON.

    Args:
        config: Identity provider configuration to import
        realm: Target realm (uses default if not specified)

    Returns:
        Import result
    """
    return await client._make_request(
        "POST", "/identity-provider/import-config", data=config, realm=realm
    )


# Identity Provider Mapper Management


@mcp.tool()
async def list_identity_provider_mappers(
    alias: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get mappers for an identity provider.

    Args:
        alias: The identity provider's alias
        realm: Target realm (uses default if not specified)

    Returns:
        List of mapper objects
    """
    return await client._make_request(
        "GET", f"/identity-provider/instances/{alias}/mappers", realm=realm
    )


@mcp.tool()
async def get_identity_provider_mapper(
    alias: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific identity provider mapper.

    Args:
        alias: The identity provider's alias
        mapper_id: The mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Mapper object
    """
    return await client._make_request(
        "GET", f"/identity-provider/instances/{alias}/mappers/{mapper_id}", realm=realm
    )


@mcp.tool()
async def create_identity_provider_mapper(
    alias: str,
    name: str,
    identity_provider_mapper: str,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a mapper for an identity provider.

    Args:
        alias: The identity provider's alias
        name: Mapper name
        identity_provider_mapper: Mapper type (e.g., "oidc-user-attribute-idp-mapper")
        config: Mapper configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    mapper_data = {
        "name": name,
        "identityProviderMapper": identity_provider_mapper,
        "identityProviderAlias": alias,
    }

    if config:
        mapper_data["config"] = config

    await client._make_request(
        "POST",
        f"/identity-provider/instances/{alias}/mappers",
        data=mapper_data,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Mapper '{name}' created for identity provider '{alias}'",
    }


@mcp.tool()
async def update_identity_provider_mapper(
    alias: str,
    mapper_id: str,
    name: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an identity provider mapper.

    Args:
        alias: The identity provider's alias
        mapper_id: The mapper's ID
        name: New mapper name
        config: Updated mapper configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current mapper data
    current_mapper = await client._make_request(
        "GET", f"/identity-provider/instances/{alias}/mappers/{mapper_id}", realm=realm
    )

    # Update only provided fields
    if name is not None:
        current_mapper["name"] = name
    if config is not None:
        if "config" not in current_mapper:
            current_mapper["config"] = {}
        current_mapper["config"].update(config)

    await client._make_request(
        "PUT",
        f"/identity-provider/instances/{alias}/mappers/{mapper_id}",
        data=current_mapper,
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Mapper {mapper_id} updated successfully",
    }


@mcp.tool()
async def delete_identity_provider_mapper(
    alias: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete an identity provider mapper.

    Args:
        alias: The identity provider's alias
        mapper_id: The mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/identity-provider/instances/{alias}/mappers/{mapper_id}",
        realm=realm,
    )
    return {
        "status": "deleted",
        "message": f"Mapper {mapper_id} deleted successfully",
    }


# User Federated Identity Management


@mcp.tool()
async def get_user_federated_identities(
    user_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get all federated identities for a user.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of federated identity objects
    """
    return await client._make_request(
        "GET", f"/users/{user_id}/federated-identity", realm=realm
    )


@mcp.tool()
async def add_user_federated_identity(
    user_id: str,
    provider: str,
    federated_identity_id: str,
    federated_username: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Link a user to an identity provider.

    Args:
        user_id: The user's ID
        provider: Identity provider alias
        federated_identity_id: Federated user ID
        federated_username: Federated username
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    identity_data = {
        "identityProvider": provider,
        "userId": federated_identity_id,
        "userName": federated_username,
    }

    await client._make_request(
        "POST",
        f"/users/{user_id}/federated-identity/{provider}",
        data=identity_data,
        realm=realm,
    )
    return {
        "status": "linked",
        "message": f"User {user_id} linked to identity provider '{provider}'",
    }


@mcp.tool()
async def remove_user_federated_identity(
    user_id: str,
    provider: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove federated identity link from a user.

    Args:
        user_id: The user's ID
        provider: Identity provider alias to unlink
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/users/{user_id}/federated-identity/{provider}", realm=realm
    )
    return {
        "status": "unlinked",
        "message": f"Identity provider '{provider}' unlinked from user {user_id}",
    }


# Convenience Functions for Common Identity Providers


@mcp.tool()
async def create_google_identity_provider(
    alias: str = "google",
    client_id: str = "",
    client_secret: str = "",
    default_scopes: str = "openid profile email",
    enabled: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a Google identity provider (convenience function).

    Args:
        alias: Provider alias (default: "google")
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        default_scopes: OAuth scopes to request
        enabled: Whether the provider is enabled
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "defaultScope": default_scopes,
    }

    return await create_identity_provider(
        alias=alias,
        provider_id="google",
        enabled=enabled,
        display_name="Google",
        config=config,
        realm=realm,
    )


@mcp.tool()
async def create_oidc_identity_provider(
    alias: str,
    client_id: str,
    client_secret: str,
    authorization_url: str,
    token_url: str,
    display_name: Optional[str] = None,
    user_info_url: Optional[str] = None,
    enabled: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create an OpenID Connect identity provider (convenience function).

    Args:
        alias: Provider alias
        client_id: OAuth client ID
        client_secret: OAuth client secret
        authorization_url: Authorization endpoint URL
        token_url: Token endpoint URL
        display_name: Display name for the provider
        user_info_url: UserInfo endpoint URL
        enabled: Whether the provider is enabled
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "authorizationUrl": authorization_url,
        "tokenUrl": token_url,
    }

    if user_info_url:
        config["userInfoUrl"] = user_info_url

    return await create_identity_provider(
        alias=alias,
        provider_id="oidc",
        enabled=enabled,
        display_name=display_name or alias,
        config=config,
        realm=realm,
    )
