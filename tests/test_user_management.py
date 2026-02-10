"""
Integration tests for User Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import user_tools

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
class TestUserLifecycle:
    """Test user CRUD operations."""

    async def test_create_and_delete_user(self, unique_username):
        """Test creating and deleting a user."""
        result = await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="User",
            enabled=True,
        )
        assert result["status"] == "created"

        # Find user
        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        assert test_user is not None
        user_id = test_user["id"]

        try:
            # Get user by ID
            user = await user_tools.get_user(user_id)
            assert user["username"] == unique_username
            assert user["email"] == f"{unique_username}@example.com"
            assert user["firstName"] == "Test"
            assert user["lastName"] == "User"
        finally:
            # Delete user
            delete_result = await user_tools.delete_user(user_id)
            assert delete_result["status"] == "deleted"

            # Verify deletion
            users = await user_tools.list_users(search=unique_username)
            assert not any(u["username"] == unique_username for u in users)

    async def test_update_user(self, unique_username):
        """Test updating user attributes."""
        # Create user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Original",
            last_name="Name",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Update user
            result = await user_tools.update_user(
                user_id=user_id,
                first_name="Updated",
                last_name="UserName",
                email=f"updated-{unique_username}@example.com",
            )
            assert result["status"] == "updated"

            # Verify update
            user = await user_tools.get_user(user_id)
            assert user["firstName"] == "Updated"
            assert user["lastName"] == "UserName"
            assert user["email"] == f"updated-{unique_username}@example.com"
        finally:
            await user_tools.delete_user(user_id)

    async def test_create_user_with_password(self, unique_username):
        """Test creating a user with an initial password."""
        result = await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="WithPassword",
            enabled=True,
            password="TestPassword123!",
            temporary_password=False,
        )
        assert result["status"] == "created"

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            user = await user_tools.get_user(user_id)
            assert user["username"] == unique_username
            assert user["enabled"] is True
        finally:
            await user_tools.delete_user(user_id)


@pytest.mark.integration
class TestUserListing:
    """Test user listing and search."""

    async def test_list_users(self):
        """Test listing users."""
        users = await user_tools.list_users(max=10)
        assert isinstance(users, list)

    async def test_list_users_with_search(self, unique_username):
        """Test listing users with search filter."""
        # Create user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Searchable",
            last_name="User",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Search should find our user
            assert test_user is not None
            assert test_user["username"] == unique_username
        finally:
            await user_tools.delete_user(user_id)

    async def test_count_users(self):
        """Test counting users."""
        count = await user_tools.count_users()
        assert isinstance(count, int)
        assert count >= 0


@pytest.mark.integration
class TestUserPasswordManagement:
    """Test user password operations."""

    async def test_reset_user_password(self, unique_username):
        """Test resetting a user password."""
        # Create user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Password",
            last_name="Reset",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Reset password
            result = await user_tools.reset_user_password(
                user_id=user_id,
                password="NewPassword456!",
                temporary=False,
            )
            assert result["status"] == "password_reset"
        finally:
            await user_tools.delete_user(user_id)


@pytest.mark.integration
class TestUserSessions:
    """Test user session operations."""

    async def test_get_user_sessions(self, unique_username):
        """Test getting user sessions."""
        # Create user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Session",
            last_name="User",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Get sessions (likely empty for new user)
            sessions = await user_tools.get_user_sessions(user_id)
            assert isinstance(sessions, list)
        finally:
            await user_tools.delete_user(user_id)

    async def test_logout_user(self, unique_username):
        """Test logging out a user."""
        # Create user
        await user_tools.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Logout",
            last_name="User",
            enabled=True,
        )

        users = await user_tools.list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Logout user (should work even with no active sessions)
            result = await user_tools.logout_user(user_id)
            assert result["status"] == "logged_out"
        finally:
            await user_tools.delete_user(user_id)


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running User Management Integration Tests ===\n")

    test_lifecycle = TestUserLifecycle()
    test_listing = TestUserListing()
    test_password = TestUserPasswordManagement()
    test_sessions = TestUserSessions()

    tests = [
        ("User create and delete", test_lifecycle.test_create_and_delete_user),
        ("User update", test_lifecycle.test_update_user),
        ("User create with password", test_lifecycle.test_create_user_with_password),
        ("List users", test_listing.test_list_users),
        ("List users with search", test_listing.test_list_users_with_search),
        ("Count users", test_listing.test_count_users),
        ("Reset user password", test_password.test_reset_user_password),
        ("Get user sessions", test_sessions.test_get_user_sessions),
        ("Logout user", test_sessions.test_logout_user),
    ]

    for name, test_func in tests:
        print(f"Testing {name}...")
        try:
            import inspect

            sig = inspect.signature(test_func)
            if "unique_username" in sig.parameters:
                await test_func(f"test-user-{uuid.uuid4().hex[:8]}")
            else:
                await test_func()
            print(f"[PASS] {name} test passed")
        except Exception as e:
            print(f"[FAIL] {name} test failed: {e}")

    print("\n=== User Management Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
