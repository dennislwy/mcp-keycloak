"""
Integration tests for Role Composite Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_tools, role_tools

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
    async def test_realm_roles():
        """Create test realm roles for composite testing."""
        role_names = [f"test-realm-role-{i}-{uuid.uuid4().hex[:8]}" for i in range(4)]

        # Create roles
        for role_name in role_names:
            await role_tools.create_realm_role(
                name=role_name,
                description=f"Test role {role_name}",
                composite=False,
            )

        # Get role representations
        roles = []
        for role_name in role_names:
            role = await role_tools.get_realm_role(role_name)
            roles.append(role)

        yield roles

        # Cleanup
        for role_name in role_names:
            try:
                await role_tools.delete_realm_role(role_name)
            except Exception:
                pass

    @pytest.fixture(scope="module")
    async def test_client_with_roles():
        """Create a test client with roles for composite testing."""
        client_id = f"test-client-{uuid.uuid4().hex[:8]}"

        # Create client
        await client_tools.create_client(
            client_id=client_id,
            name="Test Client for Composites",
            enabled=True,
            protocol="openid-connect",
        )

        # Get client database ID
        clients = await client_tools.list_clients(client_id=client_id)
        test_client = next((c for c in clients if c["clientId"] == client_id), None)
        client_db_id = test_client["id"]

        # Create test client roles
        role_names = [f"test-client-role-{i}-{uuid.uuid4().hex[:4]}" for i in range(3)]
        for role_name in role_names:
            await role_tools.create_client_role(
                client_id=client_db_id,
                name=role_name,
                description=f"Test client role {role_name}",
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


@pytest.mark.integration
class TestRoleCompositeLifecycle:
    """Test role composite operations."""

    async def test_add_and_remove_composites(self, test_realm_roles):
        """Test adding and removing composite roles."""
        composite_role_name = f"test-composite-{uuid.uuid4().hex[:8]}"

        try:
            # Create composite role
            await role_tools.create_realm_role(
                name=composite_role_name,
                description="Test composite role",
                composite=True,
            )

            # Add composites (first 2 roles)
            roles_to_add = test_realm_roles[:2]
            result = await role_tools.add_role_composites(
                role_name=composite_role_name, roles=roles_to_add
            )
            assert result["status"] == "added"
            assert "2 composite roles added" in result["message"]

            # List composites
            composites = await role_tools.list_role_composites(composite_role_name)
            assert len(composites) >= 2
            composite_names = {r["name"] for r in composites}
            for role in roles_to_add:
                assert role["name"] in composite_names

            # Remove composites
            result = await role_tools.delete_role_composites(
                role_name=composite_role_name, roles=roles_to_add
            )
            assert result["status"] == "deleted"

            # Verify removal
            composites = await role_tools.list_role_composites(composite_role_name)
            composite_names = {r["name"] for r in composites}
            for role in roles_to_add:
                assert role["name"] not in composite_names

        finally:
            # Clean up composite role
            try:
                await role_tools.delete_realm_role(composite_role_name)
            except Exception:
                pass

    async def test_list_empty_composites(self, test_realm_roles):
        """Test listing composites for a non-composite role."""
        # Get composites for a simple (non-composite) role
        composites = await role_tools.list_role_composites(test_realm_roles[0]["name"])
        # Should be empty for non-composite roles
        assert isinstance(composites, list)
        assert len(composites) == 0

    async def test_add_multiple_composites(self, test_realm_roles):
        """Test adding multiple composite roles at once."""
        composite_role_name = f"test-composite-{uuid.uuid4().hex[:8]}"

        try:
            # Create composite role
            await role_tools.create_realm_role(
                name=composite_role_name,
                description="Multi-composite test",
                composite=True,
            )

            # Add all test roles as composites
            result = await role_tools.add_role_composites(
                role_name=composite_role_name, roles=test_realm_roles
            )
            assert result["status"] == "added"

            # Verify all were added
            composites = await role_tools.list_role_composites(composite_role_name)
            composite_names = {r["name"] for r in composites}
            for role in test_realm_roles:
                assert role["name"] in composite_names

        finally:
            try:
                await role_tools.delete_realm_role(composite_role_name)
            except Exception:
                pass


@pytest.mark.integration
class TestRoleCompositeRealmAndClient:
    """Test realm-level and client-level composite queries."""

    async def test_get_realm_composites(self, test_realm_roles):
        """Test getting realm-level roles in a composite."""
        composite_role_name = f"test-composite-{uuid.uuid4().hex[:8]}"

        try:
            # Create composite role
            await role_tools.create_realm_role(
                name=composite_role_name,
                description="Realm composite test",
                composite=True,
            )

            # Add realm roles as composites
            roles_to_add = test_realm_roles[:2]
            await role_tools.add_role_composites(
                role_name=composite_role_name, roles=roles_to_add
            )

            # Get realm-level composites
            realm_composites = await role_tools.get_role_composites_realm(
                composite_role_name
            )
            assert isinstance(realm_composites, list)
            assert len(realm_composites) >= 2

            # Verify our roles are in the list
            composite_names = {r["name"] for r in realm_composites}
            for role in roles_to_add:
                assert role["name"] in composite_names

        finally:
            try:
                await role_tools.delete_realm_role(composite_role_name)
            except Exception:
                pass

    async def test_get_client_composites(
        self, test_realm_roles, test_client_with_roles
    ):
        """Test getting client-level roles in a composite."""
        composite_role_name = f"test-composite-{uuid.uuid4().hex[:8]}"

        try:
            # Create composite role
            await role_tools.create_realm_role(
                name=composite_role_name,
                description="Client composite test",
                composite=True,
            )

            # Add client roles as composites
            client_roles = test_client_with_roles["roles"]
            await role_tools.add_role_composites(
                role_name=composite_role_name, roles=client_roles
            )

            # Get client-level composites
            client_composites = await role_tools.get_role_composites_clients(
                role_name=composite_role_name, client_id=test_client_with_roles["id"]
            )
            assert isinstance(client_composites, list)
            assert len(client_composites) >= len(client_roles)

            # Verify our client roles are in the list
            composite_names = {r["name"] for r in client_composites}
            for role in client_roles:
                assert role["name"] in composite_names

        finally:
            try:
                await role_tools.delete_realm_role(composite_role_name)
            except Exception:
                pass

    async def test_mixed_composites(self, test_realm_roles, test_client_with_roles):
        """Test a composite role with both realm and client roles."""
        composite_role_name = f"test-composite-{uuid.uuid4().hex[:8]}"

        try:
            # Create composite role
            await role_tools.create_realm_role(
                name=composite_role_name,
                description="Mixed composite test",
                composite=True,
            )

            # Add both realm and client roles
            realm_roles = test_realm_roles[:2]
            client_roles = test_client_with_roles["roles"][:2]
            all_roles = realm_roles + client_roles

            await role_tools.add_role_composites(
                role_name=composite_role_name, roles=all_roles
            )

            # Get all composites
            all_composites = await role_tools.list_role_composites(composite_role_name)
            assert len(all_composites) >= len(all_roles)

            # Get realm composites only
            realm_composites = await role_tools.get_role_composites_realm(
                composite_role_name
            )
            realm_composite_names = {r["name"] for r in realm_composites}
            for role in realm_roles:
                assert role["name"] in realm_composite_names

            # Get client composites only
            client_composites = await role_tools.get_role_composites_clients(
                role_name=composite_role_name, client_id=test_client_with_roles["id"]
            )
            client_composite_names = {r["name"] for r in client_composites}
            for role in client_roles:
                assert role["name"] in client_composite_names

        finally:
            try:
                await role_tools.delete_realm_role(composite_role_name)
            except Exception:
                pass
