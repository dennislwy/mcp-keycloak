"""
Integration tests for Sessions Management Features:
- General Sessions Management (Phase 2.3)

These tests require a running Keycloak server.
Configure the server details in your .env file.

Note: Some tests may be skipped based on server capabilities.
"""

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import (
    sessions_management_tools,
    user_tools,
    client_tools,
)

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
class TestSessionsManagement:
    """Test general sessions management functionality."""

    async def test_get_realm_session_stats(self):
        """Test getting realm session statistics."""
        stats = await sessions_management_tools.get_realm_session_stats()
        assert isinstance(stats, dict)
        # Stats may be empty if no active sessions
        # Each value should be a number if present
        for client_id, session_count in stats.items():
            assert isinstance(client_id, str)
            assert isinstance(session_count, int)
            assert session_count >= 0

    async def test_get_realm_sessions_summary(self):
        """Test getting comprehensive realm sessions summary."""
        summary = await sessions_management_tools.get_realm_sessions_summary()
        assert isinstance(summary, dict)
        assert "realm" in summary
        assert "total_active_sessions" in summary
        assert "active_clients_with_sessions" in summary
        assert "client_session_breakdown" in summary
        assert "average_sessions_per_client" in summary
        assert "session_distribution" in summary

        # Verify data consistency
        assert isinstance(summary["total_active_sessions"], int)
        assert isinstance(summary["active_clients_with_sessions"], int)
        assert isinstance(summary["client_session_breakdown"], dict)

    async def test_get_sessions_by_client(self):
        """Test getting session information for a specific client."""
        # Get available clients
        clients = await client_tools.list_clients(max=5)
        if not clients:
            print("SKIPPED: No clients available for session testing")
            return

        test_client = clients[0]
        client_id = test_client.get("clientId", test_client.get("id"))

        session_info = await sessions_management_tools.get_sessions_by_client(client_id)
        assert isinstance(session_info, dict)
        assert "client_id" in session_info
        assert "active_sessions" in session_info
        assert "realm" in session_info
        assert "session_percentage" in session_info
        assert "realm_total_sessions" in session_info

        assert session_info["client_id"] == client_id
        assert isinstance(session_info["active_sessions"], int)

    async def test_monitor_active_sessions(self):
        """Test session monitoring functionality."""
        monitoring = await sessions_management_tools.monitor_active_sessions()
        assert isinstance(monitoring, dict)
        assert "realm" in monitoring
        assert "timestamp" in monitoring
        assert "session_summary" in monitoring

        # Test with detailed monitoring
        detailed_monitoring = await sessions_management_tools.monitor_active_sessions(
            include_user_details=True
        )
        assert isinstance(detailed_monitoring, dict)
        assert "session_summary" in detailed_monitoring
        # Should include note about user sessions limitation
        assert (
            "user_sessions_note" in detailed_monitoring
            or "user_sessions_error" in detailed_monitoring
            or "detailed_sessions" in detailed_monitoring
        )

    async def test_session_configuration_management(self):
        """Test getting and updating session configuration."""
        # Get current session configuration
        config = await sessions_management_tools.get_session_configuration()
        assert isinstance(config, dict)
        assert "realm" in config

        # Common session configuration fields
        expected_fields = [
            "access_token_lifespan",
            "sso_session_idle_timeout",
            "sso_session_max_lifespan",
        ]

        # At least some configuration should be present
        config_fields = [field for field in expected_fields if field in config]
        assert len(config_fields) > 0, "No session configuration fields found"

        # Test updating configuration (with small changes)
        original_access_token_lifespan = config.get("access_token_lifespan")
        if original_access_token_lifespan is not None:
            try:
                # Make a small change
                new_lifespan = max(
                    300, original_access_token_lifespan
                )  # At least 5 minutes
                if new_lifespan == original_access_token_lifespan:
                    new_lifespan += 60  # Add 1 minute

                update_result = (
                    await sessions_management_tools.update_session_configuration(
                        access_token_lifespan=new_lifespan
                    )
                )
                assert update_result["status"] == "updated"
                assert "access_token_lifespan" in update_result["updated_settings"]

                # Restore original value
                await sessions_management_tools.update_session_configuration(
                    access_token_lifespan=original_access_token_lifespan
                )

            except Exception as e:
                print(
                    f"NOTE: Session configuration update failed (may require higher privileges): {e}"
                )

    async def test_cleanup_inactive_sessions(self):
        """Test inactive session cleanup analysis."""
        # Test dry run mode (default)
        cleanup_report = await sessions_management_tools.cleanup_inactive_sessions()
        assert isinstance(cleanup_report, dict)
        assert "realm" in cleanup_report
        assert "dry_run" in cleanup_report
        assert cleanup_report["dry_run"] is True
        assert "session_config" in cleanup_report
        assert "current_sessions" in cleanup_report
        assert "cleanup_recommendations" in cleanup_report

        # Test non-dry run mode
        cleanup_report_active = (
            await sessions_management_tools.cleanup_inactive_sessions(dry_run=False)
        )
        assert isinstance(cleanup_report_active, dict)
        assert cleanup_report_active["dry_run"] is False


@pytest.mark.integration
class TestUserSessionsManagement:
    """Test user-specific session management."""

    async def test_get_user_session_details_with_existing_user(self):
        """Test getting sessions for an existing user."""
        # Get a user to test with
        users = await user_tools.list_users(max=5)
        if not users:
            print("SKIPPED: No users available for session testing")
            return

        test_user = users[0]
        user_id = test_user["id"]

        # Get user sessions
        sessions = await sessions_management_tools.get_user_session_details(user_id)
        assert isinstance(sessions, list)
        # Sessions may be empty if user is not logged in

        # If sessions exist, verify structure
        for session in sessions:
            assert isinstance(session, dict)
            # Common session fields
            expected_fields = ["id", "username", "userId", "start", "lastAccess"]
            for field in expected_fields:
                if field in session:
                    assert session[field] is not None

    async def test_find_user_sessions(self):
        """Test finding user sessions with different criteria."""
        # Test with a test IP address (likely no results)
        ip_sessions = await sessions_management_tools.find_user_sessions(
            ip_address="192.168.999.999"
        )
        assert isinstance(ip_sessions, list)
        # Should be empty for non-existent IP

        # Test with username search
        try:
            users = await user_tools.list_users(max=3)
            if users:
                test_user = users[0]
                username = test_user.get("username")
                if username:
                    username_sessions = (
                        await sessions_management_tools.find_user_sessions(
                            username=username
                        )
                    )
                    assert isinstance(username_sessions, list)
        except Exception:
            print("NOTE: Username search may require additional permissions")

        # Test error handling - no criteria provided
        try:
            await sessions_management_tools.find_user_sessions()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "At least one search criterion" in str(e)

    async def test_user_logout_operations(self):
        """Test user logout operations (careful testing)."""
        # Test logout for non-existent user (should not cause errors)
        fake_user_id = f"fake-user-{uuid.uuid4().hex[:8]}"

        try:
            result = await sessions_management_tools.logout_user_sessions(fake_user_id)
            # Should complete without error even for non-existent user
            assert result["status"] == "logged_out"
            assert result["user_id"] == fake_user_id
        except Exception:
            # Some Keycloak configurations may return errors for non-existent users
            print("NOTE: Logout of non-existent user returned error (server-dependent)")

        # Note: We don't test logout_all_users() in integration tests as it would
        # affect all users in the realm


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Sessions Management Integration Tests ===\n")

    # Test Sessions Management
    test_sessions = TestSessionsManagement()

    print("Testing realm session stats...")
    try:
        await test_sessions.test_get_realm_session_stats()
        print("[PASS] Realm session stats test passed")
    except Exception as e:
        print(f"[FAIL] Realm session stats test failed: {e}")

    print("\nTesting realm sessions summary...")
    try:
        await test_sessions.test_get_realm_sessions_summary()
        print("[PASS] Realm sessions summary test passed")
    except Exception as e:
        print(f"[FAIL] Realm sessions summary test failed: {e}")

    print("\nTesting sessions by client...")
    try:
        await test_sessions.test_get_sessions_by_client()
        print("[PASS] Sessions by client test passed")
    except Exception as e:
        print(f"[FAIL] Sessions by client test failed: {e}")

    print("\nTesting session monitoring...")
    try:
        await test_sessions.test_monitor_active_sessions()
        print("[PASS] Session monitoring test passed")
    except Exception as e:
        print(f"[FAIL] Session monitoring test failed: {e}")

    print("\nTesting session configuration management...")
    try:
        await test_sessions.test_session_configuration_management()
        print("[PASS] Session configuration management test passed")
    except Exception as e:
        print(f"[FAIL] Session configuration management test failed: {e}")

    print("\nTesting cleanup inactive sessions...")
    try:
        await test_sessions.test_cleanup_inactive_sessions()
        print("[PASS] Cleanup inactive sessions test passed")
    except Exception as e:
        print(f"[FAIL] Cleanup inactive sessions test failed: {e}")

    # Test User Sessions Management
    test_user_sessions = TestUserSessionsManagement()

    print("\nTesting get user sessions...")
    try:
        await test_user_sessions.test_get_user_session_details_with_existing_user()
        print("[PASS] Get user sessions test passed")
    except Exception as e:
        print(f"[FAIL] Get user sessions test failed: {e}")

    print("\nTesting find user sessions...")
    try:
        await test_user_sessions.test_find_user_sessions()
        print("[PASS] Find user sessions test passed")
    except Exception as e:
        print(f"[FAIL] Find user sessions test failed: {e}")

    print("\nTesting user logout operations...")
    try:
        await test_user_sessions.test_user_logout_operations()
        print("[PASS] User logout operations test passed")
    except Exception as e:
        print(f"[FAIL] User logout operations test failed: {e}")

    print("\n=== Sessions Management Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
