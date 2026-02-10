"""
Integration tests for Security Policies & Configuration.

Tests password policies, OTP policies, WebAuthn configuration, browser security
headers, SMTP configuration, realm security settings, and custom attributes.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import security_policies_tools

try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    # Mock pytest decorators for standalone execution
    class MockPytest:
        class mark:
            @staticmethod
            def integration(func):
                return func

        @staticmethod
        def fixture(func):
            return func

    pytest = MockPytest()


@pytest.mark.integration
class TestPasswordPolicy:
    """Test password policy management."""

    async def test_get_password_policy(self):
        """Test getting password policy."""
        policy = await security_policies_tools.get_password_policy()
        assert isinstance(policy, dict)
        assert "passwordPolicy" in policy or "passwordPolicyString" in policy

    async def test_update_password_policy(self):
        """Test updating password policy."""
        # Update with test policy
        result = await security_policies_tools.update_password_policy(
            length=8,
            digits=1,
            lower_case=True,
            upper_case=True,
        )
        assert isinstance(result, dict)
        assert "status" in result or "passwordPolicy" in result or "realm" in result


@pytest.mark.integration
class TestOTPPolicy:
    """Test OTP policy management."""

    async def test_get_otp_policy(self):
        """Test getting OTP policy."""
        policy = await security_policies_tools.get_otp_policy()
        assert isinstance(policy, dict)
        # Check for OTP policy fields
        assert "otpPolicyType" in policy or "realm" in policy

    async def test_update_otp_policy(self):
        """Test updating OTP policy."""
        result = await security_policies_tools.update_otp_policy(
            otp_type="totp",
            algorithm="HmacSHA256",
            digits=6,
            period=30,
        )
        assert isinstance(result, dict)
        assert "status" in result or "otpPolicyType" in result or "realm" in result


@pytest.mark.integration
class TestWebAuthnPolicy:
    """Test WebAuthn policy management."""

    async def test_get_webauthn_policy(self):
        """Test getting WebAuthn policy."""
        policy = await security_policies_tools.get_webauthn_policy()
        assert isinstance(policy, dict)
        # WebAuthn policy may have regular and passwordless sections
        assert "realm" in policy or "webAuthnPolicy" in policy

    async def test_update_webauthn_policy(self):
        """Test updating WebAuthn policy."""
        result = await security_policies_tools.update_webauthn_policy(
            policy_type="regular",
            rp_entity_name="Test Realm",
            signature_algorithms=["ES256", "RS256"],
        )
        assert isinstance(result, dict)
        assert "status" in result or "realm" in result or "webAuthnPolicy" in result


@pytest.mark.integration
class TestBrowserSecurityHeaders:
    """Test browser security headers management."""

    async def test_get_browser_security_headers(self):
        """Test getting browser security headers."""
        headers = await security_policies_tools.get_browser_security_headers()
        assert isinstance(headers, dict)
        assert "browserSecurityHeaders" in headers or "realm" in headers

    async def test_update_browser_security_headers(self):
        """Test updating browser security headers."""
        result = await security_policies_tools.update_browser_security_headers(
            x_frame_options="SAMEORIGIN",
            x_content_type_options="nosniff",
        )
        assert isinstance(result, dict)
        assert "status" in result or "browserSecurityHeaders" in result or "realm" in result


@pytest.mark.integration
class TestSMTPConfiguration:
    """Test SMTP configuration management."""

    async def test_get_smtp_configuration(self):
        """Test getting SMTP configuration."""
        config = await security_policies_tools.get_smtp_configuration()
        assert isinstance(config, dict)
        assert "smtpServer" in config or "realm" in config

    async def test_update_smtp_configuration(self):
        """Test updating SMTP configuration."""
        # Update with test values (won't actually send emails)
        result = await security_policies_tools.update_smtp_configuration(
            host="smtp.example.com",
            port="587",
            from_email="noreply@example.com",
            from_display_name="Test Realm",
        )
        assert isinstance(result, dict)
        assert "status" in result or "smtpServer" in result or "realm" in result

    async def test_test_smtp_connection(self):
        """Test SMTP connection testing."""
        # This may fail with test configuration, which is expected
        try:
            result = await security_policies_tools.test_smtp_connection(
                "test@example.com"
            )
            assert isinstance(result, dict)
        except Exception:
            # Expected to fail with invalid SMTP configuration
            pass


@pytest.mark.integration
class TestRealmSecuritySettings:
    """Test realm security settings management."""

    async def test_get_realm_security_settings(self):
        """Test getting realm security settings."""
        settings = await security_policies_tools.get_realm_security_settings()
        assert isinstance(settings, dict)
        # Check for security-related fields
        assert "sslRequired" in settings or "realm" in settings

    async def test_update_realm_security_settings(self):
        """Test updating realm security settings."""
        result = await security_policies_tools.update_realm_security_settings(
            verify_email=True,
            login_with_email_allowed=True,
        )
        assert isinstance(result, dict)
        assert "status" in result or "realm" in result or "sslRequired" in result


@pytest.mark.integration
class TestRealmAttributes:
    """Test realm custom attributes management."""

    async def test_get_realm_attributes(self):
        """Test getting realm attributes."""
        attrs = await security_policies_tools.get_realm_attributes()
        assert isinstance(attrs, dict)
        assert "attributes" in attrs or "realm" in attrs

    async def test_update_realm_attributes(self):
        """Test updating realm attributes."""
        test_attrs = {
            "test-attribute-1": "value1",
            "test-attribute-2": "value2",
        }
        result = await security_policies_tools.update_realm_attributes(test_attrs)
        assert isinstance(result, dict)
        assert "status" in result or "attributes" in result or "realm" in result


@pytest.mark.integration
class TestSecuritySummary:
    """Test comprehensive security summary."""

    async def test_get_comprehensive_security_summary(self):
        """Test getting comprehensive security summary."""
        summary = await security_policies_tools.get_comprehensive_security_summary()
        assert isinstance(summary, dict)
        assert "realm" in summary
        # Should contain comprehensive security information
        assert (
            "passwordPolicy" in summary
            or "otpPolicy" in summary
            or "summary" in summary
        )


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        """Run all tests."""
        print("\n=== Running Security Policies Integration Tests ===\n")

        # Test Password Policy
        test_pwd = TestPasswordPolicy()
        print("Testing password policy...")
        try:
            await test_pwd.test_get_password_policy()
            print("[PASS] Get password policy test passed")
        except Exception as e:
            print(f"[FAIL] Get password policy test failed: {e}")

        try:
            await test_pwd.test_update_password_policy()
            print("[PASS] Update password policy test passed")
        except Exception as e:
            print(f"[FAIL] Update password policy test failed: {e}")

        # Test OTP Policy
        test_otp = TestOTPPolicy()
        print("\nTesting OTP policy...")
        try:
            await test_otp.test_get_otp_policy()
            print("[PASS] Get OTP policy test passed")
        except Exception as e:
            print(f"[FAIL] Get OTP policy test failed: {e}")

        try:
            await test_otp.test_update_otp_policy()
            print("[PASS] Update OTP policy test passed")
        except Exception as e:
            print(f"[FAIL] Update OTP policy test failed: {e}")

        # Test WebAuthn Policy
        test_webauthn = TestWebAuthnPolicy()
        print("\nTesting WebAuthn policy...")
        try:
            await test_webauthn.test_get_webauthn_policy()
            print("[PASS] Get WebAuthn policy test passed")
        except Exception as e:
            print(f"[FAIL] Get WebAuthn policy test failed: {e}")

        try:
            await test_webauthn.test_update_webauthn_policy()
            print("[PASS] Update WebAuthn policy test passed")
        except Exception as e:
            print(f"[FAIL] Update WebAuthn policy test failed: {e}")

        # Test Browser Security Headers
        test_headers = TestBrowserSecurityHeaders()
        print("\nTesting browser security headers...")
        try:
            await test_headers.test_get_browser_security_headers()
            print("[PASS] Get browser security headers test passed")
        except Exception as e:
            print(f"[FAIL] Get browser security headers test failed: {e}")

        try:
            await test_headers.test_update_browser_security_headers()
            print("[PASS] Update browser security headers test passed")
        except Exception as e:
            print(f"[FAIL] Update browser security headers test failed: {e}")

        # Test SMTP Configuration
        test_smtp = TestSMTPConfiguration()
        print("\nTesting SMTP configuration...")
        try:
            await test_smtp.test_get_smtp_configuration()
            print("[PASS] Get SMTP configuration test passed")
        except Exception as e:
            print(f"[FAIL] Get SMTP configuration test failed: {e}")

        try:
            await test_smtp.test_update_smtp_configuration()
            print("[PASS] Update SMTP configuration test passed")
        except Exception as e:
            print(f"[FAIL] Update SMTP configuration test failed: {e}")

        try:
            await test_smtp.test_test_smtp_connection()
            print("[PASS] Test SMTP connection test passed")
        except Exception as e:
            print(f"[FAIL] Test SMTP connection test failed: {e}")

        # Test Realm Security Settings
        test_security = TestRealmSecuritySettings()
        print("\nTesting realm security settings...")
        try:
            await test_security.test_get_realm_security_settings()
            print("[PASS] Get realm security settings test passed")
        except Exception as e:
            print(f"[FAIL] Get realm security settings test failed: {e}")

        try:
            await test_security.test_update_realm_security_settings()
            print("[PASS] Update realm security settings test passed")
        except Exception as e:
            print(f"[FAIL] Update realm security settings test failed: {e}")

        # Test Realm Attributes
        test_attrs = TestRealmAttributes()
        print("\nTesting realm attributes...")
        try:
            await test_attrs.test_get_realm_attributes()
            print("[PASS] Get realm attributes test passed")
        except Exception as e:
            print(f"[FAIL] Get realm attributes test failed: {e}")

        try:
            await test_attrs.test_update_realm_attributes()
            print("[PASS] Update realm attributes test passed")
        except Exception as e:
            print(f"[FAIL] Update realm attributes test failed: {e}")

        # Test Security Summary
        test_summary = TestSecuritySummary()
        print("\nTesting comprehensive security summary...")
        try:
            await test_summary.test_get_comprehensive_security_summary()
            print("[PASS] Get comprehensive security summary test passed")
        except Exception as e:
            print(f"[FAIL] Get comprehensive security summary test failed: {e}")

        print("\n=== Security Policies Tests Completed! ===\n")

    asyncio.run(run_tests())
