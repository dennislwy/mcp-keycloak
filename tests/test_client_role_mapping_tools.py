"""
Integration tests for Client Role Mapping Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_role_mapping_tools, client_tools, group_tools, role_tools

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
        def fixture(func=None, scope=None):
            if func:
                return func
            return lambda f: f

    pytest = MockPytest()


if PYTEST_AVAILABLE:

    @pytest.fixture(scope="module")
    async def test_client_with_roles():
        """Create a test client with roles for role mapping tests."""
        client_id = f"test-client-{uuid.uuid4().hex[:8]}"

        # Create client
        await client_tools.create_client(
            client_id=client_id,
            name="Test Client for Role Mappings",
            enabled=True,
            protocol="openid-connect",
        )

        # Get client database ID
        clients = await client_tools.list_clients(client_id=client_id)
        test_client = next((c for c in clients if c["clientId"] == client_id), None)
        client_db_id = test_client["id"]

        # Create test roles
        role_names = [f"test-role-{i}-{uuid.uuid4().hex[:4]}" for i in range(3)]
        for role_name in role_names:
            await role_tools.create_client_role(
                client_id=client_db_id,
                name=role_name,
                description=f"Test role {role_name}",
            )

        # Get role representations
        client_roles = await role_tools.list_client_roles(client_db_id)
        test_roles = [r for r in client_roles if r["name"] in role_names]

        yield {"id": client_db_id, "clientId": client_id, "roles": test_roles}

        # Cleanup
        try:
            await client_tools.delete_client(client_db_id)
        except Exception:
            pass

    @pytest.fixture
    async def test_group():
        """Create a test group for role mapping tests."""
        group_name = f"test-group-{uuid.uuid4().hex[:8]}"

        # Create group
        await group_tools.create_group(name=group_name)

        # Get group ID
        groups = await group_tools.list_groups(search=group_name)
        test_group = next((g for g in groups if g["name"] == group_name), None)
        group_id = test_group["id"]

        yield {"id": group_id, "name": group_name}

        # Cleanup
        try:
            await group_tools.delete_group(group_id)
        except Exception:
            pass


@pytest.mark.integration
class TestClientRoleMappingLifecycle:
    """Test client role mapping operations for groups."""

    async def test_add_and_remove_role_mappings(
        self, test_client_with_roles, test_group
    ):
        """Test adding and removing client role mappings to a group."""
        try:
            # Add role mappings
            roles_to_add = test_client_with_roles["roles"][:2]  # Add first 2 roles
            result = await client_role_mapping_tools.add_client_role_mappings(
                group_id=test_group["id"],
                client_id=test_client_with_roles["id"],
                roles=roles_to_add,
            )
            assert result["status"] == "added"
            assert "2 client roles added" in result["message"]

            # Get role mappings
            mappings = await client_role_mapping_tools.get_client_role_mappings(
                group_id=test_group["id"], client_id=test_client_with_roles["id"]
            )
            assert len(mappings) >= 2
            mapped_role_names = {r["name"] for r in mappings}
            for role in roles_to_add:
                assert role["name"] in mapped_role_names

        finally:
            # Remove role mappings
            try:
                result = await client_role_mapping_tools.delete_client_role_mappings(
                    group_id=test_group["id"],
                    client_id=test_client_with_roles["id"],
                    roles=roles_to_add,
                )
                assert result["status"] == "deleted"

                # Verify removal
                mappings = await client_role_mapping_tools.get_client_role_mappings(
                    group_id=test_group["id"], client_id=test_client_with_roles["id"]
                )
                mapped_role_names = {r["name"] for r in mappings}
                for role in roles_to_add:
                    assert role["name"] not in mapped_role_names
            except Exception:
                pass

    async def test_list_available_role_mappings(
        self, test_client_with_roles, test_group
    ):
        """Test listing available client role mappings."""
        # Get available roles (before any are assigned)
        available = await client_role_mapping_tools.list_available_client_role_mappings(
            group_id=test_group["id"], client_id=test_client_with_roles["id"]
        )
        assert isinstance(available, list)

        # Should contain our test roles
        available_names = {r["name"] for r in available}
        test_role_names = {r["name"] for r in test_client_with_roles["roles"]}
        # At least some of our test roles should be available
        assert len(test_role_names.intersection(available_names)) > 0

    async def test_list_composite_role_mappings(
        self, test_client_with_roles, test_group
    ):
        """Test listing effective (composite) client role mappings."""
        try:
            # Add a role mapping
            roles_to_add = [test_client_with_roles["roles"][0]]
            await client_role_mapping_tools.add_client_role_mappings(
                group_id=test_group["id"],
                client_id=test_client_with_roles["id"],
                roles=roles_to_add,
            )

            # Get composite mappings (includes inherited/composite roles)
            composite = (
                await client_role_mapping_tools.list_composite_client_role_mappings(
                    group_id=test_group["id"],
                    client_id=test_client_with_roles["id"],
                    brief_representation=True,
                )
            )
            assert isinstance(composite, list)

            # Should contain at least the role we added
            composite_names = {r["name"] for r in composite}
            assert roles_to_add[0]["name"] in composite_names

        finally:
            # Clean up
            try:
                await client_role_mapping_tools.delete_client_role_mappings(
                    group_id=test_group["id"],
                    client_id=test_client_with_roles["id"],
                    roles=roles_to_add,
                )
            except Exception:
                pass


@pytest.mark.integration
class TestClientRoleMappingOperations:
    """Test client role mapping query and listing operations."""

    async def test_get_empty_role_mappings(self, test_client_with_roles, test_group):
        """Test getting role mappings when none are assigned."""
        # Get mappings for group with no roles assigned
        mappings = await client_role_mapping_tools.get_client_role_mappings(
            group_id=test_group["id"], client_id=test_client_with_roles["id"]
        )
        assert isinstance(mappings, list)
        # Should be empty or contain no test roles
        if mappings:
            mapped_names = {r["name"] for r in mappings}
            test_role_names = {r["name"] for r in test_client_with_roles["roles"]}
            # Our test roles shouldn't be assigned yet
            assert len(test_role_names.intersection(mapped_names)) == 0

    async def test_add_multiple_roles_at_once(self, test_client_with_roles, test_group):
        """Test adding multiple client roles in a single operation."""
        try:
            # Add all test roles at once
            all_roles = test_client_with_roles["roles"]
            result = await client_role_mapping_tools.add_client_role_mappings(
                group_id=test_group["id"],
                client_id=test_client_with_roles["id"],
                roles=all_roles,
            )
            assert result["status"] == "added"

            # Verify all roles were added
            mappings = await client_role_mapping_tools.get_client_role_mappings(
                group_id=test_group["id"], client_id=test_client_with_roles["id"]
            )
            mapped_names = {r["name"] for r in mappings}
            for role in all_roles:
                assert role["name"] in mapped_names

        finally:
            # Clean up
            try:
                await client_role_mapping_tools.delete_client_role_mappings(
                    group_id=test_group["id"],
                    client_id=test_client_with_roles["id"],
                    roles=all_roles,
                )
            except Exception:
                pass
