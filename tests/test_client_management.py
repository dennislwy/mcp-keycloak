"""
Integration tests for Client Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_tools

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
    def unique_client_id():
        """Generate a unique client ID for testing."""
        return f"test-client-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientLifecycle:
    """Test client CRUD operations."""

    async def test_create_and_delete_public_client(self, unique_client_id):
        """Test creating and deleting a public client."""
        result = await client_tools.create_client(
            client_id=unique_client_id,
            name="Test Public Client",
            public_client=True,
            redirect_uris=["http://localhost:8080/*"],
        )
        assert result["status"] == "created"

        # Find client
        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        assert test_client is not None
        db_id = test_client["id"]

        try:
            # Get client by internal ID
            client = await client_tools.get_client(db_id)
            assert client["clientId"] == unique_client_id
            assert client["name"] == "Test Public Client"
            assert client["publicClient"] is True
        finally:
            # Delete client
            delete_result = await client_tools.delete_client(db_id)
            assert delete_result["status"] == "deleted"

            # Verify deletion
            clients = await client_tools.list_clients(client_id=unique_client_id)
            assert not any(c["clientId"] == unique_client_id for c in clients)

    async def test_create_confidential_client(self, unique_client_id):
        """Test creating a confidential client."""
        result = await client_tools.create_client(
            client_id=unique_client_id,
            name="Test Confidential Client",
            public_client=False,
            redirect_uris=["http://localhost:8080/*"],
            web_origins=["http://localhost:8080"],
        )
        assert result["status"] == "created"

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            client = await client_tools.get_client(db_id)
            assert client["publicClient"] is False
        finally:
            await client_tools.delete_client(db_id)

    async def test_update_client(self, unique_client_id):
        """Test updating client attributes."""
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Original Name",
            public_client=True,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            # Update client
            result = await client_tools.update_client(
                id=db_id,
                name="Updated Name",
                description="Updated description",
                redirect_uris=["http://localhost:9090/*"],
            )
            assert result["status"] == "updated"

            # Verify update
            client = await client_tools.get_client(db_id)
            assert client["name"] == "Updated Name"
            assert client.get("description") == "Updated description"
        finally:
            await client_tools.delete_client(db_id)


@pytest.mark.integration
class TestClientListing:
    """Test client listing and search."""

    async def test_list_clients(self):
        """Test listing clients."""
        clients = await client_tools.list_clients()
        assert isinstance(clients, list)
        assert len(clients) > 0  # Should have at least default clients

    async def test_list_clients_with_filter(self, unique_client_id):
        """Test listing clients with client_id filter."""
        # Create client
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Filtered Client",
            public_client=True,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            assert test_client is not None
            assert test_client["clientId"] == unique_client_id
        finally:
            await client_tools.delete_client(db_id)

    async def test_get_client_by_clientid(self, unique_client_id):
        """Test getting a client by its clientId."""
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Get By ClientId",
            public_client=True,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            client = await client_tools.get_client_by_clientid(unique_client_id)
            assert client["clientId"] == unique_client_id
        finally:
            await client_tools.delete_client(db_id)


@pytest.mark.integration
class TestClientSecrets:
    """Test client secret operations."""

    async def test_get_client_secret(self, unique_client_id):
        """Test getting a confidential client's secret."""
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Secret Client",
            public_client=False,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            secret = await client_tools.get_client_secret(db_id)
            assert isinstance(secret, dict)
            assert "value" in secret
        finally:
            await client_tools.delete_client(db_id)

    async def test_regenerate_client_secret(self, unique_client_id):
        """Test regenerating a confidential client's secret."""
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Regenerate Secret Client",
            public_client=False,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            # Get original secret
            original_secret = await client_tools.get_client_secret(db_id)

            # Regenerate
            new_secret = await client_tools.regenerate_client_secret(db_id)
            assert isinstance(new_secret, dict)
            assert "value" in new_secret

            # Secrets should differ
            assert new_secret["value"] != original_secret["value"]
        finally:
            await client_tools.delete_client(db_id)


@pytest.mark.integration
class TestClientServiceAccount:
    """Test client service account operations."""

    async def test_get_service_account_user(self, unique_client_id):
        """Test getting the service account user for a client."""
        await client_tools.create_client(
            client_id=unique_client_id,
            name="Service Account Client",
            public_client=False,
            service_accounts_enabled=True,
        )

        clients = await client_tools.list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        db_id = test_client["id"]

        try:
            sa_user = await client_tools.get_client_service_account(db_id)
            assert isinstance(sa_user, dict)
            assert "username" in sa_user
            assert sa_user["username"] == f"service-account-{unique_client_id}"
        finally:
            await client_tools.delete_client(db_id)


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Client Management Integration Tests ===\n")

    test_lifecycle = TestClientLifecycle()
    test_listing = TestClientListing()
    test_secrets = TestClientSecrets()
    test_sa = TestClientServiceAccount()

    tests = [
        (
            "Create and delete public client",
            test_lifecycle.test_create_and_delete_public_client,
        ),
        ("Create confidential client", test_lifecycle.test_create_confidential_client),
        ("Update client", test_lifecycle.test_update_client),
        ("List clients", test_listing.test_list_clients),
        ("List clients with filter", test_listing.test_list_clients_with_filter),
        ("Get client by clientId", test_listing.test_get_client_by_clientid),
        ("Get client secret", test_secrets.test_get_client_secret),
        ("Regenerate client secret", test_secrets.test_regenerate_client_secret),
        ("Get service account user", test_sa.test_get_service_account_user),
    ]

    for name, test_func in tests:
        print(f"Testing {name}...")
        try:
            import inspect

            sig = inspect.signature(test_func)
            if "unique_client_id" in sig.parameters:
                await test_func(f"test-client-{uuid.uuid4().hex[:8]}")
            else:
                await test_func()
            print(f"[PASS] {name} test passed")
        except Exception as e:
            print(f"[FAIL] {name} test failed: {e}")

    print("\n=== Client Management Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
