"""
Integration tests for client management tools.

These tests cover all client-related functionality including CRUD operations,
advanced search, client configuration, and OAuth2/OIDC settings.
"""

import pytest
import uuid
from src.tools.client_tools import (
    list_clients,
    create_client,
    update_client,
    delete_client,
    get_client,
    get_client_by_clientid,
    get_client_secret,
    regenerate_client_secret,
    get_client_secret_rotated,
    delete_client_secret_rotated,
    get_client_management_permissions,
    update_client_management_permissions,
)


@pytest.fixture
def unique_client_id():
    """Generate a unique client ID for testing."""
    return f"test-client-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestClientCRUD:
    """Test basic client CRUD operations."""

    async def test_create_and_delete_client(self, unique_client_id):
        """Test creating and deleting a client."""
        result = await create_client(
            client_id=unique_client_id,
            name="Test Client",
            description="Test client description",
            enabled=True,
        )
        assert result["status"] == "created"

        # Find client
        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        assert test_client is not None
        client_db_id = test_client["id"]

        try:
            # Get client by database ID
            client = await get_client(client_db_id)
            assert client["clientId"] == unique_client_id
            assert client["name"] == "Test Client"
            assert client["description"] == "Test client description"

            # Get client by client ID
            client_by_clientid = await get_client_by_clientid(unique_client_id)
            assert client_by_clientid["id"] == client_db_id
        finally:
            # Delete client
            delete_result = await delete_client(client_db_id)
            assert delete_result["status"] == "deleted"

            # Verify deletion
            clients = await list_clients(client_id=unique_client_id)
            assert not any(c["clientId"] == unique_client_id for c in clients)

    async def test_update_client(self, unique_client_id):
        """Test updating client attributes."""
        # Create client
        await create_client(
            client_id=unique_client_id,
            name="Original Name",
            description="Original description",
            enabled=True,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Update client
            result = await update_client(
                id=client_db_id,
                name="Updated Name",
                description="Updated description",
                enabled=False,
            )
            assert result["status"] == "updated"

            # Verify update
            client = await get_client(client_db_id)
            assert client["name"] == "Updated Name"
            assert client["description"] == "Updated description"
            assert client["enabled"] is False
        finally:
            await delete_client(client_db_id)


@pytest.mark.integration
class TestClientSearch:
    """Test client listing and search capabilities."""

    async def test_list_clients(self):
        """Test listing clients."""
        clients = await list_clients(max=10)
        assert isinstance(clients, list)

    async def test_list_clients_with_filter(self, unique_client_id):
        """Test listing clients with client_id filter."""
        # Create client
        await create_client(
            client_id=unique_client_id,
            name="Searchable Client",
            enabled=True,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Filter should find our client
            assert test_client is not None
            assert test_client["clientId"] == unique_client_id
        finally:
            await delete_client(client_db_id)

    async def test_search_mode(self):
        """Test search mode parameter."""
        # Search mode should work without errors
        clients = await list_clients(search=True, max=10)
        assert isinstance(clients, list)


@pytest.mark.integration
class TestClientEnhancements:
    """Test enhanced client creation and configuration features."""

    async def test_create_client_with_full_configuration(self, unique_client_id):
        """Test creating a client with all enhanced parameters."""
        result = await create_client(
            client_id=unique_client_id,
            name="Full Config Client",
            description="Client with full configuration",
            enabled=True,
            base_url="https://example.com",
            admin_url="https://example.com/admin",
            root_url="https://example.com",
            redirect_uris=["https://example.com/callback"],
            web_origins=["https://example.com"],
            protocol="openid-connect",
            public_client=False,
            full_scope_allowed=False,
            consent_required=True,
            client_authenticator_type="client-secret",
            frontchannel_logout=True,
            attributes={"custom.attr": "value", "another.attr": "test"},
            default_client_scopes=["openid", "profile"],
            optional_client_scopes=["email"],
        )
        assert result["status"] == "created"

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Verify all configurations
            client = await get_client(client_db_id)
            assert client["name"] == "Full Config Client"
            assert client["baseUrl"] == "https://example.com"
            assert client["adminUrl"] == "https://example.com/admin"
            assert client["rootUrl"] == "https://example.com"
            assert client["fullScopeAllowed"] is False
            assert client["consentRequired"] is True
            assert client["clientAuthenticatorType"] == "client-secret"
            assert client["frontchannelLogout"] is True
            assert client["attributes"]["custom.attr"] == "value"
            assert client["attributes"]["another.attr"] == "test"
        finally:
            await delete_client(client_db_id)

    async def test_create_client_with_oauth_settings(self, unique_client_id):
        """Test creating a client with various OAuth2 flow settings."""
        result = await create_client(
            client_id=unique_client_id,
            name="OAuth Client",
            enabled=True,
            public_client=False,
            standard_flow_enabled=True,
            implicit_flow_enabled=False,
            direct_access_grants_enabled=True,
            service_accounts_enabled=True,
            authorization_services_enabled=True,
            redirect_uris=["http://localhost:3000/*"],
        )
        assert result["status"] == "created"

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            client = await get_client(client_db_id)
            assert client["standardFlowEnabled"] is True
            assert client["implicitFlowEnabled"] is False
            assert client["directAccessGrantsEnabled"] is True
            assert client["serviceAccountsEnabled"] is True
            assert client["authorizationServicesEnabled"] is True
        finally:
            await delete_client(client_db_id)

    async def test_create_client_with_consent_required(self, unique_client_id):
        """Test creating a client with consent required."""
        result = await create_client(
            client_id=unique_client_id,
            name="Consent Client",
            enabled=True,
            consent_required=True,
            full_scope_allowed=False,
        )
        assert result["status"] == "created"

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            client = await get_client(client_db_id)
            assert client["consentRequired"] is True
            assert client["fullScopeAllowed"] is False
        finally:
            await delete_client(client_db_id)

    async def test_create_client_with_custom_attributes(self, unique_client_id):
        """Test creating a client with custom attributes."""
        result = await create_client(
            client_id=unique_client_id,
            name="Attributes Client",
            enabled=True,
            attributes={
                "app.environment": "production",
                "app.version": "1.0.0",
                "custom.setting": "enabled",
            },
        )
        assert result["status"] == "created"

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            client = await get_client(client_db_id)
            assert "attributes" in client
            assert client["attributes"]["app.environment"] == "production"
            assert client["attributes"]["app.version"] == "1.0.0"
            assert client["attributes"]["custom.setting"] == "enabled"
        finally:
            await delete_client(client_db_id)

    async def test_single_step_client_creation(self, unique_client_id):
        """Test single-step client creation with all settings (no update needed)."""
        # This test demonstrates the enhancement: create client with full config in one step
        result = await create_client(
            client_id=unique_client_id,
            name="Complete Client",
            description="Client created with all settings in one step",
            enabled=True,
            base_url="https://app.example.com",
            admin_url="https://app.example.com/admin",
            root_url="https://app.example.com",
            redirect_uris=["https://app.example.com/callback"],
            web_origins=["https://app.example.com"],
            full_scope_allowed=False,
            consent_required=True,
            client_authenticator_type="client-secret",
            frontchannel_logout=True,
            standard_flow_enabled=True,
            direct_access_grants_enabled=False,
            attributes={"myapp.setting": "value"},
        )
        assert result["status"] == "created"

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Verify everything was set in single creation
            client = await get_client(client_db_id)
            assert client["baseUrl"] == "https://app.example.com"
            assert client["adminUrl"] == "https://app.example.com/admin"
            assert client["fullScopeAllowed"] is False
            assert client["consentRequired"] is True
            assert client["attributes"]["myapp.setting"] == "value"
        finally:
            await delete_client(client_db_id)


@pytest.mark.integration
class TestClientSecrets:
    """Test client secret operations."""

    async def test_get_and_regenerate_client_secret(self, unique_client_id):
        """Test getting and regenerating client secret."""
        # Create confidential client (public_client=False)
        await create_client(
            client_id=unique_client_id,
            name="Secret Client",
            enabled=True,
            public_client=False,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Get client secret
            secret_response = await get_client_secret(client_db_id)
            assert "value" in secret_response
            original_secret = secret_response["value"]

            # Regenerate secret
            new_secret_response = await regenerate_client_secret(client_db_id)
            assert "value" in new_secret_response
            new_secret = new_secret_response["value"]

            # Verify secret changed
            assert new_secret != original_secret
        finally:
            await delete_client(client_db_id)


@pytest.mark.integration
class TestClientSecretRotation:
    """Test client secret rotation operations.

    Note: These tests verify the rotation API endpoints. Whether rotation actually
    preserves the old secret depends on realm-level client policies. If rotation
    policies are not configured, get_client_secret_rotated() will return 404.
    """

    async def test_client_secret_rotation_with_policy(self, unique_client_id):
        """Test client secret rotation when rotation policies are enabled.

        This test verifies the rotation lifecycle IF rotation is enabled.
        If rotation is not enabled, the test will be skipped.
        """
        # Create confidential client
        await create_client(
            client_id=unique_client_id,
            name="Rotation Test Client",
            enabled=True,
            public_client=False,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Get initial secret
            secret_response = await get_client_secret(client_db_id)
            assert "value" in secret_response
            original_secret = secret_response["value"]

            # Regenerate secret (this may create a rotation if policies are enabled)
            new_secret_response = await regenerate_client_secret(client_db_id)
            assert "value" in new_secret_response
            new_secret = new_secret_response["value"]
            assert new_secret != original_secret

            # Try to get rotated secret
            try:
                rotated_response = await get_client_secret_rotated(client_db_id)
                assert "value" in rotated_response
                rotated_secret = rotated_response["value"]

                # The rotated secret should be the original secret
                assert rotated_secret == original_secret

                # Current secret should still be the new one
                current_secret_response = await get_client_secret(client_db_id)
                assert current_secret_response["value"] == new_secret

                # Delete rotated secret
                delete_result = await delete_client_secret_rotated(client_db_id)
                assert delete_result["status"] == "deleted"
                assert "invalidated successfully" in delete_result["message"]

                # After deletion, rotated secret should not exist
                try:
                    await get_client_secret_rotated(client_db_id)
                    assert False, "Expected 404 after deleting rotated secret"
                except Exception as e:
                    assert "404" in str(e) or "not found" in str(e).lower()

            except Exception as e:
                # If we get 404, it means rotation is not enabled in this realm
                if "404" in str(e) or "not found" in str(e).lower():
                    pytest.skip(
                        "Client secret rotation not enabled (no rotation policies configured)"
                    )
                else:
                    raise

        finally:
            await delete_client(client_db_id)

    async def test_get_rotated_secret_when_none_exists(self, unique_client_id):
        """Test that getting rotated secret returns 404 when none exists."""
        # Create confidential client
        await create_client(
            client_id=unique_client_id,
            name="No Rotation Client",
            enabled=True,
            public_client=False,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Try to get rotated secret when none exists
            # Should raise 404 error
            with pytest.raises(Exception) as exc_info:
                await get_client_secret_rotated(client_db_id)

            # Verify it's a 404 error about no rotated secret
            assert (
                "404" in str(exc_info.value)
                or "rotated secret" in str(exc_info.value).lower()
            )

        finally:
            await delete_client(client_db_id)

    async def test_secret_regeneration_changes_value(self, unique_client_id):
        """Test that regenerating secret creates a new value."""
        # Create confidential client
        await create_client(
            client_id=unique_client_id,
            name="Regeneration Client",
            enabled=True,
            public_client=False,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Get initial secret
            secret1 = await get_client_secret(client_db_id)
            assert "value" in secret1
            value1 = secret1["value"]

            # First regeneration
            secret2 = await regenerate_client_secret(client_db_id)
            assert "value" in secret2
            value2 = secret2["value"]
            assert value2 != value1

            # Second regeneration
            secret3 = await regenerate_client_secret(client_db_id)
            assert "value" in secret3
            value3 = secret3["value"]
            assert value3 != value2
            assert value3 != value1

            # Verify current secret is the latest
            current = await get_client_secret(client_db_id)
            assert current["value"] == value3

        finally:
            await delete_client(client_db_id)

    async def test_delete_rotated_secret_api(self, unique_client_id):
        """Test that delete rotated secret API works correctly."""
        # Create confidential client
        await create_client(
            client_id=unique_client_id,
            name="Delete Rotation Client",
            enabled=True,
            public_client=False,
        )

        clients = await list_clients(client_id=unique_client_id)
        test_client = next(
            (c for c in clients if c["clientId"] == unique_client_id), None
        )
        client_db_id = test_client["id"]

        try:
            # Get initial secret
            await get_client_secret(client_db_id)

            # Regenerate to potentially create rotation
            new_secret = await regenerate_client_secret(client_db_id)
            current_secret_value = new_secret["value"]

            # Try to delete rotated secret
            try:
                # First check if rotated secret exists
                await get_client_secret_rotated(client_db_id)

                # If it exists, delete it
                delete_result = await delete_client_secret_rotated(client_db_id)
                assert delete_result["status"] == "deleted"

                # Verify current secret is still intact
                current_secret = await get_client_secret(client_db_id)
                assert current_secret["value"] == current_secret_value

                # Verify rotated secret is gone
                with pytest.raises(Exception) as exc_info:
                    await get_client_secret_rotated(client_db_id)
                assert "404" in str(exc_info.value)

            except Exception as e:
                # If no rotated secret exists, that's fine - rotation not enabled
                if "404" in str(e) or "not found" in str(e).lower():
                    pytest.skip("No rotated secret to delete (rotation not configured)")
                else:
                    raise

        finally:
            await delete_client(client_db_id)


@pytest.mark.integration
class TestClientManagementPermissions:
    """Test client management permissions operations.

    Note: These tests require the admin-fine-grained-authz feature to be enabled
    in Keycloak. If the feature is not available, tests will be skipped.
    """

    async def test_get_management_permissions_default_state(self, unique_client_id):
        """Test getting management permissions for a newly created client."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Permissions Test Client",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            assert test_client is not None
            client_db_id = test_client["id"]

            # Try to get management permissions
            try:
                permissions = await get_client_management_permissions(client_db_id)
                assert isinstance(permissions, dict)
                assert "enabled" in permissions
                # New clients typically have permissions disabled
                assert permissions["enabled"] is False
            except Exception as e:
                # Feature not enabled - skip test
                if "501" in str(e) or "feature not enabled" in str(e).lower():
                    pytest.skip(
                        "Management permissions feature not enabled (requires admin-fine-grained-authz)"
                    )
                else:
                    raise

        finally:
            if client_db_id:
                await delete_client(client_db_id)

    async def test_enable_and_disable_management_permissions(self, unique_client_id):
        """Test enabling and disabling management permissions."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Permissions Toggle Client",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            try:
                # Get initial state (should be disabled)
                initial_permissions = await get_client_management_permissions(
                    client_db_id
                )
                assert initial_permissions["enabled"] is False

                # Enable management permissions
                enabled_result = await update_client_management_permissions(
                    client_db_id, enabled=True
                )
                assert enabled_result["enabled"] is True
                # When enabled, should have resource information
                assert (
                    "resource" in enabled_result or "resourceServerId" in enabled_result
                )

                # Verify it's enabled
                check_enabled = await get_client_management_permissions(client_db_id)
                assert check_enabled["enabled"] is True

                # Disable management permissions
                disabled_result = await update_client_management_permissions(
                    client_db_id, enabled=False
                )
                assert disabled_result["enabled"] is False

                # Verify it's disabled
                check_disabled = await get_client_management_permissions(client_db_id)
                assert check_disabled["enabled"] is False

            except Exception as e:
                if "501" in str(e) or "feature not enabled" in str(e).lower():
                    pytest.skip(
                        "Management permissions feature not enabled (requires admin-fine-grained-authz)"
                    )
                else:
                    raise

        finally:
            if client_db_id:
                await delete_client(client_db_id)

    async def test_management_permissions_structure(self, unique_client_id):
        """Test the structure of management permissions response."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Permissions Structure Client",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            try:
                # Enable permissions to get full structure
                enabled_result = await update_client_management_permissions(
                    client_db_id, enabled=True
                )

                # Verify response structure
                assert "enabled" in enabled_result
                assert enabled_result["enabled"] is True

                # When enabled, should contain resource server information
                # The exact field name may be 'resource' or 'resourceServerId'
                has_resource_info = (
                    "resource" in enabled_result or "resourceServerId" in enabled_result
                )
                assert has_resource_info, (
                    "Expected resource information when permissions are enabled"
                )

                # Clean up by disabling
                await update_client_management_permissions(client_db_id, enabled=False)

            except Exception as e:
                if "501" in str(e) or "feature not enabled" in str(e).lower():
                    pytest.skip(
                        "Management permissions feature not enabled (requires admin-fine-grained-authz)"
                    )
                else:
                    raise

        finally:
            if client_db_id:
                await delete_client(client_db_id)

    async def test_management_permissions_persistence(self, unique_client_id):
        """Test that management permissions persist after enabling."""
        client_db_id = None

        try:
            # Create a test client
            await create_client(
                client_id=unique_client_id,
                name="Permissions Persistence Client",
                enabled=True,
            )

            # Find the client
            clients = await list_clients(client_id=unique_client_id)
            test_client = next(
                (c for c in clients if c["clientId"] == unique_client_id), None
            )
            client_db_id = test_client["id"]

            try:
                # Enable permissions
                await update_client_management_permissions(client_db_id, enabled=True)

                # Get permissions multiple times to verify persistence
                for _ in range(3):
                    permissions = await get_client_management_permissions(client_db_id)
                    assert permissions["enabled"] is True

                # Disable and verify persistence of disabled state
                await update_client_management_permissions(client_db_id, enabled=False)

                for _ in range(3):
                    permissions = await get_client_management_permissions(client_db_id)
                    assert permissions["enabled"] is False

            except Exception as e:
                if "501" in str(e) or "feature not enabled" in str(e).lower():
                    pytest.skip(
                        "Management permissions feature not enabled (requires admin-fine-grained-authz)"
                    )
                else:
                    raise

        finally:
            if client_db_id:
                await delete_client(client_db_id)
