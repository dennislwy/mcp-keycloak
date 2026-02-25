"""
Integration tests for Client Scope Protocol Mapper Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_scope_protocol_mapper_tools, client_scope_tools

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
    async def test_client_scope():
        """Create a test client scope for protocol mapper tests."""
        scope_name = f"test-scope-{uuid.uuid4().hex[:8]}"

        # Create client scope
        await client_scope_tools.create_client_scope(
            name=scope_name,
            description="Test scope for protocol mappers",
            protocol="openid-connect",
        )

        # Get scope ID
        scopes = await client_scope_tools.list_client_scopes()
        test_scope = next((s for s in scopes if s["name"] == scope_name), None)
        scope_id = test_scope["id"]

        yield {"id": scope_id, "name": scope_name}

        # Cleanup
        try:
            await client_scope_tools.delete_client_scope(scope_id)
        except Exception:
            pass

    @pytest.fixture
    def unique_mapper_name():
        """Generate a unique mapper name for testing."""
        return f"test-scope-mapper-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientScopeProtocolMapperLifecycle:
    """Test client scope protocol mapper CRUD operations."""

    async def test_create_and_delete_mapper(
        self, test_client_scope, unique_mapper_name
    ):
        """Test creating and deleting a protocol mapper on a client scope."""
        mapper_id = None

        try:
            # Create protocol mapper
            result = await client_scope_protocol_mapper_tools.create_client_scope_protocol_mapper(
                client_scope_id=test_client_scope["id"],
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-usermodel-attribute-mapper",
                config={
                    "user.attribute": "test_scope_attribute",
                    "claim.name": "test_scope_claim",
                    "jsonType.label": "String",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "true",
                },
            )
            assert result["status"] == "created"

            # Find the created mapper
            mappers = await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                test_client_scope["id"]
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            assert test_mapper is not None
            mapper_id = test_mapper["id"]

            # Get mapper by ID
            mapper = await client_scope_protocol_mapper_tools.get_client_scope_protocol_mapper(
                test_client_scope["id"], mapper_id
            )
            assert mapper["name"] == unique_mapper_name
            assert mapper["protocol"] == "openid-connect"
            assert mapper["config"]["user.attribute"] == "test_scope_attribute"

        finally:
            # Clean up
            if mapper_id:
                try:
                    delete_result = await client_scope_protocol_mapper_tools.delete_client_scope_protocol_mapper(
                        test_client_scope["id"], mapper_id
                    )
                    assert delete_result["status"] == "deleted"

                    # Verify deletion
                    mappers = await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                        test_client_scope["id"]
                    )
                    assert not any(m["name"] == unique_mapper_name for m in mappers)
                except Exception:
                    pass

    async def test_update_mapper(self, test_client_scope, unique_mapper_name):
        """Test updating protocol mapper configuration."""
        mapper_id = None

        try:
            # Create mapper
            await (
                client_scope_protocol_mapper_tools.create_client_scope_protocol_mapper(
                    client_scope_id=test_client_scope["id"],
                    name=unique_mapper_name,
                    protocol="openid-connect",
                    protocol_mapper="oidc-usermodel-attribute-mapper",
                    config={
                        "user.attribute": "original_scope_attribute",
                        "claim.name": "original_scope_claim",
                        "jsonType.label": "String",
                    },
                )
            )

            # Find mapper
            mappers = await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                test_client_scope["id"]
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            mapper_id = test_mapper["id"]

            # Update mapper
            result = await client_scope_protocol_mapper_tools.update_client_scope_protocol_mapper(
                client_scope_id=test_client_scope["id"],
                mapper_id=mapper_id,
                config={
                    "user.attribute": "updated_scope_attribute",
                    "claim.name": "updated_scope_claim",
                    "jsonType.label": "String",
                },
            )
            assert result["status"] == "updated"

            # Verify update
            updated_mapper = await client_scope_protocol_mapper_tools.get_client_scope_protocol_mapper(
                test_client_scope["id"], mapper_id
            )
            assert (
                updated_mapper["config"]["user.attribute"] == "updated_scope_attribute"
            )

        finally:
            if mapper_id:
                try:
                    await client_scope_protocol_mapper_tools.delete_client_scope_protocol_mapper(
                        test_client_scope["id"], mapper_id
                    )
                except Exception:
                    pass

    async def test_create_mappers_bulk(self, test_client_scope):
        """Test creating multiple protocol mappers at once."""
        mapper_names = [
            f"test-scope-bulk-mapper-{i}-{uuid.uuid4().hex[:4]}" for i in range(3)
        ]

        try:
            # Create multiple mappers
            mappers_data = [
                {
                    "name": name,
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-attribute-mapper",
                    "config": {
                        "user.attribute": f"scope_attr_{i}",
                        "claim.name": f"scope_claim_{i}",
                        "jsonType.label": "String",
                    },
                }
                for i, name in enumerate(mapper_names)
            ]

            result = await client_scope_protocol_mapper_tools.create_client_scope_protocol_mappers_bulk(
                test_client_scope["id"], mappers_data
            )
            assert result["status"] == "created"
            assert "3 protocol mappers created" in result["message"]

            # Verify all mappers were created
            all_mappers = await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                test_client_scope["id"]
            )
            created_mapper_names = {m["name"] for m in all_mappers}
            for name in mapper_names:
                assert name in created_mapper_names

        finally:
            # Clean up bulk created mappers
            try:
                all_mappers = await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                    test_client_scope["id"]
                )
                for mapper in all_mappers:
                    if mapper["name"] in mapper_names:
                        try:
                            await client_scope_protocol_mapper_tools.delete_client_scope_protocol_mapper(
                                test_client_scope["id"], mapper["id"]
                            )
                        except Exception:
                            pass
            except Exception:
                pass


@pytest.mark.integration
class TestClientScopeProtocolMapperListing:
    """Test client scope protocol mapper listing operations."""

    async def test_list_scope_mappers(self, test_client_scope):
        """Test listing all protocol mappers for a client scope."""
        mappers = (
            await client_scope_protocol_mapper_tools.list_client_scope_protocol_mappers(
                test_client_scope["id"]
            )
        )
        assert isinstance(mappers, list)

        # Verify structure
        if mappers:
            mapper = mappers[0]
            assert "id" in mapper
            assert "name" in mapper
            assert "protocol" in mapper
            assert "protocolMapper" in mapper

    async def test_get_scope_mappers_by_protocol(
        self, test_client_scope, unique_mapper_name
    ):
        """Test filtering protocol mappers by protocol type."""
        mapper_id = None

        try:
            # Create OIDC mapper
            await (
                client_scope_protocol_mapper_tools.create_client_scope_protocol_mapper(
                    client_scope_id=test_client_scope["id"],
                    name=unique_mapper_name,
                    protocol="openid-connect",
                    protocol_mapper="oidc-usermodel-attribute-mapper",
                    config={"user.attribute": "test", "claim.name": "test"},
                )
            )

            # Get mappers by protocol
            oidc_mappers = await client_scope_protocol_mapper_tools.get_client_scope_protocol_mappers_by_protocol(
                test_client_scope["id"], "openid-connect"
            )
            assert isinstance(oidc_mappers, list)

            # Verify our mapper is in the list
            test_mapper = next(
                (m for m in oidc_mappers if m["name"] == unique_mapper_name), None
            )
            assert test_mapper is not None
            mapper_id = test_mapper["id"]

        finally:
            if mapper_id:
                try:
                    await client_scope_protocol_mapper_tools.delete_client_scope_protocol_mapper(
                        test_client_scope["id"], mapper_id
                    )
                except Exception:
                    pass
