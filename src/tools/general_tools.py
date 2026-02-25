from typing import Dict, Any
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """
    Get general information about the Keycloak server.

    Returns server-wide information including system info, memory info,
    profile info, themes, providers, protocols, and other server metadata.
    This is a special endpoint that operates at the server level, not realm level.

    Returns:
        Server information containing:
        - systemInfo: System information (version, uptime, serverTime, etc.)
        - memoryInfo: Memory usage information (total, used, free memory)
        - profileInfo: Active profile information
        - themes: Available themes (login, account, admin, email)
        - providers: Registered provider information
        - protocolMapperTypes: Available protocol mapper types
        - builtinProtocolMappers: Built-in protocol mappers
        - clientInstallations: Available client installation configurations
        - componentTypes: Available component types
        - passwordPolicies: Available password policies
        - enums: Enumeration types used in the system
        - cryptoInfo: Cryptographic provider information
        - identityProviders: Available identity provider implementations
        - clientImporters: Available client importers
        - socialProviders: Available social providers

    Example:
        # Get comprehensive server information
        server_info = get_server_info()
        print(f"Keycloak Version: {server_info['systemInfo']['version']}")
        print(f"Server Time: {server_info['systemInfo']['serverTime']}")
        print(f"Available Themes: {list(server_info['themes'].keys())}")
    """
    # ServerInfo endpoint is at /admin/serverinfo (no realm in path)
    return await client._make_request("GET", "/serverinfo", skip_realm=True)
