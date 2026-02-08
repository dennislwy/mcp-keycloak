from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Client Sessions Management


@mcp.tool()
async def get_client_sessions(
    client_id: str,
    first: Optional[int] = None,
    max: Optional[int] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get active user sessions for a client.

    Returns a list of active user sessions associated with the specified client.
    These are sessions where users are currently logged in to the client.

    Args:
        client_id: UUID of the client (not client_id field)
        first: Pagination offset (default: 0)
        max: Maximum results (default: 100)
        realm: Target realm (uses default if not specified)

    Returns:
        List of active user session objects
    """
    params = {}
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max

    return await client._make_request(
        "GET",
        f"/clients/{client_id}/user-sessions",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_client_offline_sessions(
    client_id: str,
    first: Optional[int] = None,
    max: Optional[int] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get offline sessions for a client.

    Returns a list of offline sessions associated with the client.
    Offline sessions allow users to maintain authentication state
    even when disconnected.

    Args:
        client_id: UUID of the client (not client_id field)
        first: Pagination offset (default: 0)
        max: Maximum results (default: 100)
        realm: Target realm (uses default if not specified)

    Returns:
        List of offline session objects
    """
    params = {}
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max

    return await client._make_request(
        "GET",
        f"/clients/{client_id}/offline-sessions",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_user_offline_sessions_for_client(
    user_id: str,
    client_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get offline sessions for a specific user and client.

    Returns offline sessions associated with a specific user and client combination.

    Args:
        user_id: ID of the user
        client_id: UUID of the client (not client_id field)
        realm: Target realm (uses default if not specified)

    Returns:
        List of user's offline sessions for the client
    """
    return await client._make_request(
        "GET",
        f"/users/{user_id}/offline-sessions/{client_id}",
        realm=realm,
    )


@mcp.tool()
async def revoke_user_consent_for_client(
    user_id: str,
    client_uuid: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Revoke user consent and offline tokens for a client.

    Revokes the user's consent for a specific client and removes
    all associated offline tokens. This effectively logs the user
    out of the client and requires re-authentication.

    Args:
        user_id: ID of the user
        client_uuid: Client ID (not UUID) to revoke consent for
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE",
        f"/users/{user_id}/consents/{client_uuid}",
        realm=realm,
    )

    return {
        "status": "revoked",
        "user_id": user_id,
        "client": client_uuid,
        "message": f"Consent revoked for user {user_id} on client {client_uuid}",
    }


# Session Statistics and Management


@mcp.tool()
async def get_client_session_count(
    client_id: str,
    realm: Optional[str] = None,
) -> Dict[str, int]:
    """
    Get session count statistics for a client.

    Returns the number of active and offline sessions for the specified client.

    Args:
        client_id: UUID of the client (not client_id field)
        realm: Target realm (uses default if not specified)

    Returns:
        Session count statistics
    """
    # Get active sessions
    active_sessions = await get_client_sessions(client_id, realm=realm)

    # Get offline sessions
    offline_sessions = await get_client_offline_sessions(client_id, realm=realm)

    return {
        "active_sessions": len(active_sessions),
        "offline_sessions": len(offline_sessions),
        "total_sessions": len(active_sessions) + len(offline_sessions),
        "client_id": client_id,
    }


@mcp.tool()
async def get_all_client_sessions_summary(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get session summary for all clients in the realm.

    Returns session statistics for all clients that have active sessions.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of client session summaries
    """
    # Get all clients first
    from . import client_tools

    clients = await client_tools.list_clients(realm=realm)

    summaries = []
    for client_info in clients:
        client_id = client_info["id"]
        client_name = client_info.get("clientId", "unknown")

        try:
            # Get session counts
            stats = await get_client_session_count(client_id, realm=realm)

            # Only include clients with sessions
            if stats["total_sessions"] > 0:
                summaries.append(
                    {
                        "client_uuid": client_id,
                        "client_id": client_name,
                        "client_name": client_info.get("name", client_name),
                        **stats,
                    }
                )
        except Exception:
            # Skip clients that don't support sessions or have errors
            continue

    return summaries


# Session Search and Filtering


@mcp.tool()
async def find_user_sessions_across_clients(
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Find all sessions for a user across all clients.

    Searches for active sessions for a specific user across all clients
    in the realm.

    Args:
        user_id: ID of the user
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary mapping client IDs to session lists
    """
    # Get all clients
    from . import client_tools

    clients = await client_tools.list_clients(realm=realm)

    user_sessions = {}

    for client_info in clients:
        client_id = client_info["id"]
        client_name = client_info.get("clientId", "unknown")

        try:
            # Get sessions for this client
            sessions = await get_client_sessions(client_id, realm=realm)

            # Filter sessions for the specific user
            user_client_sessions = [
                session for session in sessions if session.get("userId") == user_id
            ]

            if user_client_sessions:
                user_sessions[client_name] = user_client_sessions

        except Exception:
            # Skip clients that have errors
            continue

    return user_sessions


@mcp.tool()
async def find_sessions_by_ip(
    ip_address: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Find all sessions from a specific IP address.

    Searches for active sessions originating from a specific IP address
    across all clients in the realm.

    Args:
        ip_address: IP address to search for
        realm: Target realm (uses default if not specified)

    Returns:
        List of sessions from the specified IP address
    """
    # Get all clients
    from . import client_tools

    clients = await client_tools.list_clients(realm=realm)

    matching_sessions = []

    for client_info in clients:
        client_id = client_info["id"]
        client_name = client_info.get("clientId", "unknown")

        try:
            # Get sessions for this client
            sessions = await get_client_sessions(client_id, realm=realm)

            # Filter sessions by IP address
            ip_sessions = [
                {
                    **session,
                    "client_id": client_name,
                    "client_uuid": client_id,
                }
                for session in sessions
                if session.get("ipAddress") == ip_address
            ]

            matching_sessions.extend(ip_sessions)

        except Exception:
            # Skip clients that have errors
            continue

    return matching_sessions


# Convenience Functions


@mcp.tool()
async def get_active_session_statistics(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive session statistics for the realm.

    Returns detailed statistics about all active sessions in the realm,
    including breakdowns by client and overall totals.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive session statistics
    """
    client_summaries = await get_all_client_sessions_summary(realm=realm)

    total_active = sum(summary["active_sessions"] for summary in client_summaries)
    total_offline = sum(summary["offline_sessions"] for summary in client_summaries)

    # Get unique users count (approximate)
    all_sessions = []
    for summary in client_summaries:
        try:
            sessions = await get_client_sessions(summary["client_uuid"], realm=realm)
            all_sessions.extend(sessions)
        except Exception:
            continue

    unique_users = len(
        set(session.get("userId") for session in all_sessions if session.get("userId"))
    )

    return {
        "realm": realm or client.realm_name,
        "total_active_sessions": total_active,
        "total_offline_sessions": total_offline,
        "total_sessions": total_active + total_offline,
        "unique_active_users": unique_users,
        "clients_with_sessions": len(client_summaries),
        "client_breakdown": client_summaries,
    }


@mcp.tool()
async def cleanup_offline_sessions(
    client_id: str,
    older_than_days: int = 30,
    dry_run: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Clean up old offline sessions for a client.

    NOTE: This is a convenience function that identifies old offline sessions.
    Actual cleanup requires individual user consent revocation.

    Args:
        client_id: UUID of the client (not client_id field)
        older_than_days: Remove sessions older than this many days
        dry_run: If True, only report what would be cleaned (default: True)
        realm: Target realm (uses default if not specified)

    Returns:
        Cleanup report with sessions that would be/were removed
    """
    import datetime

    # Get offline sessions
    offline_sessions = await get_client_offline_sessions(client_id, realm=realm)

    # Calculate cutoff time
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(days=older_than_days)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

    # Find old sessions
    old_sessions = [
        session
        for session in offline_sessions
        if session.get("lastAccess", 0) < cutoff_timestamp
    ]

    result = {
        "client_id": client_id,
        "total_offline_sessions": len(offline_sessions),
        "old_sessions_found": len(old_sessions),
        "cutoff_date": cutoff_time.isoformat(),
        "dry_run": dry_run,
    }

    if dry_run:
        result["message"] = (
            f"Found {len(old_sessions)} offline sessions older than {older_than_days} days"
        )
        result["sessions_to_cleanup"] = old_sessions
    else:
        # Note: Actual cleanup would require iterating through sessions
        # and revoking user consent for each one
        result["message"] = (
            "Cleanup not implemented - use revoke_user_consent_for_client() for individual sessions"
        )

    return result
