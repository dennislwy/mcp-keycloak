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
