# This file has been renamed to test_attack_detection.py for consistency
# Please use test_attack_detection.py instead

import pytest
from src.tools.attack_detection_tools import (
    get_user_brute_force_status,
    clear_user_login_failures,
    clear_all_login_failures,
)
from src.tools.user_tools import create_user, list_users, delete_user


@pytest.fixture(scope="module")
async def test_user():
    """Create a test user for attack detection tests"""
    # Create test user
    username = "attack-test-user"
    await create_user(
        username=username,
        email="attack-test@example.com",
        first_name="Attack",
        last_name="Test",
        enabled=True,
    )

    # Get the user ID (realm uses registrationEmailAsUsername, so stored username = email)
    users = await list_users(email="attack-test@example.com")
    user_id = users[0]["id"]

    yield user_id

    # Cleanup
    try:
        await delete_user(user_id)
    except Exception:
        pass  # User might already be deleted


@pytest.mark.integration
class TestAttackDetection:
    """Test attack detection functionality"""

    async def test_get_user_brute_force_status(self, test_user):
        """Test getting brute force status for a user"""
        status = await get_user_brute_force_status(test_user)

        # Status should be a dictionary
        assert isinstance(status, dict)

        # Common fields that might be present (Keycloak returns empty dict for users with no failures)
        # When there are failures, it includes: numFailures, disabled, lastIPFailure, lastFailure
        # For a new user, we expect either an empty dict or a dict with numFailures=0
        if status:
            assert "numFailures" in status or len(status) == 0

    async def test_clear_user_login_failures(self, test_user):
        """Test clearing login failures for a specific user"""
        result = await clear_user_login_failures(test_user)

        assert result["status"] == "cleared"
        assert test_user in result["message"]

        # Verify the failures are cleared by checking status
        status = await get_user_brute_force_status(test_user)
        # After clearing, should either be empty dict or numFailures should be 0 or not present
        assert isinstance(status, dict)

    async def test_clear_all_login_failures(self):
        """Test clearing login failures for all users"""
        result = await clear_all_login_failures()

        assert result["status"] == "cleared"
        assert "all users" in result["message"]

    async def test_clear_user_login_failures_nonexistent_user(self):
        """Test clearing login failures for a non-existent user"""
        # Keycloak typically returns 204 No Content even for non-existent users
        # This is expected behavior - it's idempotent
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        result = await clear_user_login_failures(fake_user_id)

        assert result["status"] == "cleared"

    async def test_get_brute_force_status_nonexistent_user(self):
        """Test getting brute force status for a non-existent user"""
        fake_user_id = "00000000-0000-0000-0000-000000000000"

        # This should likely return an empty dict or raise an error
        # depending on Keycloak's implementation
        try:
            status = await get_user_brute_force_status(fake_user_id)
            # If it succeeds, it should return a dict
            assert isinstance(status, dict)
        except Exception as e:
            # If it fails, that's also acceptable
            assert "404" in str(e) or "not found" in str(e).lower()

    async def test_clear_operations_are_idempotent(self, test_user):
        """Test that clear operations can be called multiple times safely"""
        # Clear user failures multiple times
        result1 = await clear_user_login_failures(test_user)
        result2 = await clear_user_login_failures(test_user)

        assert result1["status"] == "cleared"
        assert result2["status"] == "cleared"

        # Clear all failures multiple times
        result3 = await clear_all_login_failures()
        result4 = await clear_all_login_failures()

        assert result3["status"] == "cleared"
        assert result4["status"] == "cleared"

    async def test_realm_parameter(self, test_user):
        """Test that realm parameter works correctly"""
        # Test with explicit realm parameter (using default realm from config)
        # Don't hardcode "master" as the test user is created in the default realm
        status = await get_user_brute_force_status(test_user, realm=None)
        assert isinstance(status, dict)

        result = await clear_user_login_failures(test_user, realm=None)
        assert result["status"] == "cleared"

        result = await clear_all_login_failures(realm=None)
        assert result["status"] == "cleared"
