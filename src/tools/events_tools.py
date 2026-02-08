from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# User Events Management


@mcp.tool()
async def get_user_events(
    client_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    direction: Optional[str] = None,
    first: Optional[int] = None,
    ip_address: Optional[str] = None,
    max: Optional[int] = None,
    event_type: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get user events for a realm.

    Returns events like login, logout, registration, errors, etc.
    Events can be filtered by various criteria.

    Args:
        client_id: Filter by app or OAuth client name
        date_from: From date (yyyy-MM-dd) or Epoch timestamp in millis
        date_to: To date (yyyy-MM-dd) or Epoch timestamp in millis
        direction: Sort direction ("asc" or "desc")
        first: Pagination offset
        ip_address: Filter by IP address
        max: Maximum results (defaults to 100)
        event_type: List of event types to return (e.g., ["LOGIN", "LOGOUT"])
        user_id: Filter by user ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of user event objects
    """
    params = {}
    if client_id:
        params["client"] = client_id
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if direction:
        params["direction"] = direction
    if first is not None:
        params["first"] = first
    if ip_address:
        params["ipAddress"] = ip_address
    if max is not None:
        params["max"] = max
    if event_type:
        params["type"] = event_type
    if user_id:
        params["user"] = user_id

    return await client._make_request("GET", "/events", params=params, realm=realm)


@mcp.tool()
async def clear_user_events(
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete all user events for a realm.

    WARNING: This permanently deletes all user event history.
    Use with caution, especially in production environments.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", "/events", realm=realm)
    return {
        "status": "cleared",
        "message": "All user events cleared successfully",
    }


# Admin Events Management


@mcp.tool()
async def get_admin_events(
    auth_client: Optional[str] = None,
    auth_ip_address: Optional[str] = None,
    auth_realm: Optional[str] = None,
    auth_user: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    first: Optional[int] = None,
    max: Optional[int] = None,
    operation_types: Optional[List[str]] = None,
    resource_path: Optional[str] = None,
    resource_types: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get admin events for a realm.

    Returns administrative events like configuration changes, CRUD operations
    on users/clients/roles, etc. Events are returned in reverse chronological order.

    Args:
        auth_client: Filter by the client that performed the operation
        auth_ip_address: Filter by IP address of the admin
        auth_realm: Filter by the realm of the admin
        auth_user: Filter by the user ID of the admin
        date_from: From date (yyyy-MM-dd) or Epoch timestamp in millis
        date_to: To date (yyyy-MM-dd) or Epoch timestamp in millis
        first: Pagination offset
        max: Maximum results (defaults to 100)
        operation_types: List of operation types (e.g., ["CREATE", "UPDATE", "DELETE"])
        resource_path: Filter by resource path
        resource_types: List of resource types (e.g., ["USER", "CLIENT", "REALM"])
        realm: Target realm (uses default if not specified)

    Returns:
        List of admin event objects
    """
    params = {}
    if auth_client:
        params["authClient"] = auth_client
    if auth_ip_address:
        params["authIpAddress"] = auth_ip_address
    if auth_realm:
        params["authRealm"] = auth_realm
    if auth_user:
        params["authUser"] = auth_user
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if operation_types:
        params["operationTypes"] = operation_types
    if resource_path:
        params["resourcePath"] = resource_path
    if resource_types:
        params["resourceTypes"] = resource_types

    return await client._make_request(
        "GET", "/admin-events", params=params, realm=realm
    )


@mcp.tool()
async def clear_admin_events(
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete all admin events for a realm.

    WARNING: This permanently deletes all admin event history.
    Use with caution, especially in production environments.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", "/admin-events", realm=realm)
    return {
        "status": "cleared",
        "message": "All admin events cleared successfully",
    }


# Events Configuration Management


@mcp.tool()
async def get_events_config(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the events configuration for a realm.

    Returns settings for user events and admin events including:
    - Whether events are enabled
    - Event expiration time
    - Event listeners
    - Enabled event types

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Events configuration object
    """
    return await client._make_request("GET", "/events/config", realm=realm)


@mcp.tool()
async def update_events_config(
    events_enabled: Optional[bool] = None,
    events_expiration: Optional[int] = None,
    events_listeners: Optional[List[str]] = None,
    enabled_event_types: Optional[List[str]] = None,
    admin_events_enabled: Optional[bool] = None,
    admin_events_details_enabled: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update the events configuration for a realm.

    Configure user event and admin event settings including which events
    to capture, how long to retain them, and which listeners to use.

    Args:
        events_enabled: Enable/disable user events
        events_expiration: Event expiration time in seconds
        events_listeners: List of event listener IDs (e.g., ["jboss-logging"])
        enabled_event_types: List of user event types to capture (e.g., ["LOGIN", "LOGOUT"])
        admin_events_enabled: Enable/disable admin events
        admin_events_details_enabled: Include detailed representation in admin events
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current configuration
    current_config = await client._make_request("GET", "/events/config", realm=realm)

    # Update only provided fields
    if events_enabled is not None:
        current_config["eventsEnabled"] = events_enabled
    if events_expiration is not None:
        current_config["eventsExpiration"] = events_expiration
    if events_listeners is not None:
        current_config["eventsListeners"] = events_listeners
    if enabled_event_types is not None:
        current_config["enabledEventTypes"] = enabled_event_types
    if admin_events_enabled is not None:
        current_config["adminEventsEnabled"] = admin_events_enabled
    if admin_events_details_enabled is not None:
        current_config["adminEventsDetailsEnabled"] = admin_events_details_enabled

    await client._make_request(
        "PUT", "/events/config", data=current_config, realm=realm
    )
    return {
        "status": "updated",
        "message": "Events configuration updated successfully",
    }


# Convenience Functions


@mcp.tool()
async def enable_user_events(
    event_types: Optional[List[str]] = None,
    expiration_seconds: int = 86400,
    listeners: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Enable user events with common settings (convenience function).

    Enables user event logging with specified event types and retention period.

    Args:
        event_types: List of event types to capture (defaults to common events)
        expiration_seconds: How long to retain events in seconds (default: 86400 = 1 day)
        listeners: Event listeners to use (defaults to ["jboss-logging"])
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    if event_types is None:
        # Default to common security-relevant events
        event_types = [
            "LOGIN",
            "LOGIN_ERROR",
            "LOGOUT",
            "REGISTER",
            "UPDATE_PASSWORD",
            "UPDATE_EMAIL",
            "REMOVE_TOTP",
            "UPDATE_TOTP",
        ]

    if listeners is None:
        listeners = ["jboss-logging"]

    return await update_events_config(
        events_enabled=True,
        events_expiration=expiration_seconds,
        events_listeners=listeners,
        enabled_event_types=event_types,
        realm=realm,
    )


@mcp.tool()
async def enable_admin_events(
    include_details: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Enable admin events (convenience function).

    Enables admin event logging to track administrative changes
    to the realm configuration.

    Args:
        include_details: Include full resource representation in events
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    return await update_events_config(
        admin_events_enabled=True,
        admin_events_details_enabled=include_details,
        realm=realm,
    )


@mcp.tool()
async def get_recent_login_events(
    max_results: int = 50,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get recent login events (convenience function).

    Returns recent LOGIN and LOGIN_ERROR events for security monitoring.

    Args:
        max_results: Maximum number of events to return (default: 50)
        realm: Target realm (uses default if not specified)

    Returns:
        List of login event objects
    """
    return await get_user_events(
        event_type=["LOGIN", "LOGIN_ERROR"],
        max=max_results,
        direction="desc",
        realm=realm,
    )


@mcp.tool()
async def get_recent_admin_changes(
    resource_type: Optional[str] = None,
    operation_type: Optional[str] = None,
    max_results: int = 50,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get recent administrative changes (convenience function).

    Returns recent admin events for auditing configuration changes.

    Args:
        resource_type: Filter by resource type (e.g., "USER", "CLIENT", "REALM")
        operation_type: Filter by operation (e.g., "CREATE", "UPDATE", "DELETE")
        max_results: Maximum number of events to return (default: 50)
        realm: Target realm (uses default if not specified)

    Returns:
        List of admin event objects
    """
    resource_types = [resource_type] if resource_type else None
    operation_types = [operation_type] if operation_type else None

    return await get_admin_events(
        resource_types=resource_types,
        operation_types=operation_types,
        max=max_results,
        realm=realm,
    )
