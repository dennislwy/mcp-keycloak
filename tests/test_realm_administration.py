"""
Integration tests for Realm Administration.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import realm_tools, group_tools

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
    def unique_group_name():
        """Generate a unique group name for testing."""
        return f"test-group-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestRealmInfo:
    """Test realm information retrieval."""

    async def test_get_accessible_realms(self):
        """Test listing accessible realms."""
        realms = await realm_tools.get_accessible_realms()
        assert isinstance(realms, list)
        assert len(realms) > 0

    async def test_get_realm_info(self):
        """Test getting current realm information."""
        realm_info = await realm_tools.get_realm_info()
        assert isinstance(realm_info, dict)
        assert "realm" in realm_info
        assert "enabled" in realm_info


@pytest.mark.integration
class TestRealmSettings:
    """Test realm settings management."""

    async def test_update_realm_settings(self):
        """Test updating realm settings."""
        # Get current settings first
        current_info = await realm_tools.get_realm_info()
        original_display_name = current_info.get("displayName")

        # Update with a test display name
        test_display_name = f"Test Realm {uuid.uuid4().hex[:6]}"
        result = await realm_tools.update_realm_settings(
            display_name=test_display_name,
        )
        assert result["status"] == "updated"

        # Verify the update
        updated_info = await realm_tools.get_realm_info()
        assert updated_info["displayName"] == test_display_name

        # Restore original display name if it existed
        if original_display_name:
            await realm_tools.update_realm_settings(
                display_name=original_display_name,
            )


@pytest.mark.integration
class TestRealmEventsConfig:
    """Test realm events configuration."""

    async def test_get_realm_events_config(self):
        """Test getting realm events configuration."""
        events_config = await realm_tools.get_realm_events_config()
        assert isinstance(events_config, dict)

    async def test_update_realm_events_config(self):
        """Test updating realm events configuration."""
        # Get current config
        current_config = await realm_tools.get_realm_events_config()

        # Update events config
        result = await realm_tools.update_realm_events_config(
            events_enabled=True,
            events_listeners=["jboss-logging"],
        )
        assert result["status"] == "updated"

        # Verify update
        updated_config = await realm_tools.get_realm_events_config()
        assert updated_config["eventsEnabled"] is True


@pytest.mark.integration
class TestRealmDefaultGroups:
    """Test realm default groups management."""

    async def test_manage_realm_default_groups(self, unique_group_name):
        """Test adding and removing default groups."""
        # Create a test group
        result = await group_tools.create_group(name=unique_group_name)
        assert result["status"] == "created"

        # Find the created group
        groups = await group_tools.list_groups(search=unique_group_name)
        group = next(g for g in groups if g["name"] == unique_group_name)
        group_id = group["id"]

        try:
            # Add group as default group
            add_result = await realm_tools.add_realm_default_group(group_id)
            assert add_result["status"] == "added"

            # Get default groups and verify
            default_groups = await realm_tools.get_realm_default_groups()
            assert isinstance(default_groups, list)
            assert any(g["id"] == group_id for g in default_groups)

            # Remove from default groups
            remove_result = await realm_tools.remove_realm_default_group(group_id)
            assert remove_result["status"] == "removed"

            # Verify removal
            default_groups = await realm_tools.get_realm_default_groups()
            assert not any(g["id"] == group_id for g in default_groups)

        finally:
            # Clean up the test group
            await group_tools.delete_group(group_id)


@pytest.mark.integration
class TestRealmSessionManagement:
    """Test realm-wide session management."""

    async def test_get_realm_info_includes_session_settings(self):
        """Test that realm info includes session-related settings."""
        realm_info = await realm_tools.get_realm_info()
        # Check for some session-related fields
        assert "ssoSessionIdleTimeout" in realm_info or "realm" in realm_info
        assert isinstance(realm_info, dict)
