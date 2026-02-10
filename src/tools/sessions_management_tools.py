from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Realm-wide Session Management


@mcp.tool()
async def get_realm_session_stats(
    realm: Optional[str] = None,
) -> Dict[str, int]:
    """
    Get client session statistics for the entire realm.

    Returns a map where keys are client IDs and values are the number
    of active sessions for each client. Only clients with active sessions
    are included in the response.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Map of client IDs to active session counts
    """
    result = await client._make_request("GET", "/client-session-stats", realm=realm)

    # Handle different API response formats
    if isinstance(result, list):
        # Convert list format to dictionary format
        stats = {}
        for client_info in result:
            client_id = client_info.get("clientId", client_info.get("id", "unknown"))
            active_sessions = int(client_info.get("active", 0))
            if active_sessions > 0:
                stats[client_id] = active_sessions
        return stats
    elif isinstance(result, dict):
        # Already in dictionary format
        return result
    else:
        # Fallback to empty dict
        return {}


@mcp.tool()
async def get_user_session_details(
    user_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get all active sessions for a specific user.

    Returns a list of active user sessions including session details
    such as IP address, start time, last access, and associated clients.

    Args:
        user_id: ID of the user
        realm: Target realm (uses default if not specified)

    Returns:
        List of user session objects
    """
    return await client._make_request("GET", f"/users/{user_id}/sessions", realm=realm)


@mcp.tool()
async def logout_user_sessions(
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Log out a specific user by invalidating all their active sessions.

    Revokes all user sessions across all clients and sends notifications
    to clients to invalidate their sessions.

    Args:
        user_id: ID of the user to log out
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("POST", f"/users/{user_id}/logout", realm=realm)

    return {
        "status": "logged_out",
        "user_id": user_id,
        "message": f"All sessions for user {user_id} have been invalidated",
    }


@mcp.tool()
async def logout_all_users(
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Log out all users in the realm by invalidating all active sessions.

    Removes all user sessions for the realm and instructs all clients
    with admin URLs to invalidate their sessions. This is a realm-wide
    logout operation.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with logout results
    """
    result = await client._make_request("POST", "/logout-all", realm=realm)

    return {
        "status": "logged_out_all",
        "realm": realm or client.realm_name,
        "message": "All user sessions in the realm have been invalidated",
        "result": result,
    }


# Session Analytics and Monitoring


@mcp.tool()
async def get_realm_sessions_summary(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive session summary for the realm.

    Provides detailed statistics about active sessions including total
    session counts, unique users, and per-client session distribution.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive session summary with statistics
    """
    # Get client session stats
    client_stats = await get_realm_session_stats(realm=realm)

    total_sessions = sum(client_stats.values())
    active_clients = len(client_stats)

    return {
        "realm": realm or client.realm_name,
        "total_active_sessions": total_sessions,
        "active_clients_with_sessions": active_clients,
        "client_session_breakdown": client_stats,
        "average_sessions_per_client": (
            round(total_sessions / active_clients, 2) if active_clients > 0 else 0
        ),
        "session_distribution": {
            "clients_with_sessions": active_clients,
            "total_sessions": total_sessions,
        },
    }


@mcp.tool()
async def find_user_sessions(
    username: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Find user sessions based on search criteria.

    Search for active user sessions by username, user ID, or IP address.
    At least one search criterion must be provided.

    Args:
        username: Username to search for (optional)
        user_id: User ID to search for (optional)
        ip_address: IP address to filter sessions (optional)
        realm: Target realm (uses default if not specified)

    Returns:
        List of matching user sessions
    """
    if not any([username, user_id, ip_address]):
        raise ValueError("At least one search criterion must be provided")

    matching_sessions = []

    if user_id:
        # Direct user ID lookup
        sessions = await get_user_session_details(user_id, realm=realm)
        if ip_address:
            # Filter by IP address
            sessions = [s for s in sessions if s.get("ipAddress") == ip_address]
        matching_sessions.extend(sessions)
    else:
        # Need to search through users - this is a more expensive operation
        from . import user_tools

        # Get users matching the criteria
        search_criteria = {}
        if username:
            search_criteria["username"] = username

        users = await user_tools.list_users(
            search=username if username else None,
            max=100,  # Limit to prevent excessive API calls
            realm=realm,
        )

        for user in users:
            try:
                user_sessions = await get_user_session_details(user["id"], realm=realm)

                # Filter by IP address if specified
                if ip_address:
                    user_sessions = [
                        s for s in user_sessions if s.get("ipAddress") == ip_address
                    ]

                # Add user info to sessions
                for session in user_sessions:
                    session["user_details"] = {
                        "id": user["id"],
                        "username": user.get("username"),
                        "email": user.get("email"),
                    }

                matching_sessions.extend(user_sessions)
            except Exception:
                # Skip users that cause errors
                continue

    return matching_sessions


@mcp.tool()
async def get_sessions_by_client(
    client_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get session information for a specific client.

    Returns detailed session information for the specified client including
    active session count and user session details.

    Args:
        client_id: Client ID to get sessions for
        realm: Target realm (uses default if not specified)

    Returns:
        Client session information and statistics
    """
    # Get realm session stats
    realm_stats = await get_realm_session_stats(realm=realm)

    client_session_count = realm_stats.get(client_id, 0)

    return {
        "client_id": client_id,
        "active_sessions": client_session_count,
        "realm": realm or client.realm_name,
        "session_percentage": (
            round((client_session_count / sum(realm_stats.values())) * 100, 2)
            if realm_stats and sum(realm_stats.values()) > 0
            else 0
        ),
        "realm_total_sessions": sum(realm_stats.values()),
    }


# Session Configuration Management


@mcp.tool()
async def get_session_configuration(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get current session timeout and configuration settings for the realm.

    Returns session-related configuration including timeouts, lifespans,
    and SSO settings.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Session configuration settings
    """
    # Get full realm configuration
    from . import realm_tools

    realm_config = await realm_tools.get_realm_info(realm=realm)

    # Extract session-related configuration
    session_config = {
        "realm": realm_config.get("realm"),
        "access_token_lifespan": realm_config.get("accessTokenLifespan"),
        "access_token_lifespan_implicit": realm_config.get(
            "accessTokenLifespanForImplicitFlow"
        ),
        "sso_session_idle_timeout": realm_config.get("ssoSessionIdleTimeout"),
        "sso_session_max_lifespan": realm_config.get("ssoSessionMaxLifespan"),
        "sso_session_idle_timeout_remember_me": realm_config.get(
            "ssoSessionIdleTimeoutRememberMe"
        ),
        "sso_session_max_lifespan_remember_me": realm_config.get(
            "ssoSessionMaxLifespanRememberMe"
        ),
        "offline_session_idle_timeout": realm_config.get("offlineSessionIdleTimeout"),
        "offline_session_max_lifespan_enabled": realm_config.get(
            "offlineSessionMaxLifespanEnabled"
        ),
        "offline_session_max_lifespan": realm_config.get("offlineSessionMaxLifespan"),
        "client_session_idle_timeout": realm_config.get("clientSessionIdleTimeout"),
        "client_session_max_lifespan": realm_config.get("clientSessionMaxLifespan"),
        "client_offline_session_idle_timeout": realm_config.get(
            "clientOfflineSessionIdleTimeout"
        ),
        "client_offline_session_max_lifespan": realm_config.get(
            "clientOfflineSessionMaxLifespan"
        ),
        "remember_me": realm_config.get("rememberMe"),
    }

    # Remove None values
    session_config = {k: v for k, v in session_config.items() if v is not None}

    return session_config


@mcp.tool()
async def update_session_configuration(
    sso_session_idle_timeout: Optional[int] = None,
    sso_session_max_lifespan: Optional[int] = None,
    sso_session_idle_timeout_remember_me: Optional[int] = None,
    sso_session_max_lifespan_remember_me: Optional[int] = None,
    offline_session_idle_timeout: Optional[int] = None,
    offline_session_max_lifespan: Optional[int] = None,
    offline_session_max_lifespan_enabled: Optional[bool] = None,
    client_session_idle_timeout: Optional[int] = None,
    client_session_max_lifespan: Optional[int] = None,
    access_token_lifespan: Optional[int] = None,
    remember_me: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update session timeout and configuration settings for the realm.

    Configure session timeouts, lifespans, and SSO settings. All timeouts
    are specified in seconds.

    Args:
        sso_session_idle_timeout: SSO session idle timeout in seconds
        sso_session_max_lifespan: SSO session max lifespan in seconds
        sso_session_idle_timeout_remember_me: SSO idle timeout with remember me in seconds
        sso_session_max_lifespan_remember_me: SSO max lifespan with remember me in seconds
        offline_session_idle_timeout: Offline session idle timeout in seconds
        offline_session_max_lifespan: Offline session max lifespan in seconds
        offline_session_max_lifespan_enabled: Whether to enable offline session max lifespan
        client_session_idle_timeout: Client session idle timeout in seconds
        client_session_max_lifespan: Client session max lifespan in seconds
        access_token_lifespan: Access token lifespan in seconds
        remember_me: Whether to enable remember me functionality
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Build update data with only provided values
    update_data = {}

    if sso_session_idle_timeout is not None:
        update_data["ssoSessionIdleTimeout"] = sso_session_idle_timeout
    if sso_session_max_lifespan is not None:
        update_data["ssoSessionMaxLifespan"] = sso_session_max_lifespan
    if sso_session_idle_timeout_remember_me is not None:
        update_data["ssoSessionIdleTimeoutRememberMe"] = (
            sso_session_idle_timeout_remember_me
        )
    if sso_session_max_lifespan_remember_me is not None:
        update_data["ssoSessionMaxLifespanRememberMe"] = (
            sso_session_max_lifespan_remember_me
        )
    if offline_session_idle_timeout is not None:
        update_data["offlineSessionIdleTimeout"] = offline_session_idle_timeout
    if offline_session_max_lifespan is not None:
        update_data["offlineSessionMaxLifespan"] = offline_session_max_lifespan
    if offline_session_max_lifespan_enabled is not None:
        update_data["offlineSessionMaxLifespanEnabled"] = (
            offline_session_max_lifespan_enabled
        )
    if client_session_idle_timeout is not None:
        update_data["clientSessionIdleTimeout"] = client_session_idle_timeout
    if client_session_max_lifespan is not None:
        update_data["clientSessionMaxLifespan"] = client_session_max_lifespan
    if access_token_lifespan is not None:
        update_data["accessTokenLifespan"] = access_token_lifespan
    if remember_me is not None:
        update_data["rememberMe"] = remember_me

    if not update_data:
        raise ValueError(
            "At least one session configuration parameter must be provided"
        )

    # Update realm configuration
    await client._make_request("PUT", "/", data=update_data, realm=realm)

    return {
        "status": "updated",
        "realm": realm or client.realm_name,
        "message": f"Session configuration updated with {len(update_data)} settings",
        "updated_settings": list(update_data.keys()),
    }


# Convenience Functions


@mcp.tool()
async def monitor_active_sessions(
    include_user_details: bool = False,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive monitoring view of all active sessions in the realm.

    Provides a monitoring dashboard view of session activity including
    statistics, client breakdown, and optionally detailed user information.

    Args:
        include_user_details: Whether to include detailed user session information
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive session monitoring data
    """
    # Get basic realm session summary
    summary = await get_realm_sessions_summary(realm=realm)

    monitoring_data = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "session_summary": summary,
    }

    if include_user_details:
        # Get detailed session information (this can be expensive)
        monitoring_data["detailed_sessions"] = []

        # Note: This is a simplified approach. For large realms, consider pagination
        # and limiting the number of sessions returned
        try:
            # This would require iterating through users which can be expensive
            # For now, we'll include a note about the limitation
            monitoring_data["user_sessions_note"] = (
                "Detailed user session information not included. "
                "Use find_user_sessions() for specific user lookups."
            )
        except Exception as e:
            monitoring_data["user_sessions_error"] = str(e)

    return monitoring_data


@mcp.tool()
async def cleanup_inactive_sessions(
    dry_run: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Identify and optionally clean up inactive sessions in the realm.

    Note: This function identifies sessions that may be candidates for cleanup
    based on current session configuration. Actual cleanup is performed by
    the logout operations.

    Args:
        dry_run: If True, only report what would be cleaned up (default: True)
        realm: Target realm (uses default if not specified)

    Returns:
        Cleanup report with session analysis
    """
    # Get session configuration to understand timeouts
    session_config = await get_session_configuration(realm=realm)

    # Get current session summary
    summary = await get_realm_sessions_summary(realm=realm)

    cleanup_info = {
        "realm": realm or client.realm_name,
        "dry_run": dry_run,
        "session_config": session_config,
        "current_sessions": summary,
        "cleanup_recommendations": [],
    }

    # Analyze session timeouts
    idle_timeout = session_config.get("sso_session_idle_timeout")
    max_lifespan = session_config.get("sso_session_max_lifespan")

    if idle_timeout:
        cleanup_info["cleanup_recommendations"].append(
            {
                "type": "idle_timeout",
                "timeout_seconds": idle_timeout,
                "message": f"Sessions idle for more than {idle_timeout} seconds may be automatically cleaned up",
            }
        )

    if max_lifespan:
        cleanup_info["cleanup_recommendations"].append(
            {
                "type": "max_lifespan",
                "lifespan_seconds": max_lifespan,
                "message": f"Sessions older than {max_lifespan} seconds may be automatically cleaned up",
            }
        )

    if dry_run:
        cleanup_info["message"] = "Dry run mode - no sessions were modified"
        cleanup_info["actions_available"] = [
            "Use logout_user_sessions() to log out specific users",
            "Use logout_all_users() to log out all users in the realm",
        ]
    else:
        cleanup_info["message"] = (
            "Cleanup mode not implemented - use specific logout operations"
        )

    return cleanup_info


# Helper method for client class
def _get_current_timestamp(self):
    """Get current timestamp in ISO format."""
    import datetime

    return datetime.datetime.now(datetime.UTC).isoformat() + "Z"


# Add the method to the client class
KeycloakClient._get_current_timestamp = _get_current_timestamp
