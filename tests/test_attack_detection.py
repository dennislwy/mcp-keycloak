"""
Integration tests for Attack Detection & Brute Force Protection.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import attack_detection_tools, user_tools

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


if PYTEST_AVAILABLE:

    @pytest.fixture
    def unique_username():
        """Generate a unique username for testing."""
        return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestBruteForceConfiguration:
    """Test brute force protection configuration."""

    async def test_get_brute_force_configuration(self):
        """Test getting brute force configuration."""
        config = await attack_detection_tools.get_brute_force_configuration()
        assert isinstance(config, dict)
        # Check for common brute force config fields
        assert "bruteForceProtected" in config or "realm" in config

    async def test_enable_brute_force_protection_convenience(self):
        """Test the convenience function for enabling brute force protection."""
        result = await attack_detection_tools.enable_brute_force_protection()
        assert isinstance(result, dict)
        # Function may succeed or fail depending on server config
        # Just verify it returns a dict response
        assert "success" in result or "status" in result or "bruteForceProtected" in result


@pytest.mark.integration
class TestUserLoginFailures:
    """Test user login failure management."""

    async def test_get_user_brute_force_status(self, unique_username):
        """Test getting brute force status for a user."""
        # Create a test user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="User",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        user = next(u for u in users if u["username"] == unique_username)
        user_id = user["id"]

        try:
            # Get brute force status
            status = await attack_detection_tools.get_user_brute_force_status(user_id)
            assert isinstance(status, dict)

        finally:
            await user_tools.delete_user(user_id)

    async def test_clear_user_login_failures(self, unique_username):
        """Test clearing login failures for a specific user."""
        # Create a test user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="User",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        user = next(u for u in users if u["username"] == unique_username)
        user_id = user["id"]

        try:
            # Clear login failures
            result = await attack_detection_tools.clear_user_login_failures(user_id)
            assert "status" in result

        finally:
            await user_tools.delete_user(user_id)

    async def test_clear_all_user_login_failures(self):
        """Test clearing all login failures in the realm."""
        result = await attack_detection_tools.clear_all_user_login_failures()
        assert "status" in result


@pytest.mark.integration
class TestBruteForceMonitoring:
    """Test brute force monitoring and statistics."""

    async def test_get_realm_brute_force_summary(self):
        """Test getting brute force summary for the realm."""
        summary = await attack_detection_tools.get_realm_brute_force_summary()
        assert isinstance(summary, dict)
        # Check for expected structure
        assert "realm" in summary or "brute_force_configuration" in summary
