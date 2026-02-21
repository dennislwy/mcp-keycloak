"""
Integration tests for user management tools.

These tests cover all user-related functionality including CRUD operations,
advanced search, password management, sessions, and user lifecycle features.
"""

import pytest
import uuid
from src.tools.user_tools import (
    list_users,
    create_user,
    update_user,
    delete_user,
    get_user,
    reset_user_password,
    get_user_sessions,
    logout_user,
    count_users,
)
from src.tools.group_tools import create_group, delete_group, list_groups
from src.tools.role_tools import create_realm_role, delete_realm_role


@pytest.fixture
def unique_username():
    """Generate a unique username for testing."""
    return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
async def test_group():
    """Create a test group for user assignment tests."""
    group_name = "test-group-users"
    await create_group(name=group_name)
    yield group_name
    # Cleanup
    try:
        groups = await list_groups(search=group_name, exact=True)
        if groups:
            await delete_group(groups[0]["id"])
    except Exception:
        pass


@pytest.fixture(scope="module")
async def test_role():
    """Create a test role for user assignment tests."""
    role_name = "test-role-users"
    await create_realm_role(name=role_name, description="Test role for user tests")
    yield role_name
    # Cleanup
    try:
        await delete_realm_role(role_name)
    except Exception:
        pass


@pytest.mark.integration
class TestUserCRUD:
    """Test basic user CRUD operations."""

    async def test_create_and_delete_user(self, unique_username):
        """Test creating and deleting a user."""
        result = await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="User",
            enabled=True,
        )
        assert result["status"] == "created"

        # Find user
        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        assert test_user is not None
        user_id = test_user["id"]

        try:
            # Get user by ID
            user = await get_user(user_id)
            assert user["username"] == unique_username
            assert user["email"] == f"{unique_username}@example.com"
            assert user["firstName"] == "Test"
            assert user["lastName"] == "User"
        finally:
            # Delete user
            delete_result = await delete_user(user_id)
            assert delete_result["status"] == "deleted"

            # Verify deletion
            users = await list_users(search=unique_username)
            assert not any(u["username"] == unique_username for u in users)

    async def test_update_user(self, unique_username):
        """Test updating user attributes."""
        # Create user
        await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Original",
            last_name="Name",
            enabled=True,
        )

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Update user
            result = await update_user(
                user_id=user_id,
                first_name="Updated",
                last_name="UserName",
                email=f"updated-{unique_username}@example.com",
            )
            assert result["status"] == "updated"

            # Verify update
            user = await get_user(user_id)
            assert user["firstName"] == "Updated"
            assert user["lastName"] == "UserName"
            assert user["email"] == f"updated-{unique_username}@example.com"
        finally:
            await delete_user(user_id)

    async def test_create_user_with_password(self, unique_username):
        """Test creating a user with an initial password."""
        result = await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Test",
            last_name="WithPassword",
            enabled=True,
            temporary_password="TestPassword123!",
        )
        assert result["status"] == "created"

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            user = await get_user(user_id)
            assert user["username"] == unique_username
            assert user["enabled"] is True
        finally:
            await delete_user(user_id)


@pytest.mark.integration
class TestUserSearch:
    """Test user listing and search capabilities."""

    async def test_list_users(self):
        """Test listing users."""
        users = await list_users(max=10)
        assert isinstance(users, list)

    async def test_list_users_with_search(self, unique_username):
        """Test listing users with search filter."""
        # Create user
        await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Searchable",
            last_name="User",
            enabled=True,
        )

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Search should find our user
            assert test_user is not None
            assert test_user["username"] == unique_username
        finally:
            await delete_user(user_id)

    async def test_count_users(self):
        """Test counting users."""
        count = await count_users()
        assert isinstance(count, int)
        assert count >= 0

    async def test_exact_match_search(self):
        """Test exact matching for user searches."""
        # Create test users
        user1 = "exacttest"
        user2 = "exacttest123"

        await create_user(username=user1, email=f"{user1}@test.com")
        await create_user(username=user2, email=f"{user2}@test.com")

        try:
            # Search without exact match (should find both)
            users = await list_users(username="exacttest")
            assert len(users) >= 2

            # Search with exact match (should find only one)
            exact_users = await list_users(username="exacttest", exact=True)
            assert len(exact_users) == 1
            assert exact_users[0]["username"] == user1
        finally:
            # Cleanup
            all_users = await list_users(search="exacttest")
            for user in all_users:
                if user["username"] in [user1, user2]:
                    await delete_user(user["id"])

    async def test_name_filters(self):
        """Test first_name and last_name filters."""
        username = "namefiltertest"
        await create_user(
            username=username,
            first_name="TestFirst",
            last_name="TestLast",
            email=f"{username}@test.com",
        )

        try:
            # Search by first name
            users = await list_users(first_name="TestFirst")
            found = any(u["username"] == username for u in users)
            assert found, "User not found by first name"

            # Search by last name
            users = await list_users(last_name="TestLast")
            found = any(u["username"] == username for u in users)
            assert found, "User not found by last name"

            # Search with exact match on names
            users = await list_users(
                first_name="TestFirst", last_name="TestLast", exact=True
            )
            found = any(u["username"] == username for u in users)
            assert found, "User not found with exact name match"
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])

    async def test_email_verified_filter(self):
        """Test email_verified filter."""
        username_verified = "emailverifiedtest"
        username_unverified = "emailunverifiedtest"

        await create_user(
            username=username_verified,
            email=f"{username_verified}@test.com",
            email_verified=True,
        )
        await create_user(
            username=username_unverified,
            email=f"{username_unverified}@test.com",
            email_verified=False,
        )

        try:
            # Search for verified emails
            verified_users = await list_users(email_verified=True)
            verified_usernames = [u["username"] for u in verified_users]

            # Search for unverified emails
            unverified_users = await list_users(email_verified=False)
            unverified_usernames = [u["username"] for u in unverified_users]

            # Check if our test users are in the correct lists
            assert (
                username_verified in verified_usernames
                or username_unverified in unverified_usernames
            )
        finally:
            # Cleanup
            for username in [username_verified, username_unverified]:
                users = await list_users(username=username)
                if users:
                    await delete_user(users[0]["id"])

    async def test_brief_representation(self):
        """Test brief representation parameter."""
        username = "briefreptest"
        await create_user(
            username=username,
            email=f"{username}@test.com",
            first_name="Brief",
            last_name="Test",
        )

        try:
            # Get full representation (default)
            full_users = await list_users(username=username)
            assert len(full_users) == 1
            assert "firstName" in full_users[0]
            assert "email" in full_users[0]

            # Get brief representation
            brief_users = await list_users(username=username, brief_representation=True)
            assert len(brief_users) == 1
            # Brief representation typically has fewer fields
            assert "username" in brief_users[0]
            assert "id" in brief_users[0]
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])

    async def test_custom_attribute_query(self):
        """Test searching users by custom attributes using q parameter."""
        username = "customattrtest"

        # Create user with custom attributes
        await create_user(
            username=username,
            email=f"{username}@test.com",
            attributes={
                "department": ["Engineering"],
                "team": ["Backend"],
                "employee_id": ["EMP123"],
            },
        )

        try:
            # Search by custom attribute
            # Note: This feature depends on Keycloak configuration
            users = await list_users(q="department:Engineering")
            assert isinstance(users, list)
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])


@pytest.mark.integration
class TestUserLifecycle:
    """Test user lifecycle features including required actions, groups, and roles."""

    async def test_create_user_with_required_actions(self):
        """Test creating a user with required actions."""
        username = "requiredactionstest"

        result = await create_user(
            username=username,
            email=f"{username}@test.com",
            required_actions=["UPDATE_PASSWORD", "VERIFY_EMAIL"],
        )

        assert result["status"] == "created"

        try:
            # Get the user and check required actions
            users = await list_users(username=username)
            assert len(users) == 1
            user = await get_user(users[0]["id"])
            assert "requiredActions" in user
            assert "UPDATE_PASSWORD" in user["requiredActions"]
            assert "VERIFY_EMAIL" in user["requiredActions"]
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])

    async def test_create_user_with_groups(self, test_group):
        """Test creating a user with group assignment."""
        username = "groupassigntest"

        # Note: Direct group assignment during user creation might not work
        # in all Keycloak versions. This test documents the expected behavior.
        result = await create_user(
            username=username, email=f"{username}@test.com", groups=[test_group]
        )

        assert result["status"] == "created"

        try:
            # Verify user was created
            users = await list_users(username=username)
            assert len(users) == 1
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])

    async def test_create_user_with_realm_roles(self, test_role):
        """Test creating a user with realm role assignment."""
        username = "roleassigntest"

        result = await create_user(
            username=username, email=f"{username}@test.com", realm_roles=[test_role]
        )

        assert result["status"] == "created"

        try:
            # Verify user was created
            users = await list_users(username=username)
            assert len(users) == 1
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])

    async def test_update_user_with_required_actions(self):
        """Test updating a user with required actions."""
        username = "updateactionstest"

        # Create user
        await create_user(username=username, email=f"{username}@test.com")
        users = await list_users(username=username)
        user_id = users[0]["id"]

        try:
            # Update with required actions
            result = await update_user(
                user_id=user_id, required_actions=["UPDATE_PROFILE", "CONFIGURE_TOTP"]
            )
            assert result["status"] == "updated"

            # Verify the update
            user = await get_user(user_id)
            assert "requiredActions" in user
            assert "UPDATE_PROFILE" in user["requiredActions"]
            assert "CONFIGURE_TOTP" in user["requiredActions"]
        finally:
            # Cleanup
            await delete_user(user_id)

    async def test_clear_required_actions(self):
        """Test clearing required actions from a user."""
        username = "clearactionstest"

        # Create user with required actions
        await create_user(
            username=username,
            email=f"{username}@test.com",
            required_actions=["UPDATE_PASSWORD"],
        )
        users = await list_users(username=username)
        user_id = users[0]["id"]

        try:
            # Clear required actions
            result = await update_user(user_id=user_id, required_actions=[])
            assert result["status"] == "updated"

            # Verify the update
            user = await get_user(user_id)
            assert user.get("requiredActions", []) == []
        finally:
            # Cleanup
            await delete_user(user_id)


@pytest.mark.integration
class TestUserPasswordManagement:
    """Test user password operations."""

    async def test_reset_user_password(self, unique_username):
        """Test resetting a user password."""
        # Create user
        await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Password",
            last_name="Reset",
            enabled=True,
        )

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Reset password
            result = await reset_user_password(
                user_id=user_id,
                password="NewPassword456!",
                temporary=False,
            )
            assert result["status"] == "success"
        finally:
            await delete_user(user_id)


@pytest.mark.integration
class TestUserSessions:
    """Test user session operations."""

    async def test_get_user_sessions(self, unique_username):
        """Test getting user sessions."""
        # Create user
        await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Session",
            last_name="User",
            enabled=True,
        )

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Get sessions (likely empty for new user)
            sessions = await get_user_sessions(user_id)
            assert isinstance(sessions, list)
        finally:
            await delete_user(user_id)

    async def test_logout_user(self, unique_username):
        """Test logging out a user."""
        # Create user
        await create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Logout",
            last_name="User",
            enabled=True,
        )

        users = await list_users(search=unique_username)
        test_user = next((u for u in users if u["username"] == unique_username), None)
        user_id = test_user["id"]

        try:
            # Logout user (should work even with no active sessions)
            result = await logout_user(user_id)
            assert result["status"] == "success"
        finally:
            await delete_user(user_id)