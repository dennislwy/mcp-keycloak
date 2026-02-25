"""
Integration tests for General Tools.

These tests require a running Keycloak server with admin access.
Configure the server details in your .env file.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import general_tools

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

    pytest = MockPytest()


@pytest.mark.integration
class TestServerInfo:
    """Test server information operations."""

    async def test_get_server_info(self):
        """Test getting server information."""
        server_info = await general_tools.get_server_info()

        # Verify server_info is a dictionary and not empty
        assert isinstance(server_info, dict)
        assert len(server_info) > 0

        # Verify profileInfo exists (common across versions)
        assert "profileInfo" in server_info
        profile_info = server_info["profileInfo"]
        assert "name" in profile_info

        # Verify themes section exists
        assert "themes" in server_info
        themes = server_info["themes"]
        assert isinstance(themes, dict)

        # Verify providers section exists
        assert "providers" in server_info
        providers = server_info["providers"]
        assert isinstance(providers, dict)

    async def test_server_info_structure(self):
        """Test that server info has expected top-level keys."""
        server_info = await general_tools.get_server_info()

        # Core keys that should exist in all Keycloak versions
        core_keys = ["profileInfo", "themes", "providers"]

        for key in core_keys:
            assert key in server_info, (
                f"Expected core key '{key}' not found in server info"
            )

        # Print all available top-level keys for debugging
        print(f"Available keys: {list(server_info.keys())}")

    async def test_server_info_profile(self):
        """Test that server info contains valid profile information."""
        server_info = await general_tools.get_server_info()

        profile_info = server_info["profileInfo"]
        assert "name" in profile_info
        assert isinstance(profile_info["name"], str)
        assert len(profile_info["name"]) > 0

        print(f"Keycloak Profile: {profile_info['name']}")

        # Check for features information (if available)
        if "disabledFeatures" in profile_info:
            assert isinstance(profile_info["disabledFeatures"], list)
            print(
                f"Disabled features count: {len(profile_info.get('disabledFeatures', []))}"
            )

    async def test_server_info_features(self):
        """Test that server info contains feature information."""
        server_info = await general_tools.get_server_info()

        # Features key may exist
        if "features" in server_info:
            features = server_info["features"]
            assert isinstance(features, list)
            assert len(features) > 0

            # Each feature should have expected structure
            for feature in features[:3]:  # Check first 3 features
                assert "name" in feature
                assert "enabled" in feature
                print(f"Feature: {feature['name']}, Enabled: {feature['enabled']}")

    async def test_server_info_themes(self):
        """Test that server info contains theme information."""
        server_info = await general_tools.get_server_info()

        themes = server_info["themes"]
        assert isinstance(themes, dict)
        assert len(themes) > 0, "Should have at least one theme type"

        # Verify theme structure
        theme_count = 0
        for theme_type, theme_list in themes.items():
            assert isinstance(theme_list, list)
            theme_count += len(theme_list)
            if len(theme_list) > 0:
                # Each theme should have a name
                first_theme = theme_list[0]
                assert "name" in first_theme
                print(
                    f"Theme type: {theme_type}, Count: {len(theme_list)}, First theme: {first_theme['name']}"
                )

        assert theme_count > 0, "Should have at least one theme available"

    async def test_server_info_providers(self):
        """Test that server info contains provider information."""
        server_info = await general_tools.get_server_info()

        providers = server_info["providers"]
        assert isinstance(providers, dict)
        assert len(providers) > 0, "Should have at least one provider type"

        # Check provider structure
        provider_count = 0
        for provider_type, provider_data in list(providers.items())[:5]:
            print(f"Provider type: {provider_type}, Data type: {type(provider_data)}")
            provider_count += 1

        assert provider_count > 0, "Should have providers available"

    async def test_server_info_contains_useful_data(self):
        """Test that server info contains useful operational data."""
        server_info = await general_tools.get_server_info()

        # Check for any operational information keys
        operational_keys = [
            "systemInfo",
            "memoryInfo",
            "profileInfo",
            "features",
            "themes",
            "providers",
            "protocolMapperTypes",
            "builtinProtocolMappers",
            "clientInstallations",
            "componentTypes",
            "passwordPolicies",
            "enums",
            "cryptoInfo",
            "identityProviders",
        ]

        found_keys = [key for key in operational_keys if key in server_info]
        assert len(found_keys) >= 3, (
            f"Should have at least 3 operational keys, found: {found_keys}"
        )

        print(f"Found operational keys: {found_keys}")
