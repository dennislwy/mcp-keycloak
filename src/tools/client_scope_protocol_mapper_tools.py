from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_client_scope_protocol_mappers(
    client_scope_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all protocol mappers for a client scope.

    Args:
        client_scope_id: The client scope's ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects
    """
    return await client._make_request(
        "GET", f"/client-scopes/{client_scope_id}/protocol-mappers/models", realm=realm
    )


@mcp.tool()
async def create_client_scope_protocol_mapper(
    client_scope_id: str,
    name: str,
    protocol: str,
    protocol_mapper: str,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a protocol mapper for a client scope.

    Args:
        client_scope_id: The client scope's ID
        name: Name of the protocol mapper
        protocol: Protocol (e.g., 'openid-connect', 'saml')
        protocol_mapper: Type of mapper (e.g., 'oidc-usermodel-attribute-mapper')
        config: Mapper configuration as key-value pairs
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    mapper_data = {
        "name": name,
        "protocol": protocol,
        "protocolMapper": protocol_mapper,
        "config": config or {},
    }

    await client._make_request(
        "POST",
        f"/client-scopes/{client_scope_id}/protocol-mappers/models",
        data=mapper_data,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"Protocol mapper {name} created for client scope {client_scope_id}",
    }


@mcp.tool()
async def get_client_scope_protocol_mapper(
    client_scope_id: str, mapper_id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific protocol mapper by ID for a client scope.

    Args:
        client_scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Protocol mapper object
    """
    return await client._make_request(
        "GET",
        f"/client-scopes/{client_scope_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )


@mcp.tool()
async def update_client_scope_protocol_mapper(
    client_scope_id: str,
    mapper_id: str,
    name: Optional[str] = None,
    protocol: Optional[str] = None,
    protocol_mapper: Optional[str] = None,
    config: Optional[Dict[str, str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing protocol mapper for a client scope.

    Args:
        client_scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        name: New name for the mapper
        protocol: New protocol
        protocol_mapper: New mapper type
        config: New configuration
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current mapper data
    current_mapper = await client._make_request(
        "GET",
        f"/client-scopes/{client_scope_id}/protocol-mappers/models/{mapper_id}",
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
        f"/client-scopes/{client_scope_id}/protocol-mappers/models/{mapper_id}",
        data=current_mapper,
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Protocol mapper {mapper_id} updated for client scope {client_scope_id}",
    }


@mcp.tool()
async def delete_client_scope_protocol_mapper(
    client_scope_id: str, mapper_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Delete a protocol mapper from a client scope.

    Args:
        client_scope_id: The client scope's ID
        mapper_id: The protocol mapper's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/client-scopes/{client_scope_id}/protocol-mappers/models/{mapper_id}",
        realm=realm,
    )
    return {
        "status": "deleted",
        "message": f"Protocol mapper {mapper_id} deleted from client scope {client_scope_id}",
    }


@mcp.tool()
async def create_client_scope_protocol_mappers_bulk(
    client_scope_id: str, mappers: List[Dict[str, Any]], realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Create multiple protocol mappers for a client scope at once.

    Args:
        client_scope_id: The client scope's ID
        mappers: List of protocol mapper objects (each with name, protocol, protocolMapper, config)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/client-scopes/{client_scope_id}/protocol-mappers/add-models",
        data=mappers,
        realm=realm,
    )
    return {
        "status": "created",
        "message": f"{len(mappers)} protocol mappers created for client scope {client_scope_id}",
    }


@mcp.tool()
async def get_client_scope_protocol_mappers_by_protocol(
    client_scope_id: str, protocol: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get protocol mappers for a client scope filtered by protocol type.

    Args:
        client_scope_id: The client scope's ID
        protocol: Protocol name (e.g., 'openid-connect', 'saml')
        realm: Target realm (uses default if not specified)

    Returns:
        List of protocol mapper objects for the specified protocol
    """
    return await client._make_request(
        "GET",
        f"/client-scopes/{client_scope_id}/protocol-mappers/protocol/{protocol}",
        realm=realm,
    )
