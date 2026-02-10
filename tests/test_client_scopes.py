"""
Integration tests for Client Scopes.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_scope_tools, client_tools

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
    def unique_scope_name():
        """Generate a unique scope name for testing."""
        return f"test-scope-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_client_id():
        """Generate a unique client ID for testing."""
        return f"test-client-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientScopes:
    """Test client scope management."""

    async def test_client_scope_lifecycle(self, unique_scope_name):
        """Test creating, reading, updating, and deleting a client scope."""
        # Create client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name,
            description="Test scope for integration testing",
            protocol="openid-connect",
        )
        assert result["status"] == "created"

        # List client scopes and find our scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        assert test_scope is not None
        scope_id = test_scope["id"]

        # Get specific client scope
        scope = await client_scope_tools.get_client_scope(scope_id)
        assert scope["name"] == unique_scope_name
        assert scope["description"] == "Test scope for integration testing"

        # Update client scope
        result = await client_scope_tools.update_client_scope(
            scope_id=scope_id, description="Updated test scope description"
        )
        assert result["status"] == "updated"

        # Verify update
        scope = await client_scope_tools.get_client_scope(scope_id)
        assert scope["description"] == "Updated test scope description"

        # Delete client scope
        result = await client_scope_tools.delete_client_scope(scope_id)
        assert result["status"] == "deleted"

        # Verify deletion
        scopes = await client_scope_tools.list_client_scopes()
        assert not any(s["name"] == unique_scope_name for s in scopes)

    async def test_realm_default_scopes(self, unique_scope_name):
        """Test managing realm default client scopes."""
        # Create a client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name,
            description="Test default scope",
            protocol="openid-connect",
        )
        assert result["status"] == "created"

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Add as realm default
            result = await client_scope_tools.add_realm_default_client_scope(scope_id)
            assert result["status"] == "added"

            # Get realm default scopes
            defaults = await client_scope_tools.get_realm_default_client_scopes()
            assert any(s["id"] == scope_id for s in defaults)

            # Remove from realm defaults
            result = await client_scope_tools.remove_realm_default_client_scope(
                scope_id
            )
            assert result["status"] == "removed"

            # Verify removal
            defaults = await client_scope_tools.get_realm_default_client_scopes()
            assert not any(s["id"] == scope_id for s in defaults)

        finally:
            # Clean up
            await client_scope_tools.delete_client_scope(scope_id)

    async def test_realm_optional_scopes(self, unique_scope_name):
        """Test managing realm optional client scopes."""
        # Create a client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name,
            description="Test optional scope",
            protocol="openid-connect",
        )
        assert result["status"] == "created"

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Add as realm optional
            result = await client_scope_tools.add_realm_optional_client_scope(scope_id)
            assert result["status"] == "added"

            # Get realm optional scopes
            optional = await client_scope_tools.get_realm_optional_client_scopes()
            assert any(s["id"] == scope_id for s in optional)

            # Remove from realm optional
            result = await client_scope_tools.remove_realm_optional_client_scope(
                scope_id
            )
            assert result["status"] == "removed"

            # Verify removal
            optional = await client_scope_tools.get_realm_optional_client_scopes()
            assert not any(s["id"] == scope_id for s in optional)

        finally:
            # Clean up
            await client_scope_tools.delete_client_scope(scope_id)


@pytest.mark.integration
class TestClientScopeAssignment:
    """Test client scope assignment to clients."""

    async def test_client_scope_assignment(self, unique_client_id, unique_scope_name):
        """Test assigning client scopes to clients."""
        # Create client
        client_result = await client_tools.create_client(
            client_id=unique_client_id, name="Test Client", public_client=True
        )
        assert client_result["status"] == "created"

        # Get client
        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        # Create client scope
        scope_result = await client_scope_tools.create_client_scope(
            name=unique_scope_name, protocol="openid-connect"
        )
        assert scope_result["status"] == "created"

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Add scope as default to client
            result = await client_scope_tools.add_client_default_scope(
                client_id=client_db_id, scope_id=scope_id
            )
            assert result["status"] == "added"

            # Get client default scopes
            defaults = await client_scope_tools.get_client_default_scopes(client_db_id)
            assert any(s["id"] == scope_id for s in defaults)

            # Remove from defaults and add as optional
            await client_scope_tools.remove_client_default_scope(client_db_id, scope_id)
            result = await client_scope_tools.add_client_optional_scope(
                client_id=client_db_id, scope_id=scope_id
            )
            assert result["status"] == "added"

            # Get client optional scopes
            optional = await client_scope_tools.get_client_optional_scopes(client_db_id)
            assert any(s["id"] == scope_id for s in optional)

            # Remove from optional
            result = await client_scope_tools.remove_client_optional_scope(
                client_db_id, scope_id
            )
            assert result["status"] == "removed"

        finally:
            # Clean up
            await client_tools.delete_client(client_db_id)
            await client_scope_tools.delete_client_scope(scope_id)


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Client Scopes Integration Tests ===\n")

    test_scopes = TestClientScopes()
    test_assignment = TestClientScopeAssignment()

    tests = [
        ("Client scope lifecycle", test_scopes.test_client_scope_lifecycle),
        ("Realm default scopes", test_scopes.test_realm_default_scopes),
        ("Realm optional scopes", test_scopes.test_realm_optional_scopes),
    ]

    for name, test_func in tests:
        scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
        print(f"Testing {name}...")
        try:
            await test_func(scope_name)
            print(f"[PASS] {name} test passed")
        except Exception as e:
            print(f"[FAIL] {name} test failed: {e}")

    # Test client scope assignment
    print("\nTesting client scope assignment...")
    try:
        await test_assignment.test_client_scope_assignment(
            f"test-client-{uuid.uuid4().hex[:8]}",
            f"test-scope-{uuid.uuid4().hex[:8]}",
        )
        print("[PASS] Client scope assignment test passed")
    except Exception as e:
        print(f"[FAIL] Client scope assignment test failed: {e}")

    print("\n=== Client Scopes Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
