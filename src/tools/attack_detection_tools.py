from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Brute Force Protection


@mcp.tool()
async def get_user_brute_force_status(
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the brute force detection status for a specific user.

    Returns information about whether a user account is currently affected
    by brute-force protection mechanisms, including failure counts and lockout status.

    Args:
        user_id: ID of the user to check
        realm: Target realm (uses default if not specified)

    Returns:
        Brute force status object with failure information
    """
    return await client._make_request(
        "GET", f"/attack-detection/brute-force/users/{user_id}", realm=realm
    )


@mcp.tool()
async def clear_user_login_failures(
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Clear login failures for a specific user.

    Removes any recorded login failures for the specified user,
    effectively releasing them from temporary lockout due to brute force protection.

    Args:
        user_id: ID of the user to clear failures for
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with operation result
    """
    await client._make_request(
        "DELETE", f"/attack-detection/brute-force/users/{user_id}", realm=realm
    )

    return {
        "status": "cleared",
        "user_id": user_id,
        "message": f"Login failures cleared for user {user_id}",
        "action": "user_unlocked",
    }


@mcp.tool()
async def clear_all_user_login_failures(
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Clear login failures for all users in the realm.

    Removes all recorded login failures for every user in the realm,
    releasing all temporarily disabled users from brute force protection lockouts.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with operation result
    """
    await client._make_request(
        "DELETE", "/attack-detection/brute-force/users", realm=realm
    )

    return {
        "status": "cleared_all",
        "realm": realm or client.realm_name,
        "message": "Login failures cleared for all users in realm",
        "action": "all_users_unlocked",
    }


# Enhanced Monitoring and Management


@mcp.tool()
async def get_realm_brute_force_summary(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get summary of brute force protection status across the realm.

    Provides an overview of brute force protection settings and current
    lockout statistics. Note: This requires checking individual users
    as Keycloak doesn't provide a realm-wide summary endpoint.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Summary of brute force protection status
    """
    # Get realm configuration to check brute force settings
    from . import realm_tools

    realm_config = await realm_tools.get_realm_info(realm=realm)

    # Extract brute force related configuration
    brute_force_config = {
        "realm": realm_config.get("realm"),
        "brute_force_protected": realm_config.get("bruteForceProtected", False),
        "permanent_lockout": realm_config.get("permanentLockout", False),
        "max_login_failures": realm_config.get("maxLoginFailures"),
        "wait_increment_seconds": realm_config.get("waitIncrementSeconds"),
        "quick_login_check_milli": realm_config.get("quickLoginCheckMilliSeconds"),
        "minimum_quick_login_wait": realm_config.get("minimumQuickLoginWaitSeconds"),
        "max_failure_wait_seconds": realm_config.get("maxFailureWaitSeconds"),
        "failure_reset_time_seconds": realm_config.get("failureResetTimeSeconds"),
    }

    # Remove None values
    brute_force_config = {k: v for k, v in brute_force_config.items() if v is not None}

    return {
        "realm": realm or client.realm_name,
        "brute_force_configuration": brute_force_config,
        "protection_enabled": brute_force_config.get("brute_force_protected", False),
        "timestamp": client._get_current_timestamp(),
        "note": "Individual user lockout status can be checked using get_user_brute_force_status()",
    }


@mcp.tool()
async def monitor_failed_login_attempts(
    user_id: Optional[str] = None,
    include_recent_events: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Monitor failed login attempts and brute force activities.

    Combines brute force status with recent login events to provide
    comprehensive monitoring of authentication failures and attack attempts.

    Args:
        user_id: Specific user to monitor (optional, monitors all if not provided)
        include_recent_events: Whether to include recent login events
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive monitoring data for failed login attempts
    """
    monitoring_data = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "user_id": user_id,
    }

    # Get brute force protection configuration
    brute_force_summary = await get_realm_brute_force_summary(realm=realm)
    monitoring_data["brute_force_config"] = brute_force_summary[
        "brute_force_configuration"
    ]

    # If specific user requested, get their brute force status
    if user_id:
        try:
            user_status = await get_user_brute_force_status(user_id, realm=realm)
            monitoring_data["user_brute_force_status"] = user_status
        except Exception as e:
            monitoring_data["user_brute_force_status"] = {
                "error": str(e),
                "note": "User may not exist or have no login attempts",
            }

    # Include recent login events if requested
    if include_recent_events:
        try:
            from . import events_tools

            # Get recent login failure events
            recent_events = await events_tools.get_user_events(
                type_filter=["LOGIN_ERROR", "INVALID_USER_CREDENTIALS"],
                max=20,
                realm=realm,
            )

            # Filter events for specific user if provided
            if user_id:
                recent_events = [
                    event for event in recent_events if event.get("userId") == user_id
                ]

            monitoring_data["recent_failed_logins"] = recent_events
            monitoring_data["failed_attempts_count"] = len(recent_events)
        except Exception as e:
            monitoring_data["recent_failed_logins"] = {
                "error": str(e),
                "note": "Unable to fetch recent login events",
            }

    return monitoring_data


@mcp.tool()
async def bulk_unlock_users(
    user_ids: List[str],
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Clear login failures for multiple specific users.

    Efficiently unlocks multiple users who may be locked due to
    brute force protection, providing detailed results for each user.

    Args:
        user_ids: List of user IDs to unlock
        realm: Target realm (uses default if not specified)

    Returns:
        Results of unlock operations for each user
    """
    if not user_ids:
        raise ValueError("At least one user ID must be provided")

    results = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "total_users": len(user_ids),
        "results": [],
        "summary": {"successful": 0, "failed": 0},
    }

    for user_id in user_ids:
        try:
            await client._make_request(
                "DELETE", f"/attack-detection/brute-force/users/{user_id}", realm=realm
            )
            results["results"].append(
                {
                    "user_id": user_id,
                    "status": "success",
                    "message": f"Login failures cleared for user {user_id}",
                }
            )
            results["summary"]["successful"] += 1
        except Exception as e:
            results["results"].append(
                {
                    "user_id": user_id,
                    "status": "failed",
                    "error": str(e),
                    "message": f"Failed to clear login failures for user {user_id}",
                }
            )
            results["summary"]["failed"] += 1

    return results


@mcp.tool()
async def configure_brute_force_protection(
    enabled: bool,
    permanent_lockout: Optional[bool] = None,
    max_login_failures: Optional[int] = None,
    wait_increment_seconds: Optional[int] = None,
    quick_login_check_milli: Optional[int] = None,
    minimum_quick_login_wait: Optional[int] = None,
    max_failure_wait_seconds: Optional[int] = None,
    failure_reset_time_seconds: Optional[int] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Configure brute force protection settings for the realm.

    Updates the realm's brute force protection configuration with the
    specified settings to control how authentication failures are handled.

    Args:
        enabled: Whether brute force protection is enabled
        permanent_lockout: Whether to permanently lock accounts after max failures
        max_login_failures: Maximum allowed login failures before lockout
        wait_increment_seconds: Time increment added to wait time after each failure
        quick_login_check_milli: Quick login check time in milliseconds
        minimum_quick_login_wait: Minimum quick login wait time in seconds
        max_failure_wait_seconds: Maximum wait time after failures in seconds
        failure_reset_time_seconds: Time after which failure count resets
        realm: Target realm (uses default if not specified)

    Returns:
        Status of configuration update with applied settings
    """
    # Build update data with only provided values
    update_data = {"bruteForceProtected": enabled}

    if permanent_lockout is not None:
        update_data["permanentLockout"] = permanent_lockout
    if max_login_failures is not None:
        update_data["maxLoginFailures"] = max_login_failures
    if wait_increment_seconds is not None:
        update_data["waitIncrementSeconds"] = wait_increment_seconds
    if quick_login_check_milli is not None:
        update_data["quickLoginCheckMilliSeconds"] = quick_login_check_milli
    if minimum_quick_login_wait is not None:
        update_data["minimumQuickLoginWaitSeconds"] = minimum_quick_login_wait
    if max_failure_wait_seconds is not None:
        update_data["maxFailureWaitSeconds"] = max_failure_wait_seconds
    if failure_reset_time_seconds is not None:
        update_data["failureResetTimeSeconds"] = failure_reset_time_seconds

    # Update realm configuration
    await client._make_request("PUT", "/", data=update_data, realm=realm)

    return {
        "status": "updated",
        "realm": realm or client.realm_name,
        "message": "Brute force protection configuration updated",
        "enabled": enabled,
        "updated_settings": list(update_data.keys()),
        "configuration": update_data,
    }


# Convenience Functions


@mcp.tool()
async def emergency_unlock_all_users(
    confirm: bool = False,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Emergency function to unlock all users in the realm.

    Provides a safety mechanism to quickly unlock all users during
    security incidents or mass lockouts. Requires explicit confirmation.

    Args:
        confirm: Must be True to execute (safety check)
        realm: Target realm (uses default if not specified)

    Returns:
        Status of emergency unlock operation
    """
    if not confirm:
        return {
            "status": "confirmation_required",
            "message": "Emergency unlock requires explicit confirmation",
            "action_required": "Set confirm=True to execute emergency unlock",
            "warning": "This will unlock ALL users in the realm",
        }

    # Clear all user login failures
    await clear_all_user_login_failures(realm=realm)

    return {
        "status": "emergency_unlock_completed",
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "message": "Emergency unlock completed - all users unlocked",
        "action": "all_users_unlocked",
        "warning": "Monitor for continued attack patterns",
    }


@mcp.tool()
async def analyze_brute_force_patterns(
    days_lookback: int = 7,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze brute force attack patterns from recent events.

    Examines recent login events to identify potential brute force
    attack patterns, frequent failures, and security threats.

    Args:
        days_lookback: Number of days to look back for events (default: 7)
        realm: Target realm (uses default if not specified)

    Returns:
        Analysis of brute force attack patterns and recommendations
    """
    import datetime

    # Calculate date range
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days_lookback)

    analysis = {
        "realm": realm or client.realm_name,
        "analysis_period": {
            "start_date": start_date.isoformat() + "Z",
            "end_date": end_date.isoformat() + "Z",
            "days": days_lookback,
        },
        "timestamp": client._get_current_timestamp(),
    }

    try:
        from . import events_tools

        # Get failed login events
        failed_events = await events_tools.get_user_events(
            type_filter=[
                "LOGIN_ERROR",
                "INVALID_USER_CREDENTIALS",
                "USER_DISABLED_BY_PERMANENT_LOCKOUT",
            ],
            date_from=start_date.strftime("%Y-%m-%d"),
            date_to=end_date.strftime("%Y-%m-%d"),
            max=500,  # Limit to prevent excessive API calls
            realm=realm,
        )

        # Analyze patterns
        user_failures = {}
        ip_failures = {}
        client_failures = {}
        hourly_distribution = {}

        for event in failed_events:
            # Count failures by user
            user_id = event.get("userId", "unknown")
            user_failures[user_id] = user_failures.get(user_id, 0) + 1

            # Count failures by IP
            ip_address = event.get("ipAddress", "unknown")
            ip_failures[ip_address] = ip_failures.get(ip_address, 0) + 1

            # Count failures by client
            client_id = event.get("clientId", "unknown")
            client_failures[client_id] = client_failures.get(client_id, 0) + 1

            # Count failures by hour
            event_time = datetime.datetime.fromtimestamp(event.get("time", 0) / 1000)
            hour_key = event_time.strftime("%Y-%m-%d %H:00")
            hourly_distribution[hour_key] = hourly_distribution.get(hour_key, 0) + 1

        # Generate analysis
        analysis.update(
            {
                "total_failed_attempts": len(failed_events),
                "unique_users_affected": len(user_failures),
                "unique_source_ips": len(ip_failures),
                "unique_clients_affected": len(client_failures),
                "top_targeted_users": sorted(
                    user_failures.items(), key=lambda x: x[1], reverse=True
                )[:10],
                "top_attacking_ips": sorted(
                    ip_failures.items(), key=lambda x: x[1], reverse=True
                )[:10],
                "hourly_failure_distribution": dict(
                    sorted(hourly_distribution.items())
                ),
                "attack_analysis": {
                    "potential_brute_force": len(failed_events) > 50,
                    "concentrated_attacks": any(
                        count > 20 for count in ip_failures.values()
                    ),
                    "widespread_targeting": len(user_failures) > 10,
                },
            }
        )

        # Generate recommendations
        recommendations = []
        if analysis["total_failed_attempts"] > 100:
            recommendations.append(
                "High number of failed attempts detected - review brute force settings"
            )
        if any(count > 50 for count in ip_failures.values()):
            recommendations.append(
                "Concentrated attacks from specific IPs - consider IP-based blocking"
            )
        if len(user_failures) > 20:
            recommendations.append(
                "Widespread user targeting - ensure users have strong passwords"
            )

        analysis["recommendations"] = recommendations

    except Exception as e:
        analysis["error"] = str(e)
        analysis["note"] = (
            "Unable to analyze events - events may not be enabled or accessible"
        )

    return analysis


@mcp.tool()
async def get_brute_force_configuration(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current brute force protection configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing current brute force protection settings
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    return {
        "realm": realm or client.realm_name,
        "bruteForceProtected": realm_info.get("bruteForceProtected", False),
        "permanentLockout": realm_info.get("permanentLockout", False),
        "maxFailureWaitSeconds": realm_info.get("maxFailureWaitSeconds", 900),
        "minimumQuickLoginWaitSeconds": realm_info.get(
            "minimumQuickLoginWaitSeconds", 60
        ),
        "waitIncrementSeconds": realm_info.get("waitIncrementSeconds", 60),
        "quickLoginCheckMilliSeconds": realm_info.get(
            "quickLoginCheckMilliSeconds", 1000
        ),
        "maxDeltaTimeSeconds": realm_info.get("maxDeltaTimeSeconds", 43200),
        "failureFactor": realm_info.get("failureFactor", 30),
        "maxTemporaryLockouts": realm_info.get("maxTemporaryLockouts", 0),
    }


@mcp.tool()
async def get_failed_login_events(
    days_back: int = 7, max_events: int = 100, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent failed login events from the realm.

    Args:
        days_back: Number of days back to search for events
        max_events: Maximum number of events to return
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing failed login events and summary
    """
    from . import events_tools
    import datetime

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)

    failed_events = await events_tools.get_user_events(
        type_filter=["LOGIN_ERROR", "INVALID_USER_CREDENTIALS"],
        date_from=start_date.strftime("%Y-%m-%d"),
        date_to=end_date.strftime("%Y-%m-%d"),
        max=max_events,
        realm=realm,
    )

    return {
        "events": failed_events,
        "summary": {
            "total_events": len(failed_events),
            "period_days": days_back,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        },
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def get_brute_force_statistics(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive brute force attack statistics and metrics.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing brute force statistics and analysis
    """
    # Get configuration
    config = await get_brute_force_configuration(realm=realm)

    # Get recent failed events
    failed_events_data = await get_failed_login_events(days_back=7, realm=realm)
    failed_events = failed_events_data["events"]

    # Generate statistics
    statistics = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "protection_enabled": config["bruteForceProtected"],
        "configuration": config,
        "recent_activity": {
            "failed_logins_7_days": len(failed_events),
            "unique_users_affected": len(
                set(
                    event.get("userId")
                    for event in failed_events
                    if event.get("userId")
                )
            ),
            "unique_source_ips": len(
                set(
                    event.get("ipAddress")
                    for event in failed_events
                    if event.get("ipAddress")
                )
            ),
        },
    }

    # Calculate attack indicators
    if len(failed_events) > 50:
        statistics["attack_indicators"] = {
            "high_volume_attacks": True,
            "concentrated_failures": any(
                len([e for e in failed_events if e.get("ipAddress") == ip]) > 20
                for ip in set(
                    event.get("ipAddress")
                    for event in failed_events
                    if event.get("ipAddress")
                )
            ),
            "distributed_targeting": len(
                set(
                    event.get("userId")
                    for event in failed_events
                    if event.get("userId")
                )
            )
            > 10,
        }
    else:
        statistics["attack_indicators"] = {
            "high_volume_attacks": False,
            "concentrated_failures": False,
            "distributed_targeting": False,
        }

    return statistics


@mcp.tool()
async def enable_brute_force_protection(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Enable brute force protection with security best practices.

    This is a convenience function that enables brute force protection
    with recommended security settings.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary indicating the result of enabling protection
    """
    try:
        await configure_brute_force_protection(
            enabled=True,
            max_failure_wait_seconds=900,  # 15 minutes
            minimum_quick_login_wait_seconds=60,  # 1 minute
            wait_increment_seconds=60,
            failure_factor=30,
            realm=realm,
        )

        return {
            "success": True,
            "message": "Brute force protection enabled with security best practices",
            "realm": realm or client.realm_name,
            "settings_applied": {
                "enabled": True,
                "max_failure_wait_seconds": 900,
                "minimum_quick_login_wait_seconds": 60,
                "wait_increment_seconds": 60,
                "failure_factor": 30,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to enable brute force protection",
            "realm": realm or client.realm_name,
        }


@mcp.tool()
async def get_security_monitoring_summary(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a comprehensive security monitoring summary including brute force protection,
    recent attack patterns, and security recommendations.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing comprehensive security monitoring information
    """
    # Gather all security monitoring data
    config = await get_brute_force_configuration(realm=realm)
    statistics = await get_brute_force_statistics(realm=realm)
    pattern_analysis = await analyze_brute_force_patterns(realm=realm)

    summary = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "security_status": "unknown",
        "brute_force_protection": {
            "enabled": config["bruteForceProtected"],
            "configuration": config,
        },
        "attack_statistics": statistics,
        "pattern_analysis": pattern_analysis,
        "recommendations": [],
    }

    # Determine overall security status
    if not config["bruteForceProtected"]:
        summary["security_status"] = "warning"
        summary["recommendations"].append("Enable brute force protection")
    elif statistics["recent_activity"]["failed_logins_7_days"] > 100:
        summary["security_status"] = "alert"
        summary["recommendations"].append(
            "High number of failed logins detected - investigate potential attacks"
        )
    elif statistics["attack_indicators"]["high_volume_attacks"]:
        summary["security_status"] = "warning"
        summary["recommendations"].append(
            "Unusual attack patterns detected - review security logs"
        )
    else:
        summary["security_status"] = "healthy"
        summary["recommendations"].append(
            "Security monitoring is active and no threats detected"
        )

    # Add pattern-based recommendations
    if pattern_analysis.get("recommendations"):
        summary["recommendations"].extend(pattern_analysis["recommendations"])

    return summary
