"""
Integration tests for Phase 2 Security Features

Tests for:
- Phase 2.1: Attack Detection / Brute Force Protection
- Phase 2.4: Keys Management
- Phase 2.5: Security Policies & Configuration

These tests verify all security-related MCP tools work correctly with a live Keycloak server.
"""

import pytest
import asyncio

# Import all Phase 2 security tools for testing
from src.tools.attack_detection_tools import (
    configure_brute_force_protection,
    get_brute_force_configuration,
    monitor_failed_login_attempts,
    analyze_brute_force_patterns,
    get_failed_login_events,
    get_brute_force_statistics,
    enable_brute_force_protection,
    get_security_monitoring_summary,
)

from src.tools.keys_management_tools import (
    get_realm_keys,
    get_realm_certificates,
    analyze_key_security,
    monitor_key_expiration,
    get_key_providers,
    get_signing_algorithms,
    export_realm_certificate,
    get_client_certificates,
    validate_certificate_chain,
    get_keys_summary,
    get_comprehensive_keys_report,
)

from src.tools.security_policies_tools import (
    get_password_policy,
    update_password_policy,
    get_otp_policy,
    update_otp_policy,
    get_webauthn_policy,
    update_webauthn_policy,
    get_browser_security_headers,
    update_browser_security_headers,
    get_smtp_configuration,
    update_smtp_configuration,
    test_smtp_connection,
    get_realm_security_settings,
    update_realm_security_settings,
    get_realm_attributes,
    update_realm_attributes,
    get_comprehensive_security_summary,
)

# Test realm for security testing
TEST_REALM = "security-test-realm"


@pytest.mark.integration
class TestAttackDetectionTools:
    """Test Attack Detection and Brute Force Protection tools."""

    async def test_brute_force_configuration(self):
        """Test getting and configuring brute force protection settings."""
        # Get current configuration
        config = await get_brute_force_configuration()
        assert isinstance(config, dict)
        assert "bruteForceProtected" in config
        assert "realm" in config

        # Test configuration update
        updated_config = await configure_brute_force_protection(
            enabled=True,
            max_failure_wait_seconds=900,
            minimum_quick_login_wait_seconds=60,
            wait_increment_seconds=60,
            quick_login_check_milli_seconds=1000,
            max_delta_time_seconds=43200,
            failure_factor=30,
        )
        assert isinstance(updated_config, dict)
        assert updated_config["bruteForceProtected"]

    async def test_failed_login_monitoring(self):
        """Test failed login monitoring and pattern analysis."""
        # Monitor failed login attempts
        failed_logins = await monitor_failed_login_attempts()
        assert isinstance(failed_logins, dict)
        assert "failedAttempts" in failed_logins

        # Get failed login events
        events = await get_failed_login_events()
        assert isinstance(events, dict)
        assert "events" in events

        # Analyze brute force patterns
        analysis = await analyze_brute_force_patterns()
        assert isinstance(analysis, dict)
        assert "patterns" in analysis

    async def test_brute_force_statistics(self):
        """Test brute force statistics and monitoring summary."""
        # Get brute force statistics
        stats = await get_brute_force_statistics()
        assert isinstance(stats, dict)
        assert "statistics" in stats

        # Get security monitoring summary
        summary = await get_security_monitoring_summary()
        assert isinstance(summary, dict)
        assert "summary" in summary

    async def test_enable_brute_force_protection(self):
        """Test enabling brute force protection with convenience function."""
        result = await enable_brute_force_protection()
        assert isinstance(result, dict)
        assert result["success"]


@pytest.mark.integration
class TestKeysManagementTools:
    """Test Keys Management tools."""

    async def test_realm_keys_and_certificates(self):
        """Test getting realm keys and certificates."""
        # Get realm keys
        keys = await get_realm_keys()
        assert isinstance(keys, dict)
        assert "keys" in keys
        assert isinstance(keys["keys"], list)

        # Get realm certificates
        certificates = await get_realm_certificates()
        assert isinstance(certificates, dict)
        assert "certificates" in certificates

    async def test_key_security_analysis(self):
        """Test key security analysis and monitoring."""
        # Analyze key security
        analysis = await analyze_key_security()
        assert isinstance(analysis, dict)
        assert "analysis" in analysis

        # Monitor key expiration
        expiration_report = await monitor_key_expiration()
        assert isinstance(expiration_report, dict)
        assert "expirationMonitoring" in expiration_report

    async def test_key_providers_and_algorithms(self):
        """Test getting key providers and signing algorithms."""
        # Get key providers
        providers = await get_key_providers()
        assert isinstance(providers, dict)
        assert "providers" in providers

        # Get signing algorithms
        algorithms = await get_signing_algorithms()
        assert isinstance(algorithms, dict)
        assert "algorithms" in algorithms

    async def test_certificate_operations(self):
        """Test certificate export and validation."""
        # Export realm certificate (may fail if no certificate available)
        try:
            cert_export = await export_realm_certificate()
            assert isinstance(cert_export, dict)
        except Exception as e:
            # Expected if no certificate is configured
            assert "not found" in str(e).lower() or "no certificate" in str(e).lower()

        # Get client certificates
        client_certs = await get_client_certificates()
        assert isinstance(client_certs, dict)
        assert "certificates" in client_certs

        # Validate certificate chain (may have no certificates to validate)
        validation = await validate_certificate_chain()
        assert isinstance(validation, dict)
        assert "validation" in validation

    async def test_keys_summary_reports(self):
        """Test keys summary and comprehensive reports."""
        # Get keys summary
        summary = await get_keys_summary()
        assert isinstance(summary, dict)
        assert "summary" in summary

        # Get comprehensive keys report
        comprehensive_report = await get_comprehensive_keys_report()
        assert isinstance(comprehensive_report, dict)
        assert "report" in comprehensive_report


@pytest.mark.integration
class TestSecurityPoliciesTools:
    """Test Security Policies & Configuration tools."""

    async def test_password_policy_management(self):
        """Test password policy configuration."""
        # Get current password policy
        current_policy = await get_password_policy()
        assert isinstance(current_policy, dict)
        assert "passwordPolicyString" in current_policy
        assert "parsedPolicy" in current_policy

        # Update password policy
        updated_policy = await update_password_policy(
            length=8,
            digits=1,
            lower_case=True,
            upper_case=True,
            special_chars=1,
            not_username=True,
        )
        assert isinstance(updated_policy, dict)
        assert updated_policy["parsedPolicy"]["length"] == 8
        assert updated_policy["parsedPolicy"]["digits"] == 1

    async def test_otp_policy_management(self):
        """Test OTP policy configuration."""
        # Get current OTP policy
        current_otp = await get_otp_policy()
        assert isinstance(current_otp, dict)
        assert "otpPolicyType" in current_otp
        assert "otpPolicyAlgorithm" in current_otp

        # Update OTP policy
        updated_otp = await update_otp_policy(
            otp_type="totp",
            algorithm="HmacSHA256",
            digits=6,
            period=30,
            look_ahead_window=1,
        )
        assert isinstance(updated_otp, dict)
        assert updated_otp["otpPolicyType"] == "totp"
        assert updated_otp["otpPolicyAlgorithm"] == "HmacSHA256"

    async def test_webauthn_policy_management(self):
        """Test WebAuthn policy configuration."""
        # Get current WebAuthn policy
        current_webauthn = await get_webauthn_policy()
        assert isinstance(current_webauthn, dict)
        assert "regular" in current_webauthn
        assert "passwordless" in current_webauthn

        # Update regular WebAuthn policy
        updated_regular = await update_webauthn_policy(
            policy_type="regular",
            rp_entity_name="Test Realm",
            signature_algorithms=["ES256", "RS256"],
            rp_id="test.example.com",
            user_verification_requirement="preferred",
        )
        assert isinstance(updated_regular, dict)

        # Update passwordless WebAuthn policy
        updated_passwordless = await update_webauthn_policy(
            policy_type="passwordless",
            rp_entity_name="Test Realm Passwordless",
            passkeys_enabled=True,
            user_verification_requirement="required",
        )
        assert isinstance(updated_passwordless, dict)

    async def test_browser_security_headers(self):
        """Test browser security headers configuration."""
        # Get current headers
        current_headers = await get_browser_security_headers()
        assert isinstance(current_headers, dict)
        assert "browserSecurityHeaders" in current_headers

        # Update browser security headers
        updated_headers = await update_browser_security_headers(
            content_security_policy="default-src 'self'",
            x_content_type_options="nosniff",
            x_frame_options="DENY",
            x_xss_protection="1; mode=block",
        )
        assert isinstance(updated_headers, dict)
        assert "default-src 'self'" in updated_headers["browserSecurityHeaders"].get(
            "contentSecurityPolicy", ""
        )

    async def test_smtp_configuration(self):
        """Test SMTP configuration management."""
        # Get current SMTP configuration
        current_smtp = await get_smtp_configuration()
        assert isinstance(current_smtp, dict)
        assert "smtpServer" in current_smtp

        # Update SMTP configuration
        updated_smtp = await update_smtp_configuration(
            host="smtp.example.com",
            port="587",
            from_email="test@example.com",
            from_display_name="Test Realm",
            auth=True,
            starttls=True,
            user="testuser",
            # Note: Not setting password in test
        )
        assert isinstance(updated_smtp, dict)
        assert updated_smtp["smtpServer"].get("host") == "smtp.example.com"

        # Test SMTP connection (expected to fail with test configuration)
        try:
            smtp_test = await test_smtp_connection("test@example.com")
            # If it succeeds, that's fine too
            assert isinstance(smtp_test, dict)
        except Exception:
            # Expected to fail with test configuration
            pass

    async def test_realm_security_settings(self):
        """Test comprehensive realm security settings."""
        # Get current security settings
        current_settings = await get_realm_security_settings()
        assert isinstance(current_settings, dict)
        assert "sslRequired" in current_settings
        assert "bruteForceProtected" in current_settings

        # Update security settings
        updated_settings = await update_realm_security_settings(
            ssl_required="external",
            brute_force_protected=True,
            verify_email=True,
            login_with_email_allowed=True,
            reset_password_allowed=True,
            registration_allowed=True,
            remember_me=True,
        )
        assert isinstance(updated_settings, dict)
        assert updated_settings["sslRequired"] == "external"
        assert updated_settings["bruteForceProtected"]

    async def test_realm_attributes(self):
        """Test realm custom attributes management."""
        # Get current attributes
        current_attrs = await get_realm_attributes()
        assert isinstance(current_attrs, dict)
        assert "attributes" in current_attrs

        # Update attributes
        test_attributes = {
            "customAttribute1": "value1",
            "customAttribute2": "value2",
            "testAttribute": "testValue",
        }
        updated_attrs = await update_realm_attributes(test_attributes)
        assert isinstance(updated_attrs, dict)
        assert updated_attrs["attributes"]["customAttribute1"] == "value1"
        assert updated_attrs["attributes"]["testAttribute"] == "testValue"

    async def test_comprehensive_security_summary(self):
        """Test comprehensive security configuration summary."""
        summary = await get_comprehensive_security_summary()
        assert isinstance(summary, dict)
        assert "realm" in summary
        assert "passwordPolicy" in summary
        assert "otpPolicy" in summary
        assert "webAuthnPolicy" in summary
        assert "browserSecurityHeaders" in summary
        assert "smtpConfiguration" in summary
        assert "securitySettings" in summary
        assert "realmAttributes" in summary
        assert "summary" in summary

        # Verify summary statistics
        summary_stats = summary["summary"]
        assert isinstance(summary_stats["passwordPolicyConfigured"], bool)
        assert isinstance(summary_stats["bruteForceProtectionEnabled"], bool)
        assert isinstance(summary_stats["emailVerificationRequired"], bool)
        assert isinstance(summary_stats["smtpConfigured"], bool)
        assert isinstance(summary_stats["customAttributesCount"], int)


@pytest.mark.integration
class TestPhase2Integration:
    """Integration tests for all Phase 2 security features working together."""

    async def test_complete_security_configuration(self):
        """Test configuring a complete security setup using all Phase 2 tools."""

        # Step 1: Configure brute force protection
        await configure_brute_force_protection(
            enabled=True, max_failure_wait_seconds=600, failure_factor=25
        )

        # Step 2: Set up comprehensive password policy
        await update_password_policy(
            length=10,
            digits=2,
            lower_case=True,
            upper_case=True,
            special_chars=1,
            not_username=True,
            not_email=True,
            password_history=3,
        )

        # Step 3: Configure OTP policy
        await update_otp_policy(
            otp_type="totp", algorithm="HmacSHA256", digits=6, period=30
        )

        # Step 4: Set up WebAuthn policies
        await update_webauthn_policy(
            policy_type="regular",
            rp_entity_name="Secure Test Realm",
            signature_algorithms=["ES256", "RS256"],
            user_verification_requirement="preferred",
        )

        # Step 5: Configure browser security headers
        await update_browser_security_headers(
            content_security_policy="default-src 'self'; script-src 'self' 'unsafe-inline'",
            x_content_type_options="nosniff",
            x_frame_options="SAMEORIGIN",
            strict_transport_security="max-age=31536000; includeSubDomains",
        )

        # Step 6: Update realm security settings
        await update_realm_security_settings(
            ssl_required="external",
            brute_force_protected=True,
            verify_email=True,
            registration_allowed=True,
            reset_password_allowed=True,
        )

        # Step 7: Verify comprehensive configuration
        security_summary = await get_comprehensive_security_summary()
        assert security_summary["summary"]["passwordPolicyConfigured"]
        assert security_summary["summary"]["bruteForceProtectionEnabled"]

        keys_report = await get_comprehensive_keys_report()
        assert isinstance(keys_report, dict)

        monitoring_summary = await get_security_monitoring_summary()
        assert isinstance(monitoring_summary, dict)

    async def test_security_monitoring_workflow(self):
        """Test a complete security monitoring workflow."""

        # Step 1: Enable security features
        await enable_brute_force_protection()

        # Step 2: Get baseline security state
        initial_summary = await get_comprehensive_security_summary()

        # Step 3: Monitor for security events
        failed_logins = await monitor_failed_login_attempts()
        brute_force_stats = await get_brute_force_statistics()

        # Step 4: Analyze patterns
        pattern_analysis = await analyze_brute_force_patterns()

        # Step 5: Check keys and certificates
        keys_summary = await get_keys_summary()
        key_expiration = await monitor_key_expiration()

        # Step 6: Generate comprehensive security report
        final_summary = await get_security_monitoring_summary()

        # Verify all components returned valid data
        assert isinstance(initial_summary, dict)
        assert isinstance(failed_logins, dict)
        assert isinstance(brute_force_stats, dict)
        assert isinstance(pattern_analysis, dict)
        assert isinstance(keys_summary, dict)
        assert isinstance(key_expiration, dict)
        assert isinstance(final_summary, dict)


# Test fixtures and utilities
@pytest.fixture(scope="module")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_phase2_security.py -v -m integration
    pytest.main([__file__, "-v", "-m", "integration"])
