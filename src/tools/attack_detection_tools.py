from typing import Dict, Any, Optional
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def get_user_brute_force_status(
    user_id: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the brute force detection status for a specific user.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing brute force status information such as:
        - numFailures: Number of failed login attempts
        - disabled: Whether the user is temporarily disabled
        - lastIPFailure: Last IP address that had a failed login
        - lastFailure: Timestamp of last failure
    """
    return await client._make_request(
        "GET", f"/attack-detection/brute-force/users/{user_id}", realm=realm
    )


@mcp.tool()
async def clear_user_login_failures(
    user_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Clear any login failures for a specific user.
    This can release a temporarily disabled user who was locked out due to brute force detection.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/attack-detection/brute-force/users/{user_id}", realm=realm
    )
    return {
        "status": "cleared",
        "message": f"Login failures cleared for user {user_id}",
    }


@mcp.tool()
async def clear_all_login_failures(realm: Optional[str] = None) -> Dict[str, str]:
    """
    Clear login failures for all users in the realm.
    This can release all temporarily disabled users who were locked out due to brute force detection.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", "/attack-detection/brute-force/users", realm=realm
    )
    return {
        "status": "cleared",
        "message": "Login failures cleared for all users",
    }
