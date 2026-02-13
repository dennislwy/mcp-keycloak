from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# === User Credentials Management ===


@mcp.tool()
async def list_user_credentials(
    user_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all credentials for a user.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of user credentials with type, ID, and metadata
    """
    return await client._make_request(
        "GET", f"/users/{user_id}/credentials", realm=realm
    )


@mcp.tool()
async def delete_user_credential(
    user_id: str, credential_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Delete a specific credential for a user.

    Args:
        user_id: User ID
        credential_id: Credential ID to delete
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/users/{user_id}/credentials/{credential_id}", realm=realm
    )
    return {
        "status": "deleted",
        "message": f"Credential {credential_id} deleted for user {user_id}",
    }


@mcp.tool()
async def update_credential_label(
    user_id: str, credential_id: str, label: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Update the label/user-friendly name for a credential.

    Args:
        user_id: User ID
        credential_id: Credential ID
        label: New label for the credential
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Keycloak expects text/plain content type for this endpoint
    # Build URL
    realm_name = realm or client.realm_name
    url = f"{client.server_url}/admin/realms/{realm_name}/users/{user_id}/credentials/{credential_id}/userLabel"

    # Get HTTP client and headers
    http_client = await client._ensure_client()
    headers = await client._get_headers()
    headers["Content-Type"] = "text/plain"

    # Make request
    response = await http_client.put(url, content=label, headers=headers)

    # Retry on 401
    if response.status_code == 401:
        await client._get_token()
        headers = await client._get_headers()
        headers["Content-Type"] = "text/plain"
        response = await http_client.put(url, content=label, headers=headers)

    response.raise_for_status()

    return {
        "status": "updated",
        "message": f"Credential label updated to '{label}' for credential {credential_id}",
    }


@mcp.tool()
async def move_credential_to_first(
    user_id: str, credential_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Move a credential to first priority position.

    Args:
        user_id: User ID
        credential_id: Credential ID to move
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/users/{user_id}/credentials/{credential_id}/moveToFirst",
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Credential {credential_id} moved to first position",
    }


@mcp.tool()
async def move_credential_after(
    user_id: str,
    credential_id: str,
    previous_credential_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Move a credential to position after another credential.

    Args:
        user_id: User ID
        credential_id: Credential ID to move
        previous_credential_id: Credential ID to position after
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "POST",
        f"/users/{user_id}/credentials/{credential_id}/moveAfter/{previous_credential_id}",
        realm=realm,
    )
    return {
        "status": "updated",
        "message": f"Credential {credential_id} moved after {previous_credential_id}",
    }


# === User Consents Management ===


@mcp.tool()
async def list_user_consents(
    user_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all consents granted by a user.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of consents with client information and granted scopes
    """
    return await client._make_request("GET", f"/users/{user_id}/consents", realm=realm)


@mcp.tool()
async def revoke_user_consent(
    user_id: str, client_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Revoke consent granted by user for a specific client.

    Args:
        user_id: User ID
        client_id: Client database ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request(
        "DELETE", f"/users/{user_id}/consents/{client_id}", realm=realm
    )
    return {
        "status": "revoked",
        "message": f"Consent revoked for client {client_id} by user {user_id}",
    }


# === User Offline Sessions ===


@mcp.tool()
async def list_user_offline_sessions(
    user_id: str, client_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List offline sessions for a user for a specific client.

    Args:
        user_id: User ID
        client_id: Client database ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of offline sessions
    """
    return await client._make_request(
        "GET", f"/users/{user_id}/offline-sessions/{client_id}", realm=realm
    )


# === User Required Actions ===


@mcp.tool()
async def get_user_required_actions(
    user_id: str, realm: Optional[str] = None
) -> List[str]:
    """
    Get required actions for a user.

    Args:
        user_id: User ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of required action names
    """
    user = await client._make_request("GET", f"/users/{user_id}", realm=realm)
    return user.get("requiredActions", [])


@mcp.tool()
async def set_user_required_actions(
    user_id: str, required_actions: List[str], realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Set required actions for a user.

    Args:
        user_id: User ID
        required_actions: List of required action names (e.g., ['UPDATE_PASSWORD', 'VERIFY_EMAIL'])
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current user
    user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

    # Update required actions
    user["requiredActions"] = required_actions

    await client._make_request("PUT", f"/users/{user_id}", data=user, realm=realm)
    return {
        "status": "updated",
        "message": f"Required actions updated for user {user_id}",
    }


@mcp.tool()
async def add_user_required_action(
    user_id: str, action: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Add a required action to a user.

    Args:
        user_id: User ID
        action: Required action name (e.g., 'UPDATE_PASSWORD', 'VERIFY_EMAIL', 'UPDATE_PROFILE')
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current user
    user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

    # Add action if not already present
    current_actions = user.get("requiredActions", [])
    if action not in current_actions:
        current_actions.append(action)
        user["requiredActions"] = current_actions

        await client._make_request("PUT", f"/users/{user_id}", data=user, realm=realm)
        return {
            "status": "added",
            "message": f"Required action '{action}' added to user {user_id}",
        }
    else:
        return {
            "status": "skipped",
            "message": f"Required action '{action}' already exists for user {user_id}",
        }


@mcp.tool()
async def remove_user_required_action(
    user_id: str, action: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Remove a required action from a user.

    Args:
        user_id: User ID
        action: Required action name to remove
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current user
    user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

    # Remove action if present
    current_actions = user.get("requiredActions", [])
    if action in current_actions:
        current_actions.remove(action)
        user["requiredActions"] = current_actions

        await client._make_request("PUT", f"/users/{user_id}", data=user, realm=realm)
        return {
            "status": "removed",
            "message": f"Required action '{action}' removed from user {user_id}",
        }
    else:
        return {
            "status": "skipped",
            "message": f"Required action '{action}' not found for user {user_id}",
        }


# === Bulk User Operations ===


@mcp.tool()
async def bulk_reset_user_passwords(
    user_ids: List[str],
    password: str,
    temporary: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reset passwords for multiple users in bulk.

    Args:
        user_ids: List of user IDs
        password: New password for all users
        temporary: Whether the password is temporary (default True)
        realm: Target realm (uses default if not specified)

    Returns:
        Summary of success and failures
    """
    credential_data = {"type": "password", "value": password, "temporary": temporary}

    successes = []
    failures = []

    for user_id in user_ids:
        try:
            await client._make_request(
                "PUT",
                f"/users/{user_id}/reset-password",
                data=credential_data,
                realm=realm,
            )
            successes.append(user_id)
        except Exception as e:
            failures.append({"user_id": user_id, "error": str(e)})

    return {
        "status": "completed",
        "total": len(user_ids),
        "successes": len(successes),
        "failures": len(failures),
        "success_ids": successes,
        "failed_users": failures,
    }


@mcp.tool()
async def bulk_update_user_attributes(
    user_ids: List[str],
    attributes: Dict[str, List[str]],
    merge: bool = True,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update attributes for multiple users in bulk.

    Args:
        user_ids: List of user IDs
        attributes: Attributes to set (format: {"attr_name": ["value1", "value2"]})
        merge: If True, merge with existing attributes; if False, replace all attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Summary of success and failures
    """
    successes = []
    failures = []

    for user_id in user_ids:
        try:
            # Get current user
            user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

            # Update attributes
            if merge:
                current_attrs = user.get("attributes", {})
                current_attrs.update(attributes)
                user["attributes"] = current_attrs
            else:
                user["attributes"] = attributes

            await client._make_request("PUT", f"/users/{user_id}", data=user, realm=realm)
            successes.append(user_id)
        except Exception as e:
            failures.append({"user_id": user_id, "error": str(e)})

    return {
        "status": "completed",
        "total": len(user_ids),
        "successes": len(successes),
        "failures": len(failures),
        "success_ids": successes,
        "failed_users": failures,
    }


@mcp.tool()
async def bulk_add_required_actions(
    user_ids: List[str], actions: List[str], realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add required actions to multiple users in bulk.

    Args:
        user_ids: List of user IDs
        actions: List of required action names to add
        realm: Target realm (uses default if not specified)

    Returns:
        Summary of success and failures
    """
    successes = []
    failures = []

    for user_id in user_ids:
        try:
            # Get current user
            user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

            # Add required actions
            current_actions = set(user.get("requiredActions", []))
            current_actions.update(actions)
            user["requiredActions"] = list(current_actions)

            await client._make_request("PUT", f"/users/{user_id}", data=user, realm=realm)
            successes.append(user_id)
        except Exception as e:
            failures.append({"user_id": user_id, "error": str(e)})

    return {
        "status": "completed",
        "total": len(user_ids),
        "successes": len(successes),
        "failures": len(failures),
        "success_ids": successes,
        "failed_users": failures,
    }
