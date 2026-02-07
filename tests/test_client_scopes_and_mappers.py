"""
Integration tests for Client Scopes and Protocol Mappers.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_scope_tools, protocol_mapper_tools, client_tools

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

    @pytest.fixture
    def unique_mapper_name():
        """Generate a unique mapper name for testing."""
        return f"test-mapper-{uuid.uuid4().hex[:8]}"


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
class TestProtocolMappers:
    """Test protocol mapper management."""

    async def test_client_scope_mapper_lifecycle(
        self, unique_scope_name, unique_mapper_name
    ):
        """Test creating, reading, updating, and deleting protocol mappers for client scopes."""
        # Create client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name, protocol="openid-connect"
        )
        assert result["status"] == "created"

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Create protocol mapper
            result = await protocol_mapper_tools.create_client_scope_protocol_mapper(
                scope_id=scope_id,
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-usermodel-attribute-mapper",
                config={
                    "user.attribute": "email",
                    "claim.name": "email_address",
                    "jsonType.label": "String",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "true",
                },
            )
            assert result["status"] == "created"

            # List mappers
            mappers = await protocol_mapper_tools.list_client_scope_protocol_mappers(
                scope_id
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            assert test_mapper is not None
            mapper_id = test_mapper["id"]

            # Get specific mapper
            mapper = await protocol_mapper_tools.get_client_scope_protocol_mapper(
                scope_id, mapper_id
            )
            assert mapper["name"] == unique_mapper_name
            assert mapper["config"]["claim.name"] == "email_address"

            # Update mapper
            result = await protocol_mapper_tools.update_client_scope_protocol_mapper(
                scope_id=scope_id,
                mapper_id=mapper_id,
                config={
                    "user.attribute": "email",
                    "claim.name": "user_email",
                    "jsonType.label": "String",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "false",
                },
            )
            assert result["status"] == "updated"

            # Verify update
            mapper = await protocol_mapper_tools.get_client_scope_protocol_mapper(
                scope_id, mapper_id
            )
            assert mapper["config"]["claim.name"] == "user_email"
            assert mapper["config"]["userinfo.token.claim"] == "false"

            # Delete mapper
            result = await protocol_mapper_tools.delete_client_scope_protocol_mapper(
                scope_id, mapper_id
            )
            assert result["status"] == "deleted"

            # Verify deletion
            mappers = await protocol_mapper_tools.list_client_scope_protocol_mappers(
                scope_id
            )
            assert not any(m["name"] == unique_mapper_name for m in mappers)

        finally:
            # Clean up
            await client_scope_tools.delete_client_scope(scope_id)

    async def test_multiple_mappers(self, unique_scope_name):
        """Test adding multiple mappers at once."""
        # Create client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name, protocol="openid-connect"
        )

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Create multiple mappers
            mappers = [
                {
                    "name": f"mapper1-{uuid.uuid4().hex[:8]}",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-attribute-mapper",
                    "config": {
                        "user.attribute": "firstName",
                        "claim.name": "given_name",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                    },
                },
                {
                    "name": f"mapper2-{uuid.uuid4().hex[:8]}",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-attribute-mapper",
                    "config": {
                        "user.attribute": "lastName",
                        "claim.name": "family_name",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                    },
                },
            ]

            result = await protocol_mapper_tools.add_client_scope_protocol_mappers(
                scope_id=scope_id, mappers=mappers
            )
            assert result["status"] == "created"
            assert "2 protocol mappers" in result["message"]

            # Verify mappers were created
            created_mappers = (
                await protocol_mapper_tools.list_client_scope_protocol_mappers(scope_id)
            )
            assert any(m["name"] == mappers[0]["name"] for m in created_mappers)
            assert any(m["name"] == mappers[1]["name"] for m in created_mappers)

        finally:
            # Clean up
            await client_scope_tools.delete_client_scope(scope_id)

    async def test_convenience_mapper_functions(self, unique_scope_name):
        """Test convenience functions for creating common mapper types."""
        # Create client scope
        result = await client_scope_tools.create_client_scope(
            name=unique_scope_name, protocol="openid-connect"
        )

        # Find the scope
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == unique_scope_name), None)
        scope_id = test_scope["id"]

        try:
            # Create user attribute mapper
            result = await protocol_mapper_tools.create_user_attribute_mapper(
                target_id=scope_id,
                target_type="client-scope",
                attribute_name="department",
                claim_name="dept",
                claim_type="String",
            )
            assert result["status"] == "created"

            # Create role mapper
            result = await protocol_mapper_tools.create_role_mapper(
                target_id=scope_id, target_type="client-scope", claim_name="user_roles"
            )
            assert result["status"] == "created"

            # Verify mappers were created
            mappers = await protocol_mapper_tools.list_client_scope_protocol_mappers(
                scope_id
            )
            assert any("department-mapper" in m["name"] for m in mappers)
            assert any("user_roles-realm-role-mapper" in m["name"] for m in mappers)

        finally:
            # Clean up
            await client_scope_tools.delete_client_scope(scope_id)


@pytest.mark.integration
class TestClientScopeIntegration:
    """Test client scope integration with clients."""

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

    async def test_client_protocol_mappers(self, unique_client_id, unique_mapper_name):
        """Test creating protocol mappers directly on clients."""
        # Create client
        await client_tools.create_client(
            client_id=unique_client_id, name="Test Client", public_client=True
        )

        # Get client
        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Create protocol mapper on client
            result = await protocol_mapper_tools.create_client_protocol_mapper(
                client_id=client_db_id,
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-audience-mapper",
                config={
                    "included.client.audience": unique_client_id,
                    "id.token.claim": "false",
                    "access.token.claim": "true",
                },
            )
            assert result["status"] == "created"

            # List client mappers
            mappers = await protocol_mapper_tools.list_client_protocol_mappers(
                client_db_id
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            assert test_mapper is not None

            # Test audience mapper convenience function
            result = await protocol_mapper_tools.create_audience_mapper(
                target_id=client_db_id,
                target_type="client",
                included_client_audience="another-client",
            )
            assert result["status"] == "created"

            # Evaluate all effective mappers
            effective = await protocol_mapper_tools.evaluate_client_scope_mappers(
                client_db_id
            )
            assert (
                len(effective) > 0
            )  # Should have default mappers plus our custom ones

        finally:
            # Clean up
            await client_tools.delete_client(client_db_id)


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Client Scopes and Protocol Mappers Integration Tests ===\n")

    # Test client scopes
    test_scopes = TestClientScopes()
    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"

    print("Testing client scope lifecycle...")
    await test_scopes.test_client_scope_lifecycle(scope_name)
    print("[PASS] Client scope lifecycle test passed")

    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
    print("\nTesting realm default scopes...")
    await test_scopes.test_realm_default_scopes(scope_name)
    print("[PASS] Realm default scopes test passed")

    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
    print("\nTesting realm optional scopes...")
    await test_scopes.test_realm_optional_scopes(scope_name)
    print("[PASS] Realm optional scopes test passed")

    # Test protocol mappers
    test_mappers = TestProtocolMappers()
    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
    mapper_name = f"test-mapper-{uuid.uuid4().hex[:8]}"

    print("\nTesting protocol mapper lifecycle...")
    await test_mappers.test_client_scope_mapper_lifecycle(scope_name, mapper_name)
    print("[PASS] Protocol mapper lifecycle test passed")

    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
    print("\nTesting multiple mappers...")
    await test_mappers.test_multiple_mappers(scope_name)
    print("[PASS] Multiple mappers test passed")

    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"
    print("\nTesting convenience mapper functions...")
    await test_mappers.test_convenience_mapper_functions(scope_name)
    print("[PASS] Convenience mapper functions test passed")

    # Test integration
    test_integration = TestClientScopeIntegration()
    client_id = f"test-client-{uuid.uuid4().hex[:8]}"
    scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"

    print("\nTesting client scope assignment...")
    await test_integration.test_client_scope_assignment(client_id, scope_name)
    print("[PASS] Client scope assignment test passed")

    client_id = f"test-client-{uuid.uuid4().hex[:8]}"
    mapper_name = f"test-mapper-{uuid.uuid4().hex[:8]}"
    print("\nTesting client protocol mappers...")
    await test_integration.test_client_protocol_mappers(client_id, mapper_name)
    print("[PASS] Client protocol mappers test passed")

    print("\n=== All tests passed successfully! ===\n")


if __name__ == "__main__":
    run_tests()
