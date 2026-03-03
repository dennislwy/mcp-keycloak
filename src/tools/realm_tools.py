from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def get_accessible_realms() -> List[Dict[str, Any]]:
    """
    Get accessible realms.

    Returns:
        List of accessible realms
    """
    return await client._make_request("GET", "/realms", skip_realm=True)


@mcp.tool()
async def get_realm_info(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about the current realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Realm configuration object
    """
    response = await client._make_request("GET", "", params=None, realm=realm)
    return response


@mcp.tool()
async def update_realm_settings(
    display_name: Optional[str] = None,
    display_name_html: Optional[str] = None,
    login_theme: Optional[str] = None,
    account_theme: Optional[str] = None,
    admin_theme: Optional[str] = None,
    email_theme: Optional[str] = None,
    enabled: Optional[bool] = None,
    registration_allowed: Optional[bool] = None,
    registration_email_as_username: Optional[bool] = None,
    reset_password_allowed: Optional[bool] = None,
    remember_me: Optional[bool] = None,
    verify_email: Optional[bool] = None,
    login_with_email_allowed: Optional[bool] = None,
    duplicate_emails_allowed: Optional[bool] = None,
    ssl_required: Optional[str] = None,
    brute_force_protected: Optional[bool] = None,
    permanent_lockout: Optional[bool] = None,
    max_failure_wait_seconds: Optional[int] = None,
    minimum_quick_login_wait_seconds: Optional[int] = None,
    wait_increment_seconds: Optional[int] = None,
    quick_login_check_milli_seconds: Optional[int] = None,
    max_delta_time_seconds: Optional[int] = None,
    failure_factor: Optional[int] = None,
    default_locale: Optional[str] = None,
    # Authentication flow bindings
    browser_flow: Optional[str] = None,
    registration_flow: Optional[str] = None,
    direct_grant_flow: Optional[str] = None,
    reset_credentials_flow: Optional[str] = None,
    client_authentication_flow: Optional[str] = None,
    docker_authentication_flow: Optional[str] = None,
    # OTP policy (for passwordless TOTP flows)
    otp_policy_type: Optional[str] = None,
    otp_policy_algorithm: Optional[str] = None,
    otp_policy_digits: Optional[int] = None,
    otp_policy_look_ahead_window: Optional[int] = None,
    otp_policy_period: Optional[int] = None,
    otp_policy_initial_counter: Optional[int] = None,
    # WebAuthn Passwordless policy (for Passkeys flows)
    webauthn_passwordless_policy_rp_entity_name: Optional[str] = None,
    webauthn_passwordless_policy_signature_algorithms: Optional[List[str]] = None,
    webauthn_passwordless_policy_rp_id: Optional[str] = None,
    webauthn_passwordless_policy_attestation_conveyance_preference: Optional[str] = None,
    webauthn_passwordless_policy_authenticator_attachment: Optional[str] = None,
    webauthn_passwordless_policy_require_resident_key: Optional[str] = None,
    webauthn_passwordless_policy_user_verification_requirement: Optional[str] = None,
    webauthn_passwordless_policy_create_timeout: Optional[int] = None,
    webauthn_passwordless_policy_avoid_same_authenticator_register: Optional[bool] = None,
    webauthn_passwordless_policy_acceptable_aaguids: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update realm settings.

    Args:
        display_name: Display name for the realm
        display_name_html: HTML display name
        login_theme: Login theme name
        account_theme: Account management theme
        admin_theme: Admin console theme
        email_theme: Email theme
        enabled: Whether realm is enabled
        registration_allowed: Allow user registration
        registration_email_as_username: Use email as username
        reset_password_allowed: Allow password reset
        remember_me: Enable remember me
        verify_email: Require email verification
        login_with_email_allowed: Allow login with email
        duplicate_emails_allowed: Allow duplicate emails
        ssl_required: SSL requirement (none, external, all)
        brute_force_protected: Enable brute force protection
        permanent_lockout: Permanent lockout on max failures
        max_failure_wait_seconds: Max wait after failures
        minimum_quick_login_wait_seconds: Min wait between quick logins
        wait_increment_seconds: Wait increment
        quick_login_check_milli_seconds: Quick login check interval
        max_delta_time_seconds: Max time between failures
        failure_factor: Failure factor
        default_locale: Default locale
        browser_flow: Alias of the flow bound to the browser login (e.g. 'browser-passwordless-totp')
        registration_flow: Alias of the flow bound to user registration
        direct_grant_flow: Alias of the flow bound to direct grant
        reset_credentials_flow: Alias of the flow bound to reset credentials
        client_authentication_flow: Alias of the flow bound to client authentication
        docker_authentication_flow: Alias of the flow bound to Docker authentication
        otp_policy_type: OTP type — 'totp' (time-based) or 'hotp' (counter-based)
        otp_policy_algorithm: HMAC algorithm — 'HmacSHA1', 'HmacSHA256', or 'HmacSHA512'
        otp_policy_digits: Number of OTP digits (6 or 8)
        otp_policy_look_ahead_window: Number of intervals to check before/after current (handles clock drift)
        otp_policy_period: TOTP token validity period in seconds (typically 30)
        otp_policy_initial_counter: Initial counter value for HOTP (ignored for TOTP)
        webauthn_passwordless_policy_rp_entity_name: Relying Party display name shown during registration
        webauthn_passwordless_policy_signature_algorithms: List of allowed signature algorithms e.g. ['ES256', 'RS256']
        webauthn_passwordless_policy_rp_id: Relying Party ID (domain); leave empty to auto-detect from origin
        webauthn_passwordless_policy_attestation_conveyance_preference: 'none', 'indirect', or 'direct'
        webauthn_passwordless_policy_authenticator_attachment: 'platform' (built-in), 'cross-platform' (roaming), or '' (both)
        webauthn_passwordless_policy_require_resident_key: 'Yes' or 'No' — required for true passwordless (discoverable credentials)
        webauthn_passwordless_policy_user_verification_requirement: 'required', 'preferred', or 'discouraged'
        webauthn_passwordless_policy_create_timeout: Registration ceremony timeout in seconds (0 = browser default)
        webauthn_passwordless_policy_avoid_same_authenticator_register: Prevent registering the same authenticator twice
        webauthn_passwordless_policy_acceptable_aaguids: List of allowed authenticator AAGUIDs; empty list = accept all
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current realm data
    current_realm = await client._make_request("GET", "", realm=realm)

    # Update only provided fields
    if display_name is not None:
        current_realm["displayName"] = display_name
    if display_name_html is not None:
        current_realm["displayNameHtml"] = display_name_html
    if login_theme is not None:
        current_realm["loginTheme"] = login_theme
    if account_theme is not None:
        current_realm["accountTheme"] = account_theme
    if admin_theme is not None:
        current_realm["adminTheme"] = admin_theme
    if email_theme is not None:
        current_realm["emailTheme"] = email_theme
    if enabled is not None:
        current_realm["enabled"] = enabled
    if registration_allowed is not None:
        current_realm["registrationAllowed"] = registration_allowed
    if registration_email_as_username is not None:
        current_realm["registrationEmailAsUsername"] = registration_email_as_username
    if reset_password_allowed is not None:
        current_realm["resetPasswordAllowed"] = reset_password_allowed
    if remember_me is not None:
        current_realm["rememberMe"] = remember_me
    if verify_email is not None:
        current_realm["verifyEmail"] = verify_email
    if login_with_email_allowed is not None:
        current_realm["loginWithEmailAllowed"] = login_with_email_allowed
    if duplicate_emails_allowed is not None:
        current_realm["duplicateEmailsAllowed"] = duplicate_emails_allowed
    if ssl_required is not None:
        current_realm["sslRequired"] = ssl_required
    if brute_force_protected is not None:
        current_realm["bruteForceProtected"] = brute_force_protected
    if permanent_lockout is not None:
        current_realm["permanentLockout"] = permanent_lockout
    if max_failure_wait_seconds is not None:
        current_realm["maxFailureWaitSeconds"] = max_failure_wait_seconds
    if minimum_quick_login_wait_seconds is not None:
        current_realm["minimumQuickLoginWaitSeconds"] = minimum_quick_login_wait_seconds
    if wait_increment_seconds is not None:
        current_realm["waitIncrementSeconds"] = wait_increment_seconds
    if quick_login_check_milli_seconds is not None:
        current_realm["quickLoginCheckMilliSeconds"] = quick_login_check_milli_seconds
    if max_delta_time_seconds is not None:
        current_realm["maxDeltaTimeSeconds"] = max_delta_time_seconds
    if failure_factor is not None:
        current_realm["failureFactor"] = failure_factor
    if default_locale is not None:
        current_realm["defaultLocale"] = default_locale

    # Authentication flow bindings
    if browser_flow is not None:
        current_realm["browserFlow"] = browser_flow
    if registration_flow is not None:
        current_realm["registrationFlow"] = registration_flow
    if direct_grant_flow is not None:
        current_realm["directGrantFlow"] = direct_grant_flow
    if reset_credentials_flow is not None:
        current_realm["resetCredentialsFlow"] = reset_credentials_flow
    if client_authentication_flow is not None:
        current_realm["clientAuthenticationFlow"] = client_authentication_flow
    if docker_authentication_flow is not None:
        current_realm["dockerAuthenticationFlow"] = docker_authentication_flow

    # OTP policy
    if otp_policy_type is not None:
        current_realm["otpPolicyType"] = otp_policy_type
    if otp_policy_algorithm is not None:
        current_realm["otpPolicyAlgorithm"] = otp_policy_algorithm
    if otp_policy_digits is not None:
        current_realm["otpPolicyDigits"] = otp_policy_digits
    if otp_policy_look_ahead_window is not None:
        current_realm["otpPolicyLookAheadWindow"] = otp_policy_look_ahead_window
    if otp_policy_period is not None:
        current_realm["otpPolicyPeriod"] = otp_policy_period
    if otp_policy_initial_counter is not None:
        current_realm["otpPolicyInitialCounter"] = otp_policy_initial_counter

    # WebAuthn Passwordless policy
    if webauthn_passwordless_policy_rp_entity_name is not None:
        current_realm["webAuthnPolicyPasswordlessRpEntityName"] = webauthn_passwordless_policy_rp_entity_name
    if webauthn_passwordless_policy_signature_algorithms is not None:
        current_realm["webAuthnPolicyPasswordlessSignatureAlgorithms"] = webauthn_passwordless_policy_signature_algorithms
    if webauthn_passwordless_policy_rp_id is not None:
        current_realm["webAuthnPolicyPasswordlessRpId"] = webauthn_passwordless_policy_rp_id
    if webauthn_passwordless_policy_attestation_conveyance_preference is not None:
        current_realm["webAuthnPolicyPasswordlessAttestationConveyancePreference"] = webauthn_passwordless_policy_attestation_conveyance_preference
    if webauthn_passwordless_policy_authenticator_attachment is not None:
        current_realm["webAuthnPolicyPasswordlessAuthenticatorAttachment"] = webauthn_passwordless_policy_authenticator_attachment
    if webauthn_passwordless_policy_require_resident_key is not None:
        current_realm["webAuthnPolicyPasswordlessRequireResidentKey"] = webauthn_passwordless_policy_require_resident_key
    if webauthn_passwordless_policy_user_verification_requirement is not None:
        current_realm["webAuthnPolicyPasswordlessUserVerificationRequirement"] = webauthn_passwordless_policy_user_verification_requirement
    if webauthn_passwordless_policy_create_timeout is not None:
        current_realm["webAuthnPolicyPasswordlessCreateTimeout"] = webauthn_passwordless_policy_create_timeout
    if webauthn_passwordless_policy_avoid_same_authenticator_register is not None:
        current_realm["webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister"] = webauthn_passwordless_policy_avoid_same_authenticator_register
    if webauthn_passwordless_policy_acceptable_aaguids is not None:
        current_realm["webAuthnPolicyPasswordlessAcceptableAaguids"] = webauthn_passwordless_policy_acceptable_aaguids

    await client._make_request("PUT", "", data=current_realm, realm=realm)
    return {
        "status": "updated",
        "message": f"Realm {realm if realm else client.realm_name} settings updated successfully",
    }


@mcp.tool()
async def update_realm_settings_advanced(
    realm_representation: Dict[str, Any],
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update a realm with full control using a raw RealmRepresentation object.

    This is a power-user tool for updating realm properties not exposed by
    update_realm_settings. The provided realm_representation is merged (shallow)
    with the current realm configuration, so you only need to include the fields
    you want to change.

    Args:
        realm_representation: Partial or full RealmRepresentation dict. Only the
            keys present in this dict will overwrite existing values; all other
            realm fields remain unchanged.
        realm: Target realm (uses default if not specified)

    Returns:
        Status message

    Example realm_representation values:

        Set browser flow binding:
            {"browserFlow": "browser-passwordless-totp"}

        Configure OTP policy:
            {
                "otpPolicyType": "totp",
                "otpPolicyAlgorithm": "HmacSHA1",
                "otpPolicyDigits": 6,
                "otpPolicyLookAheadWindow": 1,
                "otpPolicyPeriod": 30
            }

        Configure WebAuthn Passwordless policy:
            {
                "webAuthnPolicyPasswordlessRpEntityName": "GSF Account",
                "webAuthnPolicyPasswordlessSignatureAlgorithms": ["ES256", "RS256"],
                "webAuthnPolicyPasswordlessRequireResidentKey": "Yes",
                "webAuthnPolicyPasswordlessUserVerificationRequirement": "preferred",
                "webAuthnPolicyPasswordlessAttestationConveyancePreference": "none",
                "webAuthnPolicyPasswordlessAuthenticatorAttachment": "platform",
                "webAuthnPolicyPasswordlessCreateTimeout": 0,
                "webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister": true,
                "webAuthnPolicyPasswordlessAcceptableAaguids": []
            }

    See the full RealmRepresentation schema at:
    https://www.keycloak.org/docs-api/latest/rest-api/index.html#RealmRepresentation
    """
    # Get current realm data
    current_realm = await client._make_request("GET", "", realm=realm)

    # Merge: provided fields overwrite current values; unspecified fields are preserved
    current_realm.update(realm_representation)

    await client._make_request("PUT", "", data=current_realm, realm=realm)
    return {
        "status": "updated",
        "message": f"Realm {realm if realm else client.realm_name} updated successfully with advanced configuration",
    }


@mcp.tool()
async def get_realm_events_config(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get realm events configuration.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Events configuration object
    """
    return await client._make_request("GET", "/events/config", realm=realm)


@mcp.tool()
async def update_realm_events_config(
    events_enabled: Optional[bool] = None,
    events_listeners: Optional[List[str]] = None,
    enabled_event_types: Optional[List[str]] = None,
    admin_events_enabled: Optional[bool] = None,
    admin_events_details_enabled: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update realm events configuration.

    Args:
        events_enabled: Enable events
        events_listeners: Event listener implementations
        enabled_event_types: Types of events to record
        admin_events_enabled: Enable admin events
        admin_events_details_enabled: Include details in admin events
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # Get current config
    current_config = await client._make_request("GET", "/events/config", realm=realm)

    # Update only provided fields
    if events_enabled is not None:
        current_config["eventsEnabled"] = events_enabled
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
    return {"status": "updated", "message": "Events configuration updated successfully"}


@mcp.tool()
async def get_realm_default_groups(realm: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get default groups for the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of default groups
    """
    return await client._make_request("GET", "/default-groups", realm=realm)


@mcp.tool()
async def add_realm_default_group(
    group_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Add a default group to the realm.

    Args:
        group_id: Group ID to add as default
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("PUT", f"/default-groups/{group_id}", realm=realm)
    return {"status": "added", "message": f"Group {group_id} added as default group"}


@mcp.tool()
async def remove_realm_default_group(
    group_id: str, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Remove a default group from the realm.

    Args:
        group_id: Group ID to remove from defaults
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/default-groups/{group_id}", realm=realm)
    return {
        "status": "removed",
        "message": f"Group {group_id} removed from default groups",
    }


@mcp.tool()
async def remove_all_user_sessions(realm: Optional[str] = None) -> Dict[str, str]:
    """
    Remove all sessions for all users in the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("POST", "/logout-all", realm=realm)
    return {
        "status": "removed",
        "message": "Sessions for all users removed successfully",
    }
