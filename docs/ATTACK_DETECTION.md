# Attack Detection Tools

This document describes the attack detection tools available in the MCP Keycloak server for managing brute force protection.

## Overview

The attack detection tools allow you to monitor and manage Keycloak's brute force detection system. This system temporarily locks users after repeated failed login attempts to prevent password guessing attacks.

## Available Tools

### 1. get_user_brute_force_status

Get the current brute force detection status for a specific user.

**Function:** `get_user_brute_force_status(user_id, realm=None)`

**Parameters:**
- `user_id` (string, required): The user's ID
- `realm` (string, optional): Target realm (uses default if not specified)

**Returns:**
Dictionary containing status information:
- `numFailures`: Number of failed login attempts
- `disabled`: Whether the user is temporarily disabled
- `lastIPFailure`: Last IP address that had a failed login
- `lastFailure`: Timestamp of last failure

**Example:**
```python
status = await get_user_brute_force_status("user-uuid-123")
print(f"Failed attempts: {status.get('numFailures', 0)}")
print(f"User locked: {status.get('disabled', False)}")
```

**API Endpoint:** `GET /admin/realms/{realm}/attack-detection/brute-force/users/{userId}`

---

### 2. clear_user_login_failures

Clear login failures for a specific user, releasing them from temporary lockout.

**Function:** `clear_user_login_failures(user_id, realm=None)`

**Parameters:**
- `user_id` (string, required): The user's ID
- `realm` (string, optional): Target realm (uses default if not specified)

**Returns:**
Dictionary with status message:
```python
{
    "status": "cleared",
    "message": "Login failures cleared for user {user_id}"
}
```

**Example:**
```python
result = await clear_user_login_failures("user-uuid-123")
print(result["message"])  # "Login failures cleared for user user-uuid-123"
```

**API Endpoint:** `DELETE /admin/realms/{realm}/attack-detection/brute-force/users/{userId}`

**Notes:**
- This operation is idempotent - calling it multiple times is safe
- Works even if the user has no failures
- Returns 204 No Content from Keycloak API

---

### 3. clear_all_login_failures

Clear login failures for all users in the realm, releasing all temporarily locked users.

**Function:** `clear_all_login_failures(realm=None)`

**Parameters:**
- `realm` (string, optional): Target realm (uses default if not specified)

**Returns:**
Dictionary with status message:
```python
{
    "status": "cleared",
    "message": "Login failures cleared for all users"
}
```

**Example:**
```python
result = await clear_all_login_failures()
print(result["message"])  # "Login failures cleared for all users"
```

**API Endpoint:** `DELETE /admin/realms/{realm}/attack-detection/brute-force/users`

**Warning:**
- This affects ALL users in the realm
- Use with caution in production environments
- Consider clearing individual users instead for targeted remediation

---

## Use Cases

### Monitoring Failed Login Attempts

Check if a user has exceeded the brute force threshold:

```python
status = await get_user_brute_force_status(user_id)

if status.get("disabled"):
    print(f"User is locked out after {status['numFailures']} failed attempts")
    print(f"Last failure from IP: {status.get('lastIPFailure')}")
```

### Unlocking a Single User

When a legitimate user is locked out after forgetting their password:

```python
# Clear the failures
await clear_user_login_failures(user_id)

# Optionally reset their password
await reset_user_password(user_id, new_password, temporary=True)
```

### Bulk Unlock After System Issues

If a system issue caused legitimate users to be locked out:

```python
# Clear all failures
await clear_all_login_failures()

# Log the action
logger.info("Cleared all brute force failures due to system issue #1234")
```

### Automated Monitoring

Create a monitoring script that checks for locked users:

```python
users = await list_users()

locked_users = []
for user in users:
    status = await get_user_brute_force_status(user["id"])
    if status.get("disabled"):
        locked_users.append({
            "username": user["username"],
            "failures": status["numFailures"],
            "last_failure": status.get("lastFailure")
        })

if locked_users:
    alert(f"{len(locked_users)} users are currently locked out")
```

## Configuration

Brute force detection is configured at the realm level in Keycloak:

1. Login to Keycloak Admin Console
2. Select your realm
3. Go to **Realm Settings** → **Security Defenses** → **Brute Force Detection**
4. Configure:
   - **Permanent Lockout**: Lock user permanently after failures
   - **Max Login Failures**: Number of failures before lockout
   - **Wait Increment**: Time added to wait after each failure
   - **Quick Login Check**: Milliseconds between login attempts
   - **Minimum Quick Login Wait**: Minimum time between quick logins
   - **Max Wait**: Maximum wait time

**Note:** The attack detection tools only clear failure counts. They do not modify the realm's brute force detection settings.

## Best Practices

1. **Monitor Before Clearing**: Always check the status before clearing failures to understand the issue
2. **Log Actions**: Log when you clear failures for audit purposes
3. **Investigate Patterns**: Look for patterns in failed attempts (IP addresses, timing) before clearing
4. **User-Specific Actions**: Prefer clearing individual users over bulk clearing
5. **Combine with Password Reset**: When unlocking users, consider if they need a password reset
6. **Automate Monitoring**: Set up alerts for high failure counts
7. **Review Configuration**: Ensure brute force settings match your security requirements

## Security Considerations

- **Admin Permissions Required**: These tools require realm admin permissions
- **Audit Logging**: Consider enabling Keycloak's event logging to track admin actions
- **Careful with Bulk Operations**: `clear_all_login_failures()` affects all users
- **Investigate Before Clearing**: Don't automatically clear failures without investigation
- **Consider Attack Patterns**: Multiple failed attempts might indicate an actual attack
- **IP Whitelisting**: Consider IP whitelisting for trusted internal systems

## Testing

The attack detection tools include comprehensive integration tests:

```bash
# Run attack detection tests
uv run pytest tests/test_attack_detection.py -v

# All tests
uv run pytest -v
```

Test coverage includes:
- Getting brute force status for users
- Clearing individual user failures
- Bulk clearing all failures
- Idempotent operations
- Non-existent user handling
- Realm parameter validation

## API Reference

All endpoints require authentication with admin privileges.

**Base Path:** `/admin/realms/{realm}/attack-detection/brute-force`

| Method | Endpoint           | Description                                 |
| ------ | ------------------ | ------------------------------------------- |
| GET    | `/users/{userId}`  | Get user's brute force detection status     |
| DELETE | `/users/{userId}`  | Clear specific user's login failures        |
| DELETE | `/users`           | Clear all users' login failures in realm    |

## Related Tools

- `list_users`: List users to find those who might be locked out
- `get_user`: Get user details including enabled status
- `reset_user_password`: Reset password for locked out users
- `update_user`: Enable/disable users manually

## References

- [Keycloak Admin REST API - Attack Detection](https://www.keycloak.org/docs-api/latest/rest-api/index.html#_attack_detection_resource)
- [Keycloak Server Administration - Brute Force Detection](https://www.keycloak.org/docs/latest/server_admin/#password-guess-brute-force-attacks)
