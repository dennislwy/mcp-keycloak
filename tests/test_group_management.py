"""
Integration tests for Group Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import group_tools, user_tools, role_tools

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
    def unique_group_name():
        """Generate a unique group name for testing."""
        return f"test-group-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_username():
        """Generate a unique username for testing."""
        return f"test-user-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_role_name():
        """Generate a unique role name for testing."""
        return f"test-role-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestGroupLifecycle:
    """Test group CRUD operations."""

    async def test_create_and_delete_group(self, unique_group_name):
        """Test creating and deleting a group."""
        # Create group
        result = await group_tools.create_group(
            name=unique_group_name,
        )
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Get group
            group_detail = await group_tools.get_group(group_id)
            assert group_detail["name"] == unique_group_name

            # List groups and verify
            groups = await group_tools.list_groups(search=unique_group_name)
            assert any(g["name"] == unique_group_name for g in groups)

        finally:
            # Delete group
            delete_result = await group_tools.delete_group(group_id)
            assert delete_result["status"] == "deleted"

    async def test_update_group(self, unique_group_name):
        """Test updating group attributes."""
        # Create group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Update group with attributes
            update_result = await group_tools.update_group(
                group_id=group_id,
                attributes={"description": ["Updated test group"]},
            )
            assert update_result["status"] == "updated"

            # Verify update
            group = await group_tools.get_group(group_id)
            assert "description" in group.get("attributes", {})

        finally:
            await group_tools.delete_group(group_id)

    async def test_list_groups(self):
        """Test listing groups."""
        groups = await group_tools.list_groups(max=10)
        assert isinstance(groups, list)


@pytest.mark.integration
class TestGroupMembers:
    """Test group membership operations."""

    async def test_add_and_remove_user_from_group(
        self, unique_group_name, unique_username
    ):
        """Test adding and removing users from groups."""
        # Create test user
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

        # Create test group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Add user to group
            add_result = await group_tools.add_user_to_group(
                user_id=user_id, group_id=group_id
            )
            assert add_result["status"] == "added"

            # Get group members and verify
            members = await group_tools.get_group_members(group_id)
            assert any(m["id"] == user_id for m in members)

            # Get user groups and verify
            user_groups = await group_tools.get_user_groups(user_id)
            assert any(g["id"] == group_id for g in user_groups)

            # Remove user from group
            remove_result = await group_tools.remove_user_from_group(
                user_id=user_id, group_id=group_id
            )
            assert remove_result["status"] == "removed"

            # Verify removal
            members = await group_tools.get_group_members(group_id)
            assert not any(m["id"] == user_id for m in members)

        finally:
            await group_tools.delete_group(group_id)
            await user_tools.delete_user(user_id)


@pytest.mark.integration
class TestGroupRoles:
    """Test group role mappings."""

    async def test_assign_realm_roles_to_group(
        self, unique_group_name, unique_role_name
    ):
        """Test assigning and removing realm roles from groups."""
        # Create test group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        # Create test realm role
        await role_tools.create_realm_role(
            name=unique_role_name,
            description="Test role for group assignment",
        )

        try:
            # Get role details
            role = await role_tools.get_realm_role(unique_role_name)

            # Assign realm role to group
            add_result = await group_tools.add_realm_roles_to_group(
                group_id=group_id, role_names=[unique_role_name]
            )
            assert add_result["status"] == "assigned"

            # Get group realm roles and verify
            group_roles = await group_tools.get_group_realm_roles(group_id)
            assert any(r["name"] == unique_role_name for r in group_roles)

            # Get group role mappings (full)
            role_mappings = await group_tools.get_group_role_mappings(group_id)
            assert "realmMappings" in role_mappings

            # Remove realm role from group
            remove_result = await group_tools.remove_realm_roles_from_group(
                group_id=group_id, role_names=[unique_role_name]
            )
            assert remove_result["status"] == "removed"

            # Verify removal
            group_roles = await group_tools.get_group_realm_roles(group_id)
            assert not any(r["name"] == unique_role_name for r in group_roles)

        finally:
            await group_tools.delete_group(group_id)
            await role_tools.delete_realm_role(unique_role_name)

    async def test_get_available_and_effective_realm_roles(self, unique_group_name):
        """Test getting available and effective realm roles for a group."""
        # Create test group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Get available realm roles (roles that can be assigned)
            available_roles = await group_tools.get_group_available_realm_roles(
                group_id
            )
            assert isinstance(available_roles, list)

            # Get effective realm roles (includes inherited)
            effective_roles = await group_tools.get_group_effective_realm_roles(
                group_id
            )
            assert isinstance(effective_roles, list)

        finally:
            await group_tools.delete_group(group_id)

    async def test_get_all_group_roles(self, unique_group_name):
        """Test getting all roles (realm and client) for a group."""
        # Create test group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Get all roles (realm and client combined)
            all_roles = await group_tools.get_group_all_roles(group_id)
            assert isinstance(all_roles, dict)
            assert "realm_roles" in all_roles
            assert "client_roles" in all_roles
            assert "total_roles" in all_roles

        finally:
            await group_tools.delete_group(group_id)
