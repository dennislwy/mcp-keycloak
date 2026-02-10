"""
Keycloak Security Policies & Configuration Management Tools

This module provides comprehensive tools for managing Keycloak security policies and configurations
including password policies, OTP policies, WebAuthn policies, SMTP configuration, and browser
security headers.

Phase 2.5: Security Policies & Configuration
- Password policy configuration (length, complexity, history, age)
- OTP policy settings (algorithm, digits, period, window)
- WebAuthn policy configuration (regular and passwordless)
- Browser security headers configuration
- SMTP server configuration and testing
- Realm security settings (SSL required, brute force protection)
- Configure realm attributes
- Default roles for new users
"""

from typing import Dict, Any, List, Optional
from ..common.server import mcp
from .keycloak_client import KeycloakClient

client = KeycloakClient()


@mcp.tool()
async def get_password_policy(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current password policy configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing password policy configuration with parsed rules
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    password_policy = realm_info.get("passwordPolicy", "")

    # Parse password policy string into components
    parsed_policy = {}
    if password_policy:
        policies = password_policy.split(" and ")
        for policy in policies:
            if "(" in policy and policy.endswith(")"):
                # Policy with parameter like "length(8)"
                name, param = policy.split("(", 1)
                param = param.rstrip(")")
                if param.isdigit():
                    parsed_policy[name] = int(param)
                else:
                    parsed_policy[name] = param
            else:
                # Simple policy like "upperCase"
                parsed_policy[policy] = True

    return {
        "passwordPolicyString": password_policy,
        "parsedPolicy": parsed_policy,
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def update_password_policy(
    length: Optional[int] = None,
    digits: Optional[int] = None,
    lower_case: Optional[bool] = None,
    upper_case: Optional[bool] = None,
    special_chars: Optional[int] = None,
    not_username: Optional[bool] = None,
    not_email: Optional[bool] = None,
    regex_pattern: Optional[str] = None,
    password_history: Optional[int] = None,
    force_expired_password_change: Optional[int] = None,
    hash_iterations: Optional[int] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update the password policy configuration for a realm.

    Args:
        length: Minimum password length
        digits: Minimum number of digits required
        lower_case: Require lowercase characters
        upper_case: Require uppercase characters
        special_chars: Minimum number of special characters
        not_username: Password must not be same as username
        not_email: Password must not be same as email
        regex_pattern: Custom regex pattern for password validation
        password_history: Number of previous passwords to remember
        force_expired_password_change: Days after which password expires
        hash_iterations: Number of hash iterations for password storage
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated password policy configuration
    """
    # Build password policy string
    policy_parts = []

    if length is not None:
        policy_parts.append(f"length({length})")

    if digits is not None:
        policy_parts.append(f"digits({digits})")

    if lower_case:
        policy_parts.append("lowerCase")

    if upper_case:
        policy_parts.append("upperCase")

    if special_chars is not None:
        policy_parts.append(f"specialChars({special_chars})")

    if not_username:
        policy_parts.append("notUsername")

    if not_email:
        policy_parts.append("notEmail")

    if regex_pattern:
        policy_parts.append(f"regexPattern({regex_pattern})")

    if password_history is not None:
        policy_parts.append(f"passwordHistory({password_history})")

    if force_expired_password_change is not None:
        policy_parts.append(
            f"forceExpiredPasswordChange({force_expired_password_change})"
        )

    if hash_iterations is not None:
        policy_parts.append(f"hashIterations({hash_iterations})")

    password_policy = " and ".join(policy_parts)

    # Update realm with new password policy
    update_data = {"passwordPolicy": password_policy}

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_password_policy(realm=realm)


@mcp.tool()
async def get_otp_policy(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current OTP (One-Time Password) policy configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing OTP policy configuration
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    otp_policy = {
        "otpPolicyType": realm_info.get("otpPolicyType", "totp"),
        "otpPolicyAlgorithm": realm_info.get("otpPolicyAlgorithm", "HmacSHA1"),
        "otpPolicyInitialCounter": realm_info.get("otpPolicyInitialCounter", 0),
        "otpPolicyDigits": realm_info.get("otpPolicyDigits", 6),
        "otpPolicyLookAheadWindow": realm_info.get("otpPolicyLookAheadWindow", 1),
        "otpPolicyPeriod": realm_info.get("otpPolicyPeriod", 30),
        "otpPolicyCodeReusable": realm_info.get("otpPolicyCodeReusable", False),
        "otpSupportedApplications": realm_info.get("otpSupportedApplications", []),
        "realm": realm or client.realm_name,
    }

    return otp_policy


@mcp.tool()
async def update_otp_policy(
    otp_type: Optional[str] = None,
    algorithm: Optional[str] = None,
    digits: Optional[int] = None,
    period: Optional[int] = None,
    initial_counter: Optional[int] = None,
    look_ahead_window: Optional[int] = None,
    code_reusable: Optional[bool] = None,
    supported_applications: Optional[List[str]] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update the OTP (One-Time Password) policy configuration for a realm.

    Args:
        otp_type: Type of OTP (totp or hotp)
        algorithm: Hash algorithm (HmacSHA1, HmacSHA256, HmacSHA512)
        digits: Number of digits in OTP code (6 or 8)
        period: Time period for TOTP in seconds (default 30)
        initial_counter: Initial counter for HOTP (default 0)
        look_ahead_window: Look ahead window for validation (default 1)
        code_reusable: Whether OTP codes can be reused
        supported_applications: List of supported OTP applications
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated OTP policy configuration
    """
    update_data = {}

    if otp_type is not None:
        if otp_type not in ["totp", "hotp"]:
            raise ValueError("otp_type must be 'totp' or 'hotp'")
        update_data["otpPolicyType"] = otp_type

    if algorithm is not None:
        if algorithm not in ["HmacSHA1", "HmacSHA256", "HmacSHA512"]:
            raise ValueError(
                "algorithm must be one of: HmacSHA1, HmacSHA256, HmacSHA512"
            )
        update_data["otpPolicyAlgorithm"] = algorithm

    if digits is not None:
        if digits not in [6, 8]:
            raise ValueError("digits must be 6 or 8")
        update_data["otpPolicyDigits"] = digits

    if period is not None:
        update_data["otpPolicyPeriod"] = period

    if initial_counter is not None:
        update_data["otpPolicyInitialCounter"] = initial_counter

    if look_ahead_window is not None:
        update_data["otpPolicyLookAheadWindow"] = look_ahead_window

    if code_reusable is not None:
        update_data["otpPolicyCodeReusable"] = code_reusable

    if supported_applications is not None:
        update_data["otpSupportedApplications"] = supported_applications

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_otp_policy(realm=realm)


@mcp.tool()
async def get_webauthn_policy(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current WebAuthn policy configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing WebAuthn policy configuration for both regular and passwordless
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    webauthn_policy = {
        "regular": {
            "rpEntityName": realm_info.get("webAuthnPolicyRpEntityName"),
            "signatureAlgorithms": realm_info.get(
                "webAuthnPolicySignatureAlgorithms", []
            ),
            "rpId": realm_info.get("webAuthnPolicyRpId"),
            "attestationConveyancePreference": realm_info.get(
                "webAuthnPolicyAttestationConveyancePreference"
            ),
            "authenticatorAttachment": realm_info.get(
                "webAuthnPolicyAuthenticatorAttachment"
            ),
            "requireResidentKey": realm_info.get("webAuthnPolicyRequireResidentKey"),
            "userVerificationRequirement": realm_info.get(
                "webAuthnPolicyUserVerificationRequirement"
            ),
            "createTimeout": realm_info.get("webAuthnPolicyCreateTimeout"),
            "avoidSameAuthenticatorRegister": realm_info.get(
                "webAuthnPolicyAvoidSameAuthenticatorRegister"
            ),
            "acceptableAaguids": realm_info.get("webAuthnPolicyAcceptableAaguids", []),
            "extraOrigins": realm_info.get("webAuthnPolicyExtraOrigins", []),
        },
        "passwordless": {
            "rpEntityName": realm_info.get("webAuthnPolicyPasswordlessRpEntityName"),
            "signatureAlgorithms": realm_info.get(
                "webAuthnPolicyPasswordlessSignatureAlgorithms", []
            ),
            "rpId": realm_info.get("webAuthnPolicyPasswordlessRpId"),
            "attestationConveyancePreference": realm_info.get(
                "webAuthnPolicyPasswordlessAttestationConveyancePreference"
            ),
            "authenticatorAttachment": realm_info.get(
                "webAuthnPolicyPasswordlessAuthenticatorAttachment"
            ),
            "requireResidentKey": realm_info.get(
                "webAuthnPolicyPasswordlessRequireResidentKey"
            ),
            "userVerificationRequirement": realm_info.get(
                "webAuthnPolicyPasswordlessUserVerificationRequirement"
            ),
            "createTimeout": realm_info.get("webAuthnPolicyPasswordlessCreateTimeout"),
            "avoidSameAuthenticatorRegister": realm_info.get(
                "webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister"
            ),
            "acceptableAaguids": realm_info.get(
                "webAuthnPolicyPasswordlessAcceptableAaguids", []
            ),
            "extraOrigins": realm_info.get(
                "webAuthnPolicyPasswordlessExtraOrigins", []
            ),
            "passkeysEnabled": realm_info.get(
                "webAuthnPolicyPasswordlessPasskeysEnabled"
            ),
        },
        "realm": realm or client.realm_name,
    }

    return webauthn_policy


@mcp.tool()
async def update_webauthn_policy(
    policy_type: str,
    rp_entity_name: Optional[str] = None,
    signature_algorithms: Optional[List[str]] = None,
    rp_id: Optional[str] = None,
    attestation_conveyance_preference: Optional[str] = None,
    authenticator_attachment: Optional[str] = None,
    require_resident_key: Optional[str] = None,
    user_verification_requirement: Optional[str] = None,
    create_timeout: Optional[int] = None,
    avoid_same_authenticator_register: Optional[bool] = None,
    acceptable_aaguids: Optional[List[str]] = None,
    extra_origins: Optional[List[str]] = None,
    passkeys_enabled: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update WebAuthn policy configuration for a realm.

    Args:
        policy_type: Type of WebAuthn policy ('regular' or 'passwordless')
        rp_entity_name: Relying Party entity name
        signature_algorithms: List of signature algorithms (e.g., ['ES256', 'RS256'])
        rp_id: Relying Party ID (usually domain name)
        attestation_conveyance_preference: Attestation conveyance preference (none, indirect, direct)
        authenticator_attachment: Authenticator attachment (platform, cross-platform)
        require_resident_key: Resident key requirement (discouraged, preferred, required)
        user_verification_requirement: User verification requirement (discouraged, preferred, required)
        create_timeout: Timeout for credential creation in milliseconds
        avoid_same_authenticator_register: Whether to avoid registering same authenticator
        acceptable_aaguids: List of acceptable Authenticator Attestation GUIDs
        extra_origins: List of extra origins for WebAuthn
        passkeys_enabled: Whether passkeys are enabled (only for passwordless)
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated WebAuthn policy configuration
    """
    if policy_type not in ["regular", "passwordless"]:
        raise ValueError("policy_type must be 'regular' or 'passwordless'")

    prefix = (
        "webAuthnPolicyPasswordless"
        if policy_type == "passwordless"
        else "webAuthnPolicy"
    )

    update_data = {}

    if rp_entity_name is not None:
        update_data[f"{prefix}RpEntityName"] = rp_entity_name

    if signature_algorithms is not None:
        update_data[f"{prefix}SignatureAlgorithms"] = signature_algorithms

    if rp_id is not None:
        update_data[f"{prefix}RpId"] = rp_id

    if attestation_conveyance_preference is not None:
        update_data[f"{prefix}AttestationConveyancePreference"] = (
            attestation_conveyance_preference
        )

    if authenticator_attachment is not None:
        update_data[f"{prefix}AuthenticatorAttachment"] = authenticator_attachment

    if require_resident_key is not None:
        update_data[f"{prefix}RequireResidentKey"] = require_resident_key

    if user_verification_requirement is not None:
        update_data[f"{prefix}UserVerificationRequirement"] = (
            user_verification_requirement
        )

    if create_timeout is not None:
        update_data[f"{prefix}CreateTimeout"] = create_timeout

    if avoid_same_authenticator_register is not None:
        update_data[f"{prefix}AvoidSameAuthenticatorRegister"] = (
            avoid_same_authenticator_register
        )

    if acceptable_aaguids is not None:
        update_data[f"{prefix}AcceptableAaguids"] = acceptable_aaguids

    if extra_origins is not None:
        update_data[f"{prefix}ExtraOrigins"] = extra_origins

    if policy_type == "passwordless" and passkeys_enabled is not None:
        update_data[f"{prefix}PasskeysEnabled"] = passkeys_enabled

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_webauthn_policy(realm=realm)


@mcp.tool()
async def get_browser_security_headers(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current browser security headers configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing browser security headers configuration
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    return {
        "browserSecurityHeaders": realm_info.get("browserSecurityHeaders", {}),
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def update_browser_security_headers(
    content_security_policy: Optional[str] = None,
    content_security_policy_report_only: Optional[str] = None,
    x_content_type_options: Optional[str] = None,
    x_frame_options: Optional[str] = None,
    x_robots_tag: Optional[str] = None,
    x_xss_protection: Optional[str] = None,
    strict_transport_security: Optional[str] = None,
    referrer_policy: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update browser security headers configuration for a realm.

    Args:
        content_security_policy: Content Security Policy header
        content_security_policy_report_only: CSP report-only header
        x_content_type_options: X-Content-Type-Options header (typically "nosniff")
        x_frame_options: X-Frame-Options header (DENY, SAMEORIGIN, ALLOW-FROM)
        x_robots_tag: X-Robots-Tag header
        x_xss_protection: X-XSS-Protection header
        strict_transport_security: Strict-Transport-Security header
        referrer_policy: Referrer-Policy header
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated browser security headers configuration
    """
    headers_config = {}

    if content_security_policy is not None:
        headers_config["contentSecurityPolicy"] = content_security_policy

    if content_security_policy_report_only is not None:
        headers_config["contentSecurityPolicyReportOnly"] = (
            content_security_policy_report_only
        )

    if x_content_type_options is not None:
        headers_config["xContentTypeOptions"] = x_content_type_options

    if x_frame_options is not None:
        headers_config["xFrameOptions"] = x_frame_options

    if x_robots_tag is not None:
        headers_config["xRobotsTag"] = x_robots_tag

    if x_xss_protection is not None:
        headers_config["xXSSProtection"] = x_xss_protection

    if strict_transport_security is not None:
        headers_config["strictTransportSecurity"] = strict_transport_security

    if referrer_policy is not None:
        headers_config["referrerPolicy"] = referrer_policy

    update_data = {"browserSecurityHeaders": headers_config}

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_browser_security_headers(realm=realm)


@mcp.tool()
async def get_smtp_configuration(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current SMTP server configuration for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing SMTP configuration (passwords are masked for security)
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    smtp_config = realm_info.get("smtpServer", {}).copy()

    # Mask password for security
    if "password" in smtp_config:
        smtp_config["password"] = "***masked***"

    return {"smtpServer": smtp_config, "realm": realm or client.realm_name}


@mcp.tool()
async def update_smtp_configuration(
    host: Optional[str] = None,
    port: Optional[str] = None,
    from_email: Optional[str] = None,
    from_display_name: Optional[str] = None,
    reply_to: Optional[str] = None,
    reply_to_display_name: Optional[str] = None,
    envelope_from: Optional[str] = None,
    ssl: Optional[bool] = None,
    starttls: Optional[bool] = None,
    auth: Optional[bool] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update SMTP server configuration for a realm.

    Args:
        host: SMTP server hostname
        port: SMTP server port (typically 25, 465, 587)
        from_email: From email address
        from_display_name: Display name for from email
        reply_to: Reply-to email address
        reply_to_display_name: Display name for reply-to email
        envelope_from: Envelope from email address
        ssl: Enable SSL/TLS encryption
        starttls: Enable STARTTLS
        auth: Enable SMTP authentication
        user: SMTP username
        password: SMTP password
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated SMTP configuration (password masked)
    """
    smtp_config = {}

    if host is not None:
        smtp_config["host"] = host

    if port is not None:
        smtp_config["port"] = str(port)

    if from_email is not None:
        smtp_config["from"] = from_email

    if from_display_name is not None:
        smtp_config["fromDisplayName"] = from_display_name

    if reply_to is not None:
        smtp_config["replyTo"] = reply_to

    if reply_to_display_name is not None:
        smtp_config["replyToDisplayName"] = reply_to_display_name

    if envelope_from is not None:
        smtp_config["envelopeFrom"] = envelope_from

    if ssl is not None:
        smtp_config["ssl"] = str(ssl).lower()

    if starttls is not None:
        smtp_config["starttls"] = str(starttls).lower()

    if auth is not None:
        smtp_config["auth"] = str(auth).lower()

    if user is not None:
        smtp_config["user"] = user

    if password is not None:
        smtp_config["password"] = password

    update_data = {"smtpServer": smtp_config}

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_smtp_configuration(realm=realm)


@mcp.tool()
async def test_smtp_connection(
    test_email: str, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test SMTP connection by sending a test email.

    Args:
        test_email: Email address to send test email to
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary indicating success or failure of SMTP test
    """
    try:
        await client._make_request(
            "POST", "/testSMTPConnection", data={"email": test_email}, realm=realm
        )

        return {
            "success": True,
            "message": f"Test email sent successfully to {test_email}",
            "realm": realm or client.realm_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send test email to {test_email}",
            "realm": realm or client.realm_name,
        }


@mcp.tool()
async def get_realm_security_settings(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive security settings for a realm including SSL, brute force protection,
    and other security-related configurations.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing comprehensive security settings
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    security_settings = {
        "sslRequired": realm_info.get("sslRequired", "external"),
        "bruteForceProtected": realm_info.get("bruteForceProtected", False),
        "permanentLockout": realm_info.get("permanentLockout", False),
        "maxTemporaryLockouts": realm_info.get("maxTemporaryLockouts", 0),
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
        "verifyEmail": realm_info.get("verifyEmail", False),
        "loginWithEmailAllowed": realm_info.get("loginWithEmailAllowed", False),
        "duplicateEmailsAllowed": realm_info.get("duplicateEmailsAllowed", False),
        "resetPasswordAllowed": realm_info.get("resetPasswordAllowed", False),
        "editUsernameAllowed": realm_info.get("editUsernameAllowed", False),
        "registrationAllowed": realm_info.get("registrationAllowed", False),
        "registrationEmailAsUsername": realm_info.get(
            "registrationEmailAsUsername", False
        ),
        "rememberMe": realm_info.get("rememberMe", False),
        "realm": realm or client.realm_name,
    }

    return security_settings


@mcp.tool()
async def update_realm_security_settings(
    ssl_required: Optional[str] = None,
    brute_force_protected: Optional[bool] = None,
    permanent_lockout: Optional[bool] = None,
    max_temporary_lockouts: Optional[int] = None,
    max_failure_wait_seconds: Optional[int] = None,
    minimum_quick_login_wait_seconds: Optional[int] = None,
    wait_increment_seconds: Optional[int] = None,
    quick_login_check_milli_seconds: Optional[int] = None,
    max_delta_time_seconds: Optional[int] = None,
    failure_factor: Optional[int] = None,
    verify_email: Optional[bool] = None,
    login_with_email_allowed: Optional[bool] = None,
    duplicate_emails_allowed: Optional[bool] = None,
    reset_password_allowed: Optional[bool] = None,
    edit_username_allowed: Optional[bool] = None,
    registration_allowed: Optional[bool] = None,
    registration_email_as_username: Optional[bool] = None,
    remember_me: Optional[bool] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update comprehensive security settings for a realm.

    Args:
        ssl_required: SSL requirement (none, external, all)
        brute_force_protected: Enable brute force protection
        permanent_lockout: Enable permanent lockout after max temporary lockouts
        max_temporary_lockouts: Maximum temporary lockouts before permanent
        max_failure_wait_seconds: Maximum wait time after failed attempts
        minimum_quick_login_wait_seconds: Minimum wait for quick login detection
        wait_increment_seconds: Increment in wait time for subsequent failures
        quick_login_check_milli_seconds: Time window for quick login detection
        max_delta_time_seconds: Maximum time delta for related events
        failure_factor: Failure factor for brute force calculation
        verify_email: Require email verification
        login_with_email_allowed: Allow login with email address
        duplicate_emails_allowed: Allow duplicate email addresses
        reset_password_allowed: Allow password reset
        edit_username_allowed: Allow username editing
        registration_allowed: Allow user registration
        registration_email_as_username: Use email as username in registration
        remember_me: Enable remember me functionality
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated security settings
    """
    update_data = {}

    if ssl_required is not None:
        if ssl_required not in ["none", "external", "all"]:
            raise ValueError("ssl_required must be one of: none, external, all")
        update_data["sslRequired"] = ssl_required

    if brute_force_protected is not None:
        update_data["bruteForceProtected"] = brute_force_protected

    if permanent_lockout is not None:
        update_data["permanentLockout"] = permanent_lockout

    if max_temporary_lockouts is not None:
        update_data["maxTemporaryLockouts"] = max_temporary_lockouts

    if max_failure_wait_seconds is not None:
        update_data["maxFailureWaitSeconds"] = max_failure_wait_seconds

    if minimum_quick_login_wait_seconds is not None:
        update_data["minimumQuickLoginWaitSeconds"] = minimum_quick_login_wait_seconds

    if wait_increment_seconds is not None:
        update_data["waitIncrementSeconds"] = wait_increment_seconds

    if quick_login_check_milli_seconds is not None:
        update_data["quickLoginCheckMilliSeconds"] = quick_login_check_milli_seconds

    if max_delta_time_seconds is not None:
        update_data["maxDeltaTimeSeconds"] = max_delta_time_seconds

    if failure_factor is not None:
        update_data["failureFactor"] = failure_factor

    if verify_email is not None:
        update_data["verifyEmail"] = verify_email

    if login_with_email_allowed is not None:
        update_data["loginWithEmailAllowed"] = login_with_email_allowed

    if duplicate_emails_allowed is not None:
        update_data["duplicateEmailsAllowed"] = duplicate_emails_allowed

    if reset_password_allowed is not None:
        update_data["resetPasswordAllowed"] = reset_password_allowed

    if edit_username_allowed is not None:
        update_data["editUsernameAllowed"] = edit_username_allowed

    if registration_allowed is not None:
        update_data["registrationAllowed"] = registration_allowed

    if registration_email_as_username is not None:
        update_data["registrationEmailAsUsername"] = registration_email_as_username

    if remember_me is not None:
        update_data["rememberMe"] = remember_me

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_realm_security_settings(realm=realm)


@mcp.tool()
async def get_realm_attributes(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get custom attributes configured for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing realm attributes
    """
    realm_info = await client._make_request("GET", "", realm=realm)

    return {
        "attributes": realm_info.get("attributes", {}),
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def update_realm_attributes(
    attributes: Dict[str, str], realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update custom attributes for a realm.

    Args:
        attributes: Dictionary of attribute key-value pairs
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing updated realm attributes
    """
    update_data = {"attributes": attributes}

    await client._make_request("PUT", "", data=update_data, realm=realm)

    return await get_realm_attributes(realm=realm)


@mcp.tool()
async def get_comprehensive_security_summary(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a comprehensive summary of all security policies and configurations for a realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing comprehensive security configuration summary
    """
    # Gather all security-related information
    password_policy = await get_password_policy(realm=realm)
    otp_policy = await get_otp_policy(realm=realm)
    webauthn_policy = await get_webauthn_policy(realm=realm)
    browser_headers = await get_browser_security_headers(realm=realm)
    smtp_config = await get_smtp_configuration(realm=realm)
    security_settings = await get_realm_security_settings(realm=realm)
    realm_attributes = await get_realm_attributes(realm=realm)

    return {
        "realm": realm or client.realm_name,
        "passwordPolicy": password_policy,
        "otpPolicy": otp_policy,
        "webAuthnPolicy": webauthn_policy,
        "browserSecurityHeaders": browser_headers,
        "smtpConfiguration": smtp_config,
        "securitySettings": security_settings,
        "realmAttributes": realm_attributes,
        "summary": {
            "passwordPolicyConfigured": bool(
                password_policy.get("passwordPolicyString")
            ),
            "bruteForceProtectionEnabled": security_settings.get(
                "bruteForceProtected", False
            ),
            "emailVerificationRequired": security_settings.get("verifyEmail", False),
            "sslRequired": security_settings.get("sslRequired"),
            "registrationAllowed": security_settings.get("registrationAllowed", False),
            "smtpConfigured": bool(smtp_config.get("smtpServer", {}).get("host")),
            "webAuthnConfigured": bool(
                webauthn_policy.get("regular", {}).get("rpEntityName")
            ),
            "browserHeadersConfigured": bool(
                browser_headers.get("browserSecurityHeaders")
            ),
            "customAttributesCount": len(realm_attributes.get("attributes", {})),
        },
    }
