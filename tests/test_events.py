"""
Integration tests for Events Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.

Note: Some tests may be skipped based on server capabilities.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import events_tools

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


@pytest.mark.integration
class TestEventsConfiguration:
    """Test events configuration management."""

    async def test_get_events_config(self):
        """Test retrieving events configuration."""
        config = await events_tools.get_events_config()
        assert isinstance(config, dict)
        # Config should have expected keys
        assert "eventsEnabled" in config or "adminEventsEnabled" in config

    async def test_update_events_config(self):
        """Test updating events configuration."""
        # Get current config
        original_config = await events_tools.get_events_config()

        try:
            # Update events config
            result = await events_tools.update_events_config(
                events_enabled=True,
                events_expiration=3600,
                admin_events_enabled=True,
                admin_events_details_enabled=True,
            )
            assert result["status"] == "updated"

            # Verify update
            updated_config = await events_tools.get_events_config()
            assert updated_config["eventsEnabled"] is True
            assert updated_config["adminEventsEnabled"] is True

        finally:
            # Restore original config
            await events_tools.update_events_config(
                events_enabled=original_config.get("eventsEnabled", False),
                events_expiration=original_config.get("eventsExpiration", 86400),
                admin_events_enabled=original_config.get("adminEventsEnabled", False),
                admin_events_details_enabled=original_config.get(
                    "adminEventsDetailsEnabled", False
                ),
            )

    async def test_enable_user_events_convenience(self):
        """Test convenience function for enabling user events."""
        # Get current config
        original_config = await events_tools.get_events_config()

        try:
            # Enable user events
            result = await events_tools.enable_user_events(
                expiration_seconds=7200,
            )
            assert result["status"] == "updated"

            # Verify
            config = await events_tools.get_events_config()
            assert config["eventsEnabled"] is True
            assert config["eventsExpiration"] == 7200

        finally:
            # Restore
            await events_tools.update_events_config(
                events_enabled=original_config.get("eventsEnabled", False),
                events_expiration=original_config.get("eventsExpiration", 86400),
            )

    async def test_enable_admin_events_convenience(self):
        """Test convenience function for enabling admin events."""
        # Get current config
        original_config = await events_tools.get_events_config()

        try:
            # Enable admin events
            result = await events_tools.enable_admin_events(include_details=True)
            assert result["status"] == "updated"

            # Verify
            config = await events_tools.get_events_config()
            assert config["adminEventsEnabled"] is True
            assert config.get("adminEventsDetailsEnabled") is True

        finally:
            # Restore
            await events_tools.update_events_config(
                admin_events_enabled=original_config.get("adminEventsEnabled", False),
                admin_events_details_enabled=original_config.get(
                    "adminEventsDetailsEnabled", False
                ),
            )


@pytest.mark.integration
class TestUserEvents:
    """Test user events management."""

    async def test_get_user_events(self):
        """Test retrieving user events."""
        # First enable events
        await events_tools.enable_user_events()

        # Get events
        events = await events_tools.get_user_events(max=10)
        assert isinstance(events, list)
        # Events may be empty if no user activity yet
        if events:
            event = events[0]
            # Check for expected fields
            assert "type" in event or "time" in event

    async def test_get_user_events_with_filters(self):
        """Test retrieving user events with filters."""
        # Enable events
        await events_tools.enable_user_events()

        # Get events with filters
        events = await events_tools.get_user_events(
            max=5,
            event_type=["LOGIN", "LOGOUT", "LOGIN_ERROR"],
        )
        assert isinstance(events, list)

    async def test_get_recent_login_events_convenience(self):
        """Test convenience function for recent login events."""
        # Enable events
        await events_tools.enable_user_events()

        # Get recent login events
        events = await events_tools.get_recent_login_events(max_results=20)
        assert isinstance(events, list)


@pytest.mark.integration
class TestAdminEvents:
    """Test admin events management."""

    async def test_get_admin_events(self):
        """Test retrieving admin events."""
        # First enable admin events
        await events_tools.enable_admin_events()

        # Get events
        events = await events_tools.get_admin_events(max=10)
        assert isinstance(events, list)
        # Events may be empty if no admin activity yet
        if events:
            event = events[0]
            # Check for expected fields
            assert (
                "operationType" in event or "resourceType" in event or "time" in event
            )

    async def test_get_admin_events_with_filters(self):
        """Test retrieving admin events with filters."""
        # Enable admin events
        await events_tools.enable_admin_events()

        # Get events with operation type filter
        events = await events_tools.get_admin_events(
            max=5,
            operation_types=["CREATE", "UPDATE", "DELETE"],
        )
        assert isinstance(events, list)

    async def test_get_admin_events_by_resource_type(self):
        """Test filtering admin events by resource type."""
        # Enable admin events
        await events_tools.enable_admin_events()

        # Get events for specific resource types
        events = await events_tools.get_admin_events(
            max=10,
            resource_types=["USER", "CLIENT"],
        )
        assert isinstance(events, list)

    async def test_get_recent_admin_changes_convenience(self):
        """Test convenience function for recent admin changes."""
        # Enable admin events
        await events_tools.enable_admin_events()

        # Get recent admin changes
        events = await events_tools.get_recent_admin_changes(max_results=20)
        assert isinstance(events, list)

    async def test_get_recent_admin_changes_filtered(self):
        """Test filtered admin changes."""
        # Enable admin events
        await events_tools.enable_admin_events()

        # Get recent user-related changes
        events = await events_tools.get_recent_admin_changes(
            resource_type="USER",
            operation_type="CREATE",
            max_results=10,
        )
        assert isinstance(events, list)


@pytest.mark.integration
class TestEventsClearance:
    """Test clearing events."""

    async def test_clear_user_events(self):
        """Test clearing all user events."""
        # Enable events first
        await events_tools.enable_user_events()

        # Clear events
        result = await events_tools.clear_user_events()
        assert result["status"] == "cleared"

        # Events should be empty or have only new events
        events = await events_tools.get_user_events(max=100)
        # Should either be empty or have very recent events only
        assert isinstance(events, list)

    async def test_clear_admin_events(self):
        """Test clearing all admin events."""
        # Enable admin events first
        await events_tools.enable_admin_events()

        # Clear events
        result = await events_tools.clear_admin_events()
        assert result["status"] == "cleared"

        # Events should be empty or have only new events
        events = await events_tools.get_admin_events(max=100)
        # Should either be empty or have very recent events only
        assert isinstance(events, list)


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Events Management Integration Tests ===\n")

    # Test events configuration
    test_config = TestEventsConfiguration()

    print("Testing get events config...")
    try:
        await test_config.test_get_events_config()
        print("[PASS] Get events config test passed")
    except Exception as e:
        print(f"[FAIL] Get events config test failed: {e}")

    print("\nTesting update events config...")
    try:
        await test_config.test_update_events_config()
        print("[PASS] Update events config test passed")
    except Exception as e:
        print(f"[FAIL] Update events config test failed: {e}")

    print("\nTesting enable user events convenience function...")
    try:
        await test_config.test_enable_user_events_convenience()
        print("[PASS] Enable user events convenience test passed")
    except Exception as e:
        print(f"[FAIL] Enable user events convenience test failed: {e}")

    print("\nTesting enable admin events convenience function...")
    try:
        await test_config.test_enable_admin_events_convenience()
        print("[PASS] Enable admin events convenience test passed")
    except Exception as e:
        print(f"[FAIL] Enable admin events convenience test failed: {e}")

    # Test user events
    test_user_events = TestUserEvents()

    print("\nTesting get user events...")
    try:
        await test_user_events.test_get_user_events()
        print("[PASS] Get user events test passed")
    except Exception as e:
        print(f"[FAIL] Get user events test failed: {e}")

    print("\nTesting get user events with filters...")
    try:
        await test_user_events.test_get_user_events_with_filters()
        print("[PASS] Get user events with filters test passed")
    except Exception as e:
        print(f"[FAIL] Get user events with filters test failed: {e}")

    print("\nTesting get recent login events...")
    try:
        await test_user_events.test_get_recent_login_events_convenience()
        print("[PASS] Get recent login events test passed")
    except Exception as e:
        print(f"[FAIL] Get recent login events test failed: {e}")

    # Test admin events
    test_admin_events = TestAdminEvents()

    print("\nTesting get admin events...")
    try:
        await test_admin_events.test_get_admin_events()
        print("[PASS] Get admin events test passed")
    except Exception as e:
        print(f"[FAIL] Get admin events test failed: {e}")

    print("\nTesting get admin events with filters...")
    try:
        await test_admin_events.test_get_admin_events_with_filters()
        print("[PASS] Get admin events with filters test passed")
    except Exception as e:
        print(f"[FAIL] Get admin events with filters test failed: {e}")

    print("\nTesting get admin events by resource type...")
    try:
        await test_admin_events.test_get_admin_events_by_resource_type()
        print("[PASS] Get admin events by resource type test passed")
    except Exception as e:
        print(f"[FAIL] Get admin events by resource type test failed: {e}")

    print("\nTesting get recent admin changes...")
    try:
        await test_admin_events.test_get_recent_admin_changes_convenience()
        print("[PASS] Get recent admin changes test passed")
    except Exception as e:
        print(f"[FAIL] Get recent admin changes test failed: {e}")

    print("\nTesting get filtered admin changes...")
    try:
        await test_admin_events.test_get_recent_admin_changes_filtered()
        print("[PASS] Get filtered admin changes test passed")
    except Exception as e:
        print(f"[FAIL] Get filtered admin changes test failed: {e}")

    # Test event clearance
    test_clearance = TestEventsClearance()

    print("\nTesting clear user events...")
    try:
        await test_clearance.test_clear_user_events()
        print("[PASS] Clear user events test passed")
    except Exception as e:
        print(f"[FAIL] Clear user events test failed: {e}")

    print("\nTesting clear admin events...")
    try:
        await test_clearance.test_clear_admin_events()
        print("[PASS] Clear admin events test passed")
    except Exception as e:
        print(f"[FAIL] Clear admin events test failed: {e}")

    print("\n=== Test run completed! ===\n")


if __name__ == "__main__":
    run_tests()
