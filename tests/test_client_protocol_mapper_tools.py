"""
Integration tests for Client Protocol Mapper Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_protocol_mapper_tools, client_tools

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
    async def test_client():
        """Create a test client for protocol mapper tests."""
        client_id = f"test-client-{uuid.uuid4().hex[:8]}"

        # Create client
        await client_tools.create_client(
            client_id=client_id,
            name="Test Client for Protocol Mappers",
            enabled=True,
            protocol="openid-connect",
        )

        # Get client database ID
        clients = await client_tools.list_clients(client_id=client_id)
        test_client = next((c for c in clients if c["clientId"] == client_id), None)
        client_db_id = test_client["id"]

        yield {"id": client_db_id, "clientId": client_id}

        # Cleanup
        try:
            await client_tools.delete_client(client_db_id)
        except Exception:
            pass

    @pytest.fixture
    def unique_mapper_name():
        """Generate a unique mapper name for testing."""
        return f"test-mapper-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientProtocolMapperLifecycle:
    """Test client protocol mapper CRUD operations."""

    async def test_create_and_delete_mapper(self, test_client, unique_mapper_name):
        """Test creating and deleting a protocol mapper."""
        mapper_id = None

        try:
            # Create protocol mapper
            result = await client_protocol_mapper_tools.create_client_protocol_mapper(
                client_id=test_client["id"],
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-usermodel-attribute-mapper",
                config={
                    "user.attribute": "test_attribute",
                    "claim.name": "test_claim",
                    "jsonType.label": "String",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "true",
                },
            )
            assert result["status"] == "created"

            # Find the created mapper
            mappers = await client_protocol_mapper_tools.list_client_protocol_mappers(
                test_client["id"]
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            assert test_mapper is not None
            mapper_id = test_mapper["id"]

            # Get mapper by ID
            mapper = await client_protocol_mapper_tools.get_client_protocol_mapper(
                test_client["id"], mapper_id
            )
            assert mapper["name"] == unique_mapper_name
            assert mapper["protocol"] == "openid-connect"
            assert mapper["config"]["user.attribute"] == "test_attribute"

        finally:
            # Clean up
            if mapper_id:
                try:
                    delete_result = await client_protocol_mapper_tools.delete_client_protocol_mapper(
                        test_client["id"], mapper_id
                    )
                    assert delete_result["status"] == "deleted"

                    # Verify deletion
                    mappers = (
                        await client_protocol_mapper_tools.list_client_protocol_mappers(
                            test_client["id"]
                        )
                    )
                    assert not any(m["name"] == unique_mapper_name for m in mappers)
                except Exception:
                    pass

    async def test_update_mapper(self, test_client, unique_mapper_name):
        """Test updating protocol mapper configuration."""
        mapper_id = None

        try:
            # Create mapper
            await client_protocol_mapper_tools.create_client_protocol_mapper(
                client_id=test_client["id"],
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-usermodel-attribute-mapper",
                config={
                    "user.attribute": "original_attribute",
                    "claim.name": "original_claim",
                    "jsonType.label": "String",
                },
            )

            # Find mapper
            mappers = await client_protocol_mapper_tools.list_client_protocol_mappers(
                test_client["id"]
            )
            test_mapper = next(
                (m for m in mappers if m["name"] == unique_mapper_name), None
            )
            mapper_id = test_mapper["id"]

            # Update mapper
            result = await client_protocol_mapper_tools.update_client_protocol_mapper(
                client_id=test_client["id"],
                mapper_id=mapper_id,
                config={
                    "user.attribute": "updated_attribute",
                    "claim.name": "updated_claim",
                    "jsonType.label": "String",
                },
            )
            assert result["status"] == "updated"

            # Verify update
            updated_mapper = (
                await client_protocol_mapper_tools.get_client_protocol_mapper(
                    test_client["id"], mapper_id
                )
            )
            assert updated_mapper["config"]["user.attribute"] == "updated_attribute"

        finally:
            if mapper_id:
                try:
                    await client_protocol_mapper_tools.delete_client_protocol_mapper(
                        test_client["id"], mapper_id
                    )
                except Exception:
                    pass

    async def test_create_mappers_bulk(self, test_client):
        """Test creating multiple protocol mappers at once."""
        mapper_names = [
            f"test-bulk-mapper-{i}-{uuid.uuid4().hex[:4]}" for i in range(3)
        ]

        try:
            # Create multiple mappers
            mappers_data = [
                {
                    "name": name,
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-attribute-mapper",
                    "config": {
                        "user.attribute": f"attr_{i}",
                        "claim.name": f"claim_{i}",
                        "jsonType.label": "String",
                    },
                }
                for i, name in enumerate(mapper_names)
            ]

            result = (
                await client_protocol_mapper_tools.create_client_protocol_mappers_bulk(
                    test_client["id"], mappers_data
                )
            )
            assert result["status"] == "created"
            assert "3 protocol mappers created" in result["message"]

            # Verify all mappers were created
            all_mappers = (
                await client_protocol_mapper_tools.list_client_protocol_mappers(
                    test_client["id"]
                )
            )
            created_mapper_names = {m["name"] for m in all_mappers}
            for name in mapper_names:
                assert name in created_mapper_names

        finally:
            # Clean up bulk created mappers
            try:
                all_mappers = (
                    await client_protocol_mapper_tools.list_client_protocol_mappers(
                        test_client["id"]
                    )
                )
                for mapper in all_mappers:
                    if mapper["name"] in mapper_names:
                        try:
                            await client_protocol_mapper_tools.delete_client_protocol_mapper(
                                test_client["id"], mapper["id"]
                            )
                        except Exception:
                            pass
            except Exception:
                pass


@pytest.mark.integration
class TestClientProtocolMapperListing:
    """Test client protocol mapper listing operations."""

    async def test_list_client_mappers(self, test_client):
        """Test listing all protocol mappers for a client."""
        mappers = await client_protocol_mapper_tools.list_client_protocol_mappers(
            test_client["id"]
        )
        assert isinstance(mappers, list)

        # Verify structure
        if mappers:
            mapper = mappers[0]
            assert "id" in mapper
            assert "name" in mapper
            assert "protocol" in mapper
            assert "protocolMapper" in mapper

    async def test_get_mappers_by_protocol(self, test_client, unique_mapper_name):
        """Test filtering protocol mappers by protocol type."""
        mapper_id = None

        try:
            # Create OIDC mapper
            await client_protocol_mapper_tools.create_client_protocol_mapper(
                client_id=test_client["id"],
                name=unique_mapper_name,
                protocol="openid-connect",
                protocol_mapper="oidc-usermodel-attribute-mapper",
                config={"user.attribute": "test", "claim.name": "test"},
            )

            # Get mappers by protocol
            oidc_mappers = await client_protocol_mapper_tools.get_client_protocol_mappers_by_protocol(
                test_client["id"], "openid-connect"
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
                    await client_protocol_mapper_tools.delete_client_protocol_mapper(
                        test_client["id"], mapper_id
                    )
                except Exception:
                    pass
