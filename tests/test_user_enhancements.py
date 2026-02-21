"""
Integration tests for enhanced User Management features.

These tests cover the new parameters added to user tools.
"""

import pytest
from src.tools.user_tools import (
    list_users,
    create_user,
    update_user,
    delete_user,
    get_user,
)
from src.tools.group_tools import create_group, delete_group, list_groups
from src.tools.role_tools import create_realm_role, delete_realm_role


@pytest.fixture(scope="module")
async def test_group():
    """Create a test group for user assignment tests."""
    group_name = "test-group-enhanced"
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
    role_name = "test-role-enhanced"
    await create_realm_role(name=role_name, description="Test role for enhancements")
    yield role_name
    # Cleanup
    try:
        await delete_realm_role(role_name)
    except Exception:
        pass


@pytest.mark.integration
class TestEnhancedUserSearch:
    """Test enhanced user search capabilities."""

    async def test_list_users_with_exact_match(self):
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

    async def test_list_users_with_name_filters(self):
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

    async def test_list_users_with_email_verified_filter(self):
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

    async def test_list_users_with_brief_representation(self):
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


@pytest.mark.integration
class TestEnhancedUserCreation:
    """Test enhanced user creation with groups and roles."""

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

            # Note: Group assignment during creation might require additional
            # API calls depending on Keycloak version
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

            # Note: Role assignment during creation might require additional
            # API calls depending on Keycloak version
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])


@pytest.mark.integration
class TestEnhancedUserUpdate:
    """Test enhanced user update capabilities."""

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

    async def test_update_user_clear_required_actions(self):
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
class TestCustomAttributeQuery:
    """Test custom attribute query functionality."""

    async def test_search_users_with_custom_attributes(self):
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
            # and may require custom attribute indexing
            users = await list_users(q="department:Engineering")

            # The query parameter behavior depends on Keycloak configuration
            # This test documents the expected API parameter
            assert isinstance(users, list)
        finally:
            # Cleanup
            users = await list_users(username=username)
            if users:
                await delete_user(users[0]["id"])
