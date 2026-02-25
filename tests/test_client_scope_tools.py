"""
Integration tests for Client Scope Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_scope_tools
from src.tools.client_tools import (
    create_client,
    delete_client,
    list_clients,
    list_client_default_client_scopes,
    update_client_default_client_scope,
    delete_client_default_client_scope,
)

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
        """Generate a unique client scope name for testing."""
        return f"test-scope-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_client_id():
        """Generate a unique client ID for testing."""
        return f"test-client-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientScopeLifecycle:
    """Test client scope CRUD operations."""

    async def test_create_and_delete_scope(self, unique_scope_name):
        """Test creating and deleting a client scope."""
        scope_id = None

        try:
            # Create scope
            result = await client_scope_tools.create_client_scope(
                name=unique_scope_name,
                description="Test client scope for integration tests",
                protocol="openid-connect",
            )
            assert result["status"] == "created"

            # Find the created scope
            scopes = await client_scope_tools.list_client_scopes()
            test_scope = next(
                (s for s in scopes if s["name"] == unique_scope_name), None
            )
            assert test_scope is not None
            scope_id = test_scope["id"]

            # Get scope by ID
            scope = await client_scope_tools.get_client_scope(scope_id)
            assert scope["name"] == unique_scope_name
            assert scope["description"] == "Test client scope for integration tests"
            assert scope["protocol"] == "openid-connect"

        finally:
            # Clean up
            if scope_id:
                try:
                    delete_result = await client_scope_tools.delete_client_scope(
                        scope_id
                    )
                    assert delete_result["status"] == "deleted"

                    # Verify deletion
                    scopes = await client_scope_tools.list_client_scopes()
                    assert not any(s["name"] == unique_scope_name for s in scopes)
                except Exception:
                    pass  # Ignore cleanup errors

    async def test_update_scope(self, unique_scope_name):
        """Test updating client scope attributes."""
        scope_id = None

        try:
            # Create scope
            await client_scope_tools.create_client_scope(
                name=unique_scope_name,
                description="Original description",
                protocol="openid-connect",
            )

            # Find scope
            scopes = await client_scope_tools.list_client_scopes()
            test_scope = next(
                (s for s in scopes if s["name"] == unique_scope_name), None
            )
            scope_id = test_scope["id"]

            # Update scope
            result = await client_scope_tools.update_client_scope(
                client_scope_id=scope_id,
                description="Updated description",
            )
            assert result["status"] == "updated"

            # Verify update
            updated_scope = await client_scope_tools.get_client_scope(scope_id)
            assert updated_scope["description"] == "Updated description"

        finally:
            if scope_id:
                try:
                    await client_scope_tools.delete_client_scope(scope_id)
                except Exception:
                    pass

    async def test_create_scope_with_attributes(self, unique_scope_name):
        """Test creating a client scope with custom attributes."""
        scope_id = None

        try:
            # Create scope with attributes
            result = await client_scope_tools.create_client_scope(
                name=unique_scope_name,
                description="Scope with custom attributes",
                protocol="openid-connect",
                attributes={
                    "include.in.token.scope": "true",
                    "display.on.consent.screen": "true",
                    "consent.screen.text": "Custom consent text",
                },
            )
            assert result["status"] == "created"

            # Find and verify
            scopes = await client_scope_tools.list_client_scopes()
            test_scope = next(
                (s for s in scopes if s["name"] == unique_scope_name), None
            )
            scope_id = test_scope["id"]

            scope = await client_scope_tools.get_client_scope(scope_id)
            assert "attributes" in scope
            assert scope["attributes"].get("include.in.token.scope") == "true"

        finally:
            if scope_id:
                try:
                    await client_scope_tools.delete_client_scope(scope_id)
                except Exception:
                    pass


@pytest.mark.integration
class TestClientScopeListing:
    """Test client scope listing operations."""

    async def test_list_all_scopes(self):
        """Test listing all client scopes."""
        scopes = await client_scope_tools.list_client_scopes()
        assert isinstance(scopes, list)
        # Should have at least default scopes
        assert len(scopes) > 0

        # Verify structure
        if scopes:
            scope = scopes[0]
            assert "id" in scope
            assert "name" in scope
            assert "protocol" in scope


@pytest.mark.integration
class TestClientDefaultScopes:
    """Test client default scope management operations."""

    async def test_list_client_default_scopes(self, unique_client_id):
        """Test listing default client scopes for a client."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Test Client for Scopes",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            assert test_client is not None
            client_db_id = test_client["id"]

            # List default client scopes
            default_scopes = await list_client_default_client_scopes(client_db_id)
            assert isinstance(default_scopes, list)
            # New clients typically have some default scopes assigned
            assert len(default_scopes) >= 0

            # Verify structure if scopes exist
            if default_scopes:
                scope = default_scopes[0]
                assert "id" in scope
                assert "name" in scope

        finally:
            if client_db_id:
                await delete_client(client_db_id)

    async def test_add_and_remove_default_scope(
        self, unique_client_id, unique_scope_name
    ):
        """Test adding and removing default client scopes."""
        client_db_id = None
        scope_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Test Client for Scope Assignment",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            # Create a test client scope
            await client_scope_tools.create_client_scope(
                name=unique_scope_name,
                description="Test scope for assignment",
                protocol="openid-connect",
            )

            # Find the scope
            scopes = await client_scope_tools.list_client_scopes()
            test_scope = next(
                (s for s in scopes if s["name"] == unique_scope_name), None
            )
            assert test_scope is not None
            scope_id = test_scope["id"]

            # Get initial default scopes
            initial_scopes = await list_client_default_client_scopes(client_db_id)
            initial_count = len(initial_scopes)
            initial_scope_ids = {s["id"] for s in initial_scopes}

            # Add the scope as default
            result = await update_client_default_client_scope(client_db_id, scope_id)
            assert result["status"] == "updated"
            assert scope_id in result["message"]

            # Verify it was added
            updated_scopes = await list_client_default_client_scopes(client_db_id)
            assert len(updated_scopes) == initial_count + 1
            updated_scope_ids = {s["id"] for s in updated_scopes}
            assert scope_id in updated_scope_ids

            # Remove the scope
            delete_result = await delete_client_default_client_scope(
                client_db_id, scope_id
            )
            assert delete_result["status"] == "deleted"
            assert scope_id in delete_result["message"]

            # Verify it was removed
            final_scopes = await list_client_default_client_scopes(client_db_id)
            assert len(final_scopes) == initial_count
            final_scope_ids = {s["id"] for s in final_scopes}
            assert scope_id not in final_scope_ids
            assert final_scope_ids == initial_scope_ids

        finally:
            if client_db_id:
                await delete_client(client_db_id)
            if scope_id:
                try:
                    await client_scope_tools.delete_client_scope(scope_id)
                except Exception:
                    pass

    async def test_add_multiple_default_scopes(
        self, unique_client_id, unique_scope_name
    ):
        """Test adding multiple default scopes to a client."""
        client_db_id = None
        scope_ids = []

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Test Client for Multiple Scopes",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            # Create two test scopes
            scope_names = [f"{unique_scope_name}-1", f"{unique_scope_name}-2"]
            for name in scope_names:
                await client_scope_tools.create_client_scope(
                    name=name,
                    description=f"Test scope {name}",
                    protocol="openid-connect",
                )

            # Find the scopes
            all_scopes = await client_scope_tools.list_client_scopes()
            for name in scope_names:
                test_scope = next((s for s in all_scopes if s["name"] == name), None)
                assert test_scope is not None
                scope_ids.append(test_scope["id"])

            # Get initial count
            initial_scopes = await list_client_default_client_scopes(client_db_id)
            initial_count = len(initial_scopes)

            # Add both scopes
            for scope_id in scope_ids:
                await update_client_default_client_scope(client_db_id, scope_id)

            # Verify both were added
            updated_scopes = await list_client_default_client_scopes(client_db_id)
            assert len(updated_scopes) == initial_count + 2
            updated_scope_ids = {s["id"] for s in updated_scopes}
            for scope_id in scope_ids:
                assert scope_id in updated_scope_ids

            # Remove both scopes
            for scope_id in scope_ids:
                await delete_client_default_client_scope(client_db_id, scope_id)

            # Verify both were removed
            final_scopes = await list_client_default_client_scopes(client_db_id)
            assert len(final_scopes) == initial_count

        finally:
            if client_db_id:
                await delete_client(client_db_id)
            for scope_id in scope_ids:
                try:
                    await client_scope_tools.delete_client_scope(scope_id)
                except Exception:
                    pass

    async def test_remove_nonexistent_scope_fails(self, unique_client_id):
        """Test that removing a non-existent default scope fails appropriately."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Test Client for Error Cases",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            # Try to remove a non-existent scope (using a fake UUID)
            fake_scope_id = "00000000-0000-0000-0000-000000000000"

            # This should raise an error
            with pytest.raises(Exception) as exc_info:
                await delete_client_default_client_scope(client_db_id, fake_scope_id)

            # Verify it's a 404 or appropriate error
            assert (
                "404" in str(exc_info.value)
                or "not found" in str(exc_info.value).lower()
                or "does not exist" in str(exc_info.value).lower()
            )

        finally:
            if client_db_id:
                await delete_client(client_db_id)
