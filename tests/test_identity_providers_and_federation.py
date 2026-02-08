"""
Integration tests for Identity Providers and User Federation.

These tests require a running Keycloak server.
Configure the server details in your .env file.

Note: Some tests may be skipped based on server capabilities.
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import identity_provider_tools, user_federation_tools

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
    def unique_idp_alias():
        """Generate a unique IDP alias for testing."""
        return f"test-idp-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def unique_component_name():
        """Generate a unique component name for testing."""
        return f"test-component-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestIdentityProviders:
    """Test identity provider management."""

    async def test_identity_provider_lifecycle(self, unique_idp_alias):
        """Test creating, reading, updating, and deleting an identity provider."""
        # Create identity provider (OIDC generic provider)
        result = await identity_provider_tools.create_identity_provider(
            alias=unique_idp_alias,
            provider_id="oidc",
            enabled=True,
            display_name="Test OIDC Provider",
            config={
                "clientId": "test-client",
                "clientSecret": "test-secret",
                "authorizationUrl": "https://example.com/auth",
                "tokenUrl": "https://example.com/token",
            },
        )
        assert result["status"] == "created"

        try:
            # List identity providers
            providers = await identity_provider_tools.list_identity_providers()
            test_provider = next(
                (p for p in providers if p["alias"] == unique_idp_alias), None
            )
            assert test_provider is not None
            assert test_provider["providerId"] == "oidc"

            # Get specific identity provider
            provider = await identity_provider_tools.get_identity_provider(
                unique_idp_alias
            )
            assert provider["alias"] == unique_idp_alias
            assert provider["displayName"] == "Test OIDC Provider"

            # Update identity provider
            result = await identity_provider_tools.update_identity_provider(
                alias=unique_idp_alias,
                display_name="Updated Test Provider",
                trust_email=True,
            )
            assert result["status"] == "updated"

            # Verify update
            provider = await identity_provider_tools.get_identity_provider(
                unique_idp_alias
            )
            assert provider["displayName"] == "Updated Test Provider"
            assert provider.get("trustEmail")

        finally:
            # Delete identity provider
            result = await identity_provider_tools.delete_identity_provider(
                unique_idp_alias
            )
            assert result["status"] == "deleted"

            # Verify deletion
            providers = await identity_provider_tools.list_identity_providers()
            assert not any(p["alias"] == unique_idp_alias for p in providers)

    async def test_identity_provider_mappers(self, unique_idp_alias):
        """Test identity provider mapper management."""
        # Create identity provider first
        await identity_provider_tools.create_identity_provider(
            alias=unique_idp_alias,
            provider_id="oidc",
            enabled=True,
            config={
                "clientId": "test",
                "clientSecret": "secret",
                "authorizationUrl": "https://example.com/auth",
                "tokenUrl": "https://example.com/token",
            },
        )

        try:
            mapper_name = f"test-mapper-{uuid.uuid4().hex[:8]}"

            # Create mapper
            result = await identity_provider_tools.create_identity_provider_mapper(
                alias=unique_idp_alias,
                name=mapper_name,
                identity_provider_mapper="oidc-user-attribute-idp-mapper",
                config={
                    "claim": "email",
                    "user.attribute": "email",
                },
            )
            assert result["status"] == "created"

            # List mappers
            mappers = await identity_provider_tools.list_identity_provider_mappers(
                unique_idp_alias
            )
            test_mapper = next((m for m in mappers if m["name"] == mapper_name), None)
            assert test_mapper is not None
            mapper_id = test_mapper["id"]

            # Get specific mapper
            mapper = await identity_provider_tools.get_identity_provider_mapper(
                unique_idp_alias, mapper_id
            )
            assert mapper["name"] == mapper_name

            # Update mapper
            result = await identity_provider_tools.update_identity_provider_mapper(
                alias=unique_idp_alias,
                mapper_id=mapper_id,
                name=f"{mapper_name}-updated",
            )
            assert result["status"] == "updated"

            # Delete mapper
            result = await identity_provider_tools.delete_identity_provider_mapper(
                unique_idp_alias, mapper_id
            )
            assert result["status"] == "deleted"

        finally:
            # Clean up
            await identity_provider_tools.delete_identity_provider(unique_idp_alias)

    async def test_google_identity_provider_convenience(self, unique_idp_alias):
        """Test Google identity provider convenience function."""
        # Create Google provider
        result = await identity_provider_tools.create_google_identity_provider(
            alias=unique_idp_alias,
            client_id="test-google-client-id",
            client_secret="test-google-secret",
            enabled=True,
        )
        assert result["status"] == "created"

        try:
            # Verify it was created correctly
            provider = await identity_provider_tools.get_identity_provider(
                unique_idp_alias
            )
            assert provider["providerId"] == "google"
            assert provider["config"]["clientId"] == "test-google-client-id"

        finally:
            # Clean up
            await identity_provider_tools.delete_identity_provider(unique_idp_alias)


@pytest.mark.integration
class TestUserFederation:
    """Test user federation/storage management."""

    async def test_component_lifecycle(self, unique_component_name):
        """Test creating, reading, updating, and deleting components."""
        # Create a simple component (using a mock provider for testing)
        result = await user_federation_tools.create_component(
            name=unique_component_name,
            provider_id="allowed-client-templates",
            provider_type="org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy",
            config={"allow-default-scopes": ["true"]},
        )
        assert result["status"] == "created"

        # List components and find ours
        components = await user_federation_tools.list_components(
            name=unique_component_name
        )
        test_component = next(
            (c for c in components if c["name"] == unique_component_name), None
        )
        assert test_component is not None
        component_id = test_component["id"]

        try:
            # Get specific component
            component = await user_federation_tools.get_component(component_id)
            assert component["name"] == unique_component_name

            # Update component
            result = await user_federation_tools.update_component(
                component_id=component_id,
                config={"allow-default-scopes": ["false"]},
            )
            assert result["status"] == "updated"

            # Verify update
            component = await user_federation_tools.get_component(component_id)
            assert component["config"]["allow-default-scopes"] == ["false"]

        finally:
            # Delete component
            result = await user_federation_tools.delete_component(component_id)
            assert result["status"] == "deleted"

            # Verify deletion
            components = await user_federation_tools.list_components(
                name=unique_component_name
            )
            assert len(components) == 0

    async def test_list_user_storage_providers(self):
        """Test listing user storage providers."""
        # This should work even if there are no custom providers
        providers = await user_federation_tools.list_user_storage_providers()
        assert isinstance(providers, list)
        # The list might be empty, which is fine for testing

    async def test_list_components_with_filters(self):
        """Test listing components with various filters."""
        # List all components
        all_components = await user_federation_tools.list_components()
        assert isinstance(all_components, list)

        # List with type filter (should return specific types)
        typed_components = await user_federation_tools.list_components(
            type="org.keycloak.keys.KeyProvider"
        )
        assert isinstance(typed_components, list)
        # All returned components should match the type if any exist
        for comp in typed_components:
            assert comp["providerType"] == "org.keycloak.keys.KeyProvider"


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print(
        "\n=== Running Identity Providers and User Federation Integration Tests ===\n"
    )

    # Test identity providers
    test_idp = TestIdentityProviders()
    idp_alias = f"test-idp-{uuid.uuid4().hex[:8]}"

    print("Testing identity provider lifecycle...")
    try:
        await test_idp.test_identity_provider_lifecycle(idp_alias)
        print("[PASS] Identity provider lifecycle test passed")
    except Exception as e:
        print(f"[FAIL] Identity provider lifecycle test failed: {e}")

    idp_alias = f"test-idp-{uuid.uuid4().hex[:8]}"
    print("\nTesting identity provider mappers...")
    try:
        await test_idp.test_identity_provider_mappers(idp_alias)
        print("[PASS] Identity provider mappers test passed")
    except Exception as e:
        print(f"[FAIL] Identity provider mappers test failed: {e}")

    idp_alias = f"test-idp-{uuid.uuid4().hex[:8]}"
    print("\nTesting Google identity provider convenience function...")
    try:
        await test_idp.test_google_identity_provider_convenience(idp_alias)
        print("[PASS] Google identity provider convenience test passed")
    except Exception as e:
        print(f"[FAIL] Google identity provider convenience test failed: {e}")

    # Test user federation
    test_federation = TestUserFederation()
    component_name = f"test-component-{uuid.uuid4().hex[:8]}"

    print("\nTesting component lifecycle...")
    try:
        await test_federation.test_component_lifecycle(component_name)
        print("[PASS] Component lifecycle test passed")
    except Exception as e:
        print(f"[FAIL] Component lifecycle test failed: {e}")

    print("\nTesting list user storage providers...")
    try:
        await test_federation.test_list_user_storage_providers()
        print("[PASS] List user storage providers test passed")
    except Exception as e:
        print(f"[FAIL] List user storage providers test failed: {e}")

    print("\nTesting list components with filters...")
    try:
        await test_federation.test_list_components_with_filters()
        print("[PASS] List components with filters test passed")
    except Exception as e:
        print(f"[FAIL] List components with filters test failed: {e}")

    print("\n=== Test run completed! ===\n")


if __name__ == "__main__":
    run_tests()
