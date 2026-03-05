from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def get_user_profile(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the declarative user profile configuration for the realm (UPConfig).

    Returns the full user profile schema including all attribute definitions,
    validators, permissions, groups, and the unmanaged attribute policy.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        UPConfig object with the following structure:
        - unmanagedAttributePolicy: "DISABLED" | "ENABLED" | "ADMIN_VIEW" | "ADMIN_EDIT"
        - attributes: list of attribute definitions (name, displayName, validations,
          permissions, required, multivalued, annotations, group)
        - groups: list of attribute groups (name, displayHeader, annotations)
    """
    return await client._make_request("GET", "/users/profile", realm=realm)


@mcp.tool()
async def update_user_profile(
    profile_config: Dict[str, Any],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update the declarative user profile configuration for the realm.

    Shallow-merges the provided profile_config with the current configuration,
    so you only need to supply the top-level keys you want to change. To replace
    the full configuration, include all keys in profile_config.

    Args:
        profile_config: Partial or full UPConfig dict. Supported top-level keys:
            - unmanagedAttributePolicy (str): Policy for attributes not declared in
              the profile. One of:
                "DISABLED"    — unknown attributes are rejected (default)
                "ENABLED"     — unknown attributes are allowed for all users
                "ADMIN_VIEW"  — unknown attributes visible to admins only
                "ADMIN_EDIT"  — unknown attributes editable by admins only
            - attributes (list): Attribute definition objects. Each entry supports:
                - name (str, required): Attribute name
                - displayName (str): Human-readable label
                - multivalued (bool): Allow multiple values
                - group (str): Attribute group name
                - required (dict): {"roles": [...], "scopes": [...]}
                - permissions (dict): {"view": [...], "edit": [...]}
                  Role values: "user", "admin"
                - validations (dict): Validator name → options, e.g.
                    {"length": {"min": 1, "max": 255}, "email": {}}
                - annotations (dict): Arbitrary key-value metadata
            - groups (list): Attribute group objects. Each entry supports:
                - name (str, required): Group name
                - displayHeader (str): Group heading shown in UI
                - displayDescription (str): Group description
                - annotations (dict): Arbitrary key-value metadata
        realm: Target realm (uses default if not specified)

    Returns:
        Status message

    Example — enable unmanaged attributes for admins only:
        update_user_profile({"unmanagedAttributePolicy": "ADMIN_EDIT"})

    Example — add a custom attribute:
        update_user_profile({
            "attributes": [
                *existing_attributes,
                {
                    "name": "department",
                    "displayName": "Department",
                    "permissions": {"view": ["admin", "user"], "edit": ["admin"]},
                    "validations": {"length": {"max": 128}}
                }
            ]
        })
    """
    # Get current config and shallow-merge so unspecified keys are preserved
    current = await client._make_request("GET", "/users/profile", realm=realm)
    current.update(profile_config)

    await client._make_request("PUT", "/users/profile", data=current, realm=realm)
    return {
        "status": "updated",
        "message": f"User profile configuration updated successfully for realm "
                   f"'{realm or client.realm_name}'",
    }


@mcp.tool()
async def get_user_profile_metadata(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get user profile metadata for the realm.

    Returns the metadata representation of the user profile, which includes
    attribute metadata (display name, validators, annotations, required status,
    read-only status) as seen by the current caller. This is the read-only view
    used by account consoles and clients, as opposed to the full admin UPConfig
    returned by get_user_profile.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        UserProfileMetadata object containing:
        - attributes: list of UserProfileAttributeMetadata objects with
          name, displayName, required, readOnly, validators, annotations
        - groups: list of UserProfileAttributeGroupMetadata objects
    """
    return await client._make_request("GET", "/users/profile/metadata", realm=realm)
