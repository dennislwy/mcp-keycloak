from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Protocol Mapper Management for Client Scopes


@mcp.tool()
async def list_client_scope_protocol_mappers(
    scope_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get protocol mappers for a client scope.

    Args:
        scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects
    """
    return await client._make_request(
        "GET", f"/client-scopes/{scope_id}/protocol-mappers/models", realm=realm
    )


@mcp.tool()
async def get_client_scope_protocol_mapper(
    scope_id: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific protocol mapper by ID for a client scope.

    Args:
        scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Protocol mapper object
    """
    return await client._make_request(
        "GET",
        f"/client-scopes/{scope_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )


@mcp.tool()
async def create_client_scope_protocol_mapper(
    scope_id: str,
    name: str,
    protocol: str = "openid-connect",
    protocol_mapper: str = "oidc-usermodel-attribute-mapper",
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a protocol mapper for a client scope.

    Args:
        scope_id: The client scope's ID
        name: Mapper name
        protocol: Protocol (openid-connect or saml)
        protocol_mapper: Type of mapper (e.g., oidc-usermodel-attribute-mapper, oidc-role-mapper)
        config: Mapper configuration (e.g., {"user.attribute": "email", "claim.name": "email"})
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    mapper_data = {
        "name": name,
        "protocol": protocol,
        "protocolMapper": protocol_mapper,
    }

    if config:
        mapper_data["config"] = config

    await client._make_request(
        "POST",
        f"/client-scopes/{scope_id}/protocol-mappers/models",
        data=mapper_data,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Protocol mapper '{name}' created successfully",
    }


@mcp.tool()
async def update_client_scope_protocol_mapper(
    scope_id: str,
    mapper_id: str,
    name: Optional[str] = None,
    protocol: Optional[str] = None,
    protocol_mapper: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a protocol mapper for a client scope.

    Args:
        scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        name: New mapper name
        protocol: New protocol
        protocol_mapper: New mapper type
        config: New mapper configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current mapper data
    current_mapper = await client._make_request(
        "GET",
        f"/client-scopes/{scope_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )

    # Update only provided fields
    if name is not None:
        current_mapper["name"] = name
    if protocol is not None:
        current_mapper["protocol"] = protocol
    if protocol_mapper is not None:
        current_mapper["protocolMapper"] = protocol_mapper
    if config is not None:
        current_mapper["config"] = config

    await client._make_request(
        "PUT",
        f"/client-scopes/{scope_id}/protocol-mappers/models/{mapper_id}",
        data=current_mapper,
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Protocol mapper {mapper_id} updated successfully",
    }


@mcp.tool()
async def delete_client_scope_protocol_mapper(
    scope_id: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete a protocol mapper from a client scope.

    Args:
        scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/client-scopes/{scope_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )
    return {
        "status": "deleted",
        "message": f"Protocol mapper {mapper_id} deleted successfully",
    }


@mcp.tool()
async def add_client_scope_protocol_mappers(
    scope_id: str,
    mappers: List[Dict[str, Any]],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create multiple protocol mappers for a client scope at once.

    Args:
        scope_id: The client scope's ID
        mappers: List of mapper configurations
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/client-scopes/{scope_id}/protocol-mappers/add-models",
        data=mappers,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Added {len(mappers)} protocol mappers successfully",
    }


@mcp.tool()
async def get_client_scope_mappers_by_protocol(
    scope_id: str,
    protocol: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get protocol mappers for a client scope filtered by protocol.

    Args:
        scope_id: The client scope's ID
        protocol: Protocol name (openid-connect or saml)
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects
    """
    return await client._make_request(
        "GET",
        f"/client-scopes/{scope_id}/protocol-mappers/protocol/{protocol}",
        realm=realm,
    )


# Protocol Mapper Management for Clients


@mcp.tool()
async def list_client_protocol_mappers(
    client_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get protocol mappers for a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects
    """
    return await client._make_request(
        "GET", f"/clients/{client_id}/protocol-mappers/models", realm=realm
    )


@mcp.tool()
async def get_client_protocol_mapper(
    client_id: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific protocol mapper by ID for a client.

    Args:
        client_id: The client's database ID (not client_id)
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Protocol mapper object
    """
    return await client._make_request(
        "GET", f"/clients/{client_id}/protocol-mappers/models/{mapper_id}", realm=realm
    )


@mcp.tool()
async def create_client_protocol_mapper(
    client_id: str,
    name: str,
    protocol: str = "openid-connect",
    protocol_mapper: str = "oidc-usermodel-attribute-mapper",
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a protocol mapper for a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        name: Mapper name
        protocol: Protocol (openid-connect or saml)
        protocol_mapper: Type of mapper (e.g., oidc-usermodel-attribute-mapper, oidc-role-mapper)
        config: Mapper configuration (e.g., {"user.attribute": "email", "claim.name": "email"})
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    mapper_data = {
        "name": name,
        "protocol": protocol,
        "protocolMapper": protocol_mapper,
    }

    if config:
        mapper_data["config"] = config

    await client._make_request(
        "POST",
        f"/clients/{client_id}/protocol-mappers/models",
        data=mapper_data,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Protocol mapper '{name}' created for client",
    }


@mcp.tool()
async def update_client_protocol_mapper(
    client_id: str,
    mapper_id: str,
    name: Optional[str] = None,
    protocol: Optional[str] = None,
    protocol_mapper: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a protocol mapper for a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        mapper_id: The protocol mapper's ID
        name: New mapper name
        protocol: New protocol
        protocol_mapper: New mapper type
        config: New mapper configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current mapper data
    current_mapper = await client._make_request(
        "GET", f"/clients/{client_id}/protocol-mappers/models/{mapper_id}", realm=realm
    )

    # Update only provided fields
    if name is not None:
        current_mapper["name"] = name
    if protocol is not None:
        current_mapper["protocol"] = protocol
    if protocol_mapper is not None:
        current_mapper["protocolMapper"] = protocol_mapper
    if config is not None:
        current_mapper["config"] = config

    await client._make_request(
        "PUT",
        f"/clients/{client_id}/protocol-mappers/models/{mapper_id}",
        data=current_mapper,
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Client protocol mapper {mapper_id} updated successfully",
    }


@mcp.tool()
async def delete_client_protocol_mapper(
    client_id: str,
    mapper_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete a protocol mapper from a specific client.

    Args:
        client_id: The client's database ID (not client_id)
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/clients/{client_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )
    return {
        "status": "deleted",
        "message": f"Client protocol mapper {mapper_id} deleted successfully",
    }


@mcp.tool()
async def add_client_protocol_mappers(
    client_id: str,
    mappers: List[Dict[str, Any]],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create multiple protocol mappers for a client at once.

    Args:
        client_id: The client's database ID (not client_id)
        mappers: List of mapper configurations
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/clients/{client_id}/protocol-mappers/add-models",
        data=mappers,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Added {len(mappers)} protocol mappers to client",
    }


@mcp.tool()
async def get_client_mappers_by_protocol(
    client_id: str,
    protocol: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get protocol mappers for a client filtered by protocol.

    Args:
        client_id: The client's database ID (not client_id)
        protocol: Protocol name (openid-connect or saml)
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects
    """
    return await client._make_request(
        "GET", f"/clients/{client_id}/protocol-mappers/protocol/{protocol}", realm=realm
    )


@mcp.tool()
async def evaluate_client_scope_mappers(
    client_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get all effective protocol mappers for token generation.

    This includes mappers from both the client and its associated client scopes.

    Args:
        client_id: The client's database ID (not client_id)
        scope: Scope parameter for evaluation
        realm: Target realm (uses default if not specified)

    Returns:
        List of effective protocol mapper objects
    """
    params = {}
    if scope:
        params["scope"] = scope

    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/protocol-mappers",
        params=params,
        realm=realm,
    )


# Common Protocol Mapper Templates


@mcp.tool()
async def create_user_attribute_mapper(
    target_id: str,
    target_type: str,
    attribute_name: str,
    claim_name: str,
    claim_type: str = "String",
    add_to_id_token: bool = True,
    add_to_access_token: bool = True,
    add_to_userinfo: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a user attribute protocol mapper (convenience function).

    Args:
        target_id: Client ID or Client Scope ID
        target_type: Either "client" or "client-scope"
        attribute_name: User attribute to map
        claim_name: Name of the claim in token
        claim_type: JSON type of claim (String, long, int, boolean, JSON)
        add_to_id_token: Include in ID token
        add_to_access_token: Include in access token
        add_to_userinfo: Include in userinfo endpoint response
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "user.attribute": attribute_name,
        "claim.name": claim_name,
        "jsonType.label": claim_type,
        "id.token.claim": str(add_to_id_token).lower(),
        "access.token.claim": str(add_to_access_token).lower(),
        "userinfo.token.claim": str(add_to_userinfo).lower(),
    }

    mapper_data = {
        "name": f"{attribute_name}-mapper",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-attribute-mapper",
        "config": config,
    }

    if target_type == "client":
        endpoint = f"/clients/{target_id}/protocol-mappers/models"
    else:
        endpoint = f"/client-scopes/{target_id}/protocol-mappers/models"

    await client._make_request("POST", endpoint, data=mapper_data, realm=realm)
    return {
        "status": "created",
        "message": f"User attribute mapper for '{attribute_name}' created",
    }


@mcp.tool()
async def create_role_mapper(
    target_id: str,
    target_type: str,
    claim_name: str = "roles",
    add_to_id_token: bool = True,
    add_to_access_token: bool = True,
    add_to_userinfo: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a realm role protocol mapper (convenience function).

    Args:
        target_id: Client ID or Client Scope ID
        target_type: Either "client" or "client-scope"
        claim_name: Name of the claim for roles
        add_to_id_token: Include in ID token
        add_to_access_token: Include in access token
        add_to_userinfo: Include in userinfo endpoint response
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "claim.name": claim_name,
        "id.token.claim": str(add_to_id_token).lower(),
        "access.token.claim": str(add_to_access_token).lower(),
        "userinfo.token.claim": str(add_to_userinfo).lower(),
        "multivalued": "true",
    }

    mapper_data = {
        "name": f"{claim_name}-realm-role-mapper",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-realm-role-mapper",
        "config": config,
    }

    if target_type == "client":
        endpoint = f"/clients/{target_id}/protocol-mappers/models"
    else:
        endpoint = f"/client-scopes/{target_id}/protocol-mappers/models"

    await client._make_request("POST", endpoint, data=mapper_data, realm=realm)
    return {
        "status": "created",
        "message": f"Role mapper with claim '{claim_name}' created",
    }


@mcp.tool()
async def create_audience_mapper(
    target_id: str,
    target_type: str,
    included_client_audience: str,
    add_to_id_token: bool = False,
    add_to_access_token: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create an audience protocol mapper (convenience function).

    Args:
        target_id: Client ID or Client Scope ID
        target_type: Either "client" or "client-scope"
        included_client_audience: Client ID to include as audience
        add_to_id_token: Include in ID token
        add_to_access_token: Include in access token
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    config = {
        "included.client.audience": included_client_audience,
        "id.token.claim": str(add_to_id_token).lower(),
        "access.token.claim": str(add_to_access_token).lower(),
    }

    mapper_data = {
        "name": f"audience-{included_client_audience}",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "config": config,
    }

    if target_type == "client":
        endpoint = f"/clients/{target_id}/protocol-mappers/models"
    else:
        endpoint = f"/client-scopes/{target_id}/protocol-mappers/models"

    await client._make_request("POST", endpoint, data=mapper_data, realm=realm)
    return {
        "status": "created",
        "message": f"Audience mapper for '{included_client_audience}' created",
    }
