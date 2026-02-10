"""
Integration tests for Role Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import role_tools, user_tools, client_tools

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
    def unique_role_name():
        """Generate a unique role name for testing."""
        return f"test-role-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_username():
        """Generate a unique username for testing."""
        return f"test-user-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_client_id():
        """Generate a unique client ID for testing."""
        return f"test-client-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestRealmRoles:
    """Test realm role operations."""

    async def test_realm_role_lifecycle(self, unique_role_name):
        """Test creating, reading, updating and deleting a realm role."""
        # Create realm role
        result = await role_tools.create_realm_role(
            name=unique_role_name,
            description="Test realm role for integration testing",
        )
        assert result["status"] == "created"

        try:
            # Get realm role
            role = await role_tools.get_realm_role(unique_role_name)
            assert role["name"] == unique_role_name
            assert role["description"] == "Test realm role for integration testing"

            # Update realm role
            update_result = await role_tools.update_realm_role(
                role_name=unique_role_name,
                description="Updated test realm role",
            )
            assert update_result["status"] == "updated"

            # Verify update
            role = await role_tools.get_realm_role(unique_role_name)
            assert role["description"] == "Updated test realm role"

            # List realm roles and verify our role is there
            roles = await role_tools.list_realm_roles(search=unique_role_name)
            assert any(r["name"] == unique_role_name for r in roles)

        finally:
            # Delete realm role
            delete_result = await role_tools.delete_realm_role(unique_role_name)
            assert delete_result["status"] == "deleted"

            # Verify deletion - should not find the role
            roles = await role_tools.list_realm_roles(search=unique_role_name)
            assert not any(r["name"] == unique_role_name for r in roles)

    async def test_list_realm_roles(self):
        """Test listing realm roles with pagination."""
        roles = await role_tools.list_realm_roles(max=10)
        assert isinstance(roles, list)
        assert len(roles) <= 10


@pytest.mark.integration
class TestClientRoles:
    """Test client-specific role operations."""

    async def test_client_role_lifecycle(self, unique_client_id, unique_role_name):
        """Test creating and managing client-specific roles."""
        # Create a test client first
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Test Client for Roles",
            enabled=True,
        )

        # Get client UUID
        clients = await client_tools.list_clients(client_id=unique_client_id)
        client = next(c for c in clients if c["clientId"] == unique_client_id)
        client_uuid = client["id"]

        try:
            # Create client role
            result = await role_tools.create_client_role(
                client_id=client_uuid,
                name=unique_role_name,
                description="Test client role",
            )
            assert result["status"] == "created"

            # Get client role
            role = await role_tools.get_client_role(
                client_id=client_uuid, role_name=unique_role_name
            )
            assert role["name"] == unique_role_name
            assert role["description"] == "Test client role"

            # List client roles
            roles = await role_tools.list_client_roles(client_id=client_uuid)
            assert any(r["name"] == unique_role_name for r in roles)

        finally:
            # Clean up client (this will also delete its roles)
            await client_tools.delete_client(client_uuid)


@pytest.mark.integration
class TestRoleAssignments:
    """Test role assignment to users."""

    async def test_assign_realm_role_to_user(self, unique_username, unique_role_name):
        """Test assigning and removing realm roles from users."""
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

        # Create test realm role
        await role_tools.create_realm_role(
            name=unique_role_name,
            description="Test role for assignment",
        )

        try:
            # Get role details
            role = await role_tools.get_realm_role(unique_role_name)

            # Assign realm role to user
            result = await role_tools.assign_realm_role_to_user(
                user_id=user_id, role_names=[unique_role_name]
            )
            assert result["status"] == "assigned"

            # Get user roles and verify
            user_roles = await role_tools.get_user_realm_roles(user_id)
            assert any(r["name"] == unique_role_name for r in user_roles)

            # Remove realm role from user
            remove_result = await role_tools.remove_realm_role_from_user(
                user_id=user_id, role_names=[unique_role_name]
            )
            assert remove_result["status"] == "removed"

            # Verify removal
            user_roles = await role_tools.get_user_realm_roles(user_id)
            assert not any(r["name"] == unique_role_name for r in user_roles)

        finally:
            # Clean up
            await role_tools.delete_realm_role(unique_role_name)
            await user_tools.delete_user(user_id)

    async def test_assign_client_role_to_user(
        self, unique_username, unique_client_id, unique_role_name
    ):
        """Test assigning client roles to users."""
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

        # Create test client
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Test Client",
            enabled=True,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        client = next(c for c in clients if c["clientId"] == unique_client_id)
        client_uuid = client["id"]

        # Create client role
        await role_tools.create_client_role(
            client_id=client_uuid,
            name=unique_role_name,
            description="Test client role",
        )

        try:
            # Assign client role to user
            result = await role_tools.assign_client_role_to_user(
                user_id=user_id, client_id=client_uuid, role_names=[unique_role_name]
            )
            assert result["status"] == "assigned"

        finally:
            # Clean up
            await client_tools.delete_client(client_uuid)
            await user_tools.delete_user(user_id)
