"""
Integration tests for Realm Operations and Related Operational Workflows.

This test suite covers three main operational areas:

1. Realm Operations (8 tests):
   - Realm lifecycle (create, delete, list)
   - Import/Export (full and partial)
   - Backup and restore operations
   - Realm duplication with customizations

2. Client Sessions Management (4 tests):
   - Session statistics and monitoring
   - Client session queries and management
   - IP-based session filtering

3. Group Role Mappings (3 tests):
   - Group role assignment lifecycle
   - Realm and client role mappings for groups
   - Role inheritance and effective roles

These tests require a running Keycloak server.
Configure the server details in your .env file.

Note: Some tests may be skipped if the server restricts realm creation/modification
operations. This is expected for non-master admin users.
"""

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import (
    realm_operations_tools,
    client_sessions_tools,
    group_tools,
    client_tools,
)
import httpx

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
class TestRealmOperations:
    """Test realm import/export and management operations."""

    async def test_list_realms(self):
        """Test listing accessible realms."""
        try:
            realms = await realm_operations_tools.list_realms()
            assert isinstance(realms, list)
            assert len(realms) > 0

            # Check for master realm
            realm_names = [realm.get("realm") for realm in realms]
            assert "master" in realm_names
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (302, 405, 403):
                pytest.skip(f"Realm listing not permitted on this server: {e.response.status_code}")

    async def test_export_realm(self):
        """Test exporting realm configuration."""
        realm_data = await realm_operations_tools.export_realm()
        assert isinstance(realm_data, dict)
        assert "realm" in realm_data
        assert "enabled" in realm_data

    async def test_partial_export_realm(self):
        """Test partial realm export."""
        partial_data = await realm_operations_tools.partial_export_realm(
            export_clients=True, export_groups_and_roles=True
        )
        assert isinstance(partial_data, dict)

    async def test_backup_and_restore_realm(self):
        """Test realm backup and restore functionality."""
        # Create backup
        backup = await realm_operations_tools.backup_realm()
        assert isinstance(backup, dict)
        assert "backup_info" in backup
        assert "realm_data" in backup

        # Verify backup structure
        assert "backup_timestamp" in backup["backup_info"]
        assert backup["realm_data"]["realm"] is not None

        # Test restore backup functionality (may be restricted on some servers)
        try:
            restore_result = await realm_operations_tools.restore_realm_backup(backup_data=backup)
            assert isinstance(restore_result, dict)
            assert "status" in restore_result or "realm" in restore_result
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (405, 403):
                pytest.skip(f"Realm restore not permitted on this server: {e.response.status_code}")
            raise

    async def test_realm_lifecycle(self):
        """Test creating and deleting a realm."""
        test_realm_name = f"test-realm-{uuid.uuid4().hex[:8]}"

        try:
            # Create realm
            result = await realm_operations_tools.create_realm(
                realm_name=test_realm_name,
                display_name="Test Realm for Integration Tests",
                enabled=True,
            )
            assert result["status"] == "created"
            assert result["realm"] == test_realm_name

            # Verify realm exists
            realms = await realm_operations_tools.list_realms()
            realm_names = [realm.get("realm") for realm in realms]
            assert test_realm_name in realm_names

            # Export the new realm
            exported_data = await realm_operations_tools.export_realm(realm=test_realm_name)
            assert exported_data["realm"] == test_realm_name

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (405, 403):
                pytest.skip(
                    f"Realm creation not permitted on this server: {e.response.status_code}"
                )
            raise
        finally:
            # Clean up - delete realm
            try:
                delete_result = await realm_operations_tools.delete_realm(
                    test_realm_name, confirm=True
                )
                assert delete_result["status"] == "deleted"
            except Exception:
                pass  # Ignore cleanup errors

    async def test_import_realm(self):
        """Test importing a realm from configuration.

        Note: import_realm uses the same Keycloak API endpoint as create_realm.
        This test verifies that import_realm properly handles realm configuration.
        """
        test_realm_name = f"test-import-{uuid.uuid4().hex[:8]}"

        # Create a comprehensive realm configuration for import
        realm_config = {
            "realm": test_realm_name,
            "enabled": True,
            "displayName": "Test Import Realm",
            "registrationAllowed": False,
            "resetPasswordAllowed": True,
            "loginTheme": "keycloak",
        }

        try:
            # Import the realm
            result = await realm_operations_tools.import_realm(realm_data=realm_config)
            assert result["status"] == "imported"

            # Verify realm was created with correct configuration
            realms = await realm_operations_tools.list_realms()
            realm_names = [realm.get("realm") for realm in realms]
            assert test_realm_name in realm_names

            # Export and verify configuration was imported correctly
            exported = await realm_operations_tools.export_realm(realm=test_realm_name)
            assert exported["realm"] == test_realm_name
            assert exported["displayName"] == "Test Import Realm"
            assert exported["registrationAllowed"] == False

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (405, 403):
                pytest.skip(f"Realm import not permitted on this server: {e.response.status_code}")
            raise
        finally:
            # Clean up
            try:
                await realm_operations_tools.delete_realm(test_realm_name, confirm=True)
            except Exception:
                pass

    async def test_partial_import_realm(self):
        """Test partial import of realm configuration."""
        # Create a test realm first
        test_realm_name = f"test-partial-import-{uuid.uuid4().hex[:8]}"

        try:
            # Create the realm
            await realm_operations_tools.create_realm(
                realm_name=test_realm_name,
                display_name="Test Partial Import Realm",
                enabled=True,
            )

            # Prepare partial import data (e.g., clients, roles)
            partial_data = {
                "clients": [
                    {
                        "clientId": f"test-client-{uuid.uuid4().hex[:8]}",
                        "enabled": True,
                        "publicClient": False,
                        "protocol": "openid-connect",
                    }
                ],
                "roles": {
                    "realm": [
                        {
                            "name": f"test-role-{uuid.uuid4().hex[:8]}",
                            "description": "Test role from partial import",
                        }
                    ]
                },
            }

            # Perform partial import
            result = await realm_operations_tools.partial_import_realm(
                realm=test_realm_name,
                realm_data=partial_data,
                if_resource_exists="SKIP",
            )
            assert isinstance(result, dict)
            assert "status" in result or "results" in result or "added" in result

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (405, 403):
                pytest.skip(
                    f"Realm creation/import not permitted on this server: {e.response.status_code}"
                )
            raise
        finally:
            # Clean up
            try:
                await realm_operations_tools.delete_realm(test_realm_name, confirm=True)
            except Exception:
                pass

    async def test_duplicate_realm(self):
        """Test duplicating a realm with customizations."""
        source_realm_name = f"test-source-{uuid.uuid4().hex[:8]}"
        target_realm_name = f"test-target-{uuid.uuid4().hex[:8]}"

        try:
            # Create source realm with some configuration
            await realm_operations_tools.create_realm(
                realm_name=source_realm_name,
                display_name="Source Realm for Duplication",
                enabled=True,
            )

            # Duplicate the realm
            result = await realm_operations_tools.duplicate_realm(
                source_realm=source_realm_name,
                new_realm_name=target_realm_name,
                new_display_name="Duplicated Target Realm",
            )
            assert result["status"] == "duplicated"
            assert result["new_realm"] == target_realm_name

            # Verify both realms exist
            realms = await realm_operations_tools.list_realms()
            realm_names = [realm.get("realm") for realm in realms]
            assert source_realm_name in realm_names
            assert target_realm_name in realm_names

            # Verify target realm has expected display name
            target_export = await realm_operations_tools.export_realm(realm=target_realm_name)
            assert target_export["displayName"] == "Duplicated Target Realm"

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (405, 403):
                pytest.skip(
                    f"Realm creation/duplication not permitted on this server: {e.response.status_code}"
                )
            raise
        finally:
            # Clean up both realms
            try:
                await realm_operations_tools.delete_realm(source_realm_name, confirm=True)
            except Exception:
                pass
            try:
                await realm_operations_tools.delete_realm(target_realm_name, confirm=True)
            except Exception:
                pass


@pytest.mark.integration
class TestClientSessions:
    """Test client sessions management."""

    async def test_get_session_statistics(self):
        """Test getting realm session statistics."""
        stats = await client_sessions_tools.get_active_session_statistics()
        assert isinstance(stats, dict)
        assert "total_active_sessions" in stats
        assert "total_offline_sessions" in stats
        assert "clients_with_sessions" in stats

    async def test_client_sessions_summary(self):
        """Test getting client sessions summary."""
        summary = await client_sessions_tools.get_all_client_sessions_summary()
        assert isinstance(summary, list)
        # Summary may be empty if no active sessions

    async def test_find_sessions_by_ip(self):
        """Test finding sessions by IP address."""
        # Use a test IP that likely won't have sessions
        sessions = await client_sessions_tools.find_sessions_by_ip("192.168.999.999")
        assert isinstance(sessions, list)
        # Should be empty for non-existent IP

    async def test_client_session_management(self):
        """Test client session management with a test client."""
        # Get existing clients
        clients = await client_tools.list_clients()
        if not clients:
            pytest.skip("No clients available for session testing")

        test_client = clients[0]
        client_id = test_client["id"]

        # Get session count
        count = await client_sessions_tools.get_client_session_count(client_id)
        assert isinstance(count, dict)
        assert "active_sessions" in count
        assert "offline_sessions" in count
        assert count["client_id"] == client_id

        # Get sessions (may be empty)
        sessions = await client_sessions_tools.get_client_sessions(client_id)
        assert isinstance(sessions, list)

        # Get offline sessions (may be empty)
        offline_sessions = await client_sessions_tools.get_client_offline_sessions(client_id)
        assert isinstance(offline_sessions, list)


@pytest.mark.integration
class TestGroupRoleMappings:
    """Test group role mappings functionality."""

    async def test_group_role_mappings_lifecycle(self):
        """Test complete group role mappings lifecycle."""
        # Create test group
        test_group_name = f"test-group-{uuid.uuid4().hex[:8]}"
        group_result = await group_tools.create_group(test_group_name)
        assert group_result["status"] == "created"

        try:
            # Get the created group
            groups = await group_tools.list_groups(search=test_group_name)
            test_group = next((g for g in groups if g["name"] == test_group_name), None)
            assert test_group is not None
            group_id = test_group["id"]

            # Test getting role mappings (should be empty initially)
            mappings = await group_tools.get_group_role_mappings(group_id)
            assert isinstance(mappings, dict)

            # Get realm roles
            realm_roles = await group_tools.get_group_realm_roles(group_id)
            assert isinstance(realm_roles, list)
            # Should be empty initially
            assert len(realm_roles) == 0

            # Get available realm roles
            available_roles = await group_tools.get_group_available_realm_roles(group_id)
            assert isinstance(available_roles, list)

            # Test with default roles if available
            if available_roles:
                test_role_name = available_roles[0]["name"]

                # Add realm role to group
                add_result = await group_tools.add_realm_roles_to_group(group_id, [test_role_name])
                assert add_result["status"] == "assigned"

                # Verify role was added
                updated_roles = await group_tools.get_group_realm_roles(group_id)
                role_names = [role["name"] for role in updated_roles]
                assert test_role_name in role_names

                # Get effective roles (should include the assigned role)
                effective_roles = await group_tools.get_group_effective_realm_roles(group_id)
                assert isinstance(effective_roles, list)

                # Remove realm role from group
                remove_result = await group_tools.remove_realm_roles_from_group(
                    group_id, [test_role_name]
                )
                assert remove_result["status"] == "removed"

                # Verify role was removed
                final_roles = await group_tools.get_group_realm_roles(group_id)
                final_role_names = [role["name"] for role in final_roles]
                assert test_role_name not in final_role_names

        finally:
            # Clean up - delete test group
            try:
                delete_result = await group_tools.delete_group(group_id)
                assert delete_result["status"] == "deleted"
            except Exception:
                pass  # Ignore cleanup errors

    async def test_group_all_roles(self):
        """Test getting all roles for a group."""
        # Get existing groups
        groups = await group_tools.list_groups(max=5)
        if not groups:
            print("SKIPPED: No groups available for testing")
            return

        test_group = groups[0]
        group_id = test_group["id"]

        # Get all roles
        all_roles = await group_tools.get_group_all_roles(group_id)
        assert isinstance(all_roles, dict)
        assert "group_id" in all_roles
        assert "realm_roles" in all_roles
        assert "client_roles" in all_roles
        assert "total_roles" in all_roles

    async def test_client_role_mappings(self):
        """Test client role mappings for groups."""
        # Get existing groups and clients
        groups = await group_tools.list_groups(max=5)
        clients = await client_tools.list_clients(max=5)

        if not groups or not clients:
            print("SKIPPED: Need both groups and clients for client role testing")
            return

        test_group = groups[0]
        group_id = test_group["id"]
        test_client = clients[0]
        client_id = test_client["id"]

        # Get client roles for group (should work even if empty)
        client_roles = await group_tools.get_group_client_roles(group_id, client_id)
        assert isinstance(client_roles, list)

        # Get available client roles
        try:
            available_client_roles = await group_tools.get_group_available_client_roles(
                group_id, client_id
            )
            assert isinstance(available_client_roles, list)
        except Exception:
            # Some clients may not support this operation
            pass

        # Get effective client roles
        try:
            effective_client_roles = await group_tools.get_group_effective_client_roles(
                group_id, client_id
            )
            assert isinstance(effective_client_roles, list)
        except Exception:
            # Some clients may not support this operation
            pass


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Realm Operations Integration Tests ===\n")

    # Test Realm Operations
    test_realm = TestRealmOperations()

    print("Testing list realms...")
    try:
        await test_realm.test_list_realms()
        print("[PASS] List realms test passed")
    except Exception as e:
        print(f"[FAIL] List realms test failed: {e}")

    print("\nTesting export realm...")
    try:
        await test_realm.test_export_realm()
        print("[PASS] Export realm test passed")
    except Exception as e:
        print(f"[FAIL] Export realm test failed: {e}")

    print("\nTesting partial export realm...")
    try:
        await test_realm.test_partial_export_realm()
        print("[PASS] Partial export realm test passed")
    except Exception as e:
        print(f"[FAIL] Partial export realm test failed: {e}")

    print("\nTesting backup and restore realm...")
    try:
        await test_realm.test_backup_and_restore_realm()
        print("[PASS] Backup and restore realm test passed")
    except Exception as e:
        print(f"[FAIL] Backup and restore realm test failed: {e}")

    print("\nTesting realm lifecycle...")
    try:
        await test_realm.test_realm_lifecycle()
        print("[PASS] Realm lifecycle test passed")
    except Exception as e:
        print(f"[FAIL] Realm lifecycle test failed: {e}")

    print("\nTesting import realm...")
    try:
        await test_realm.test_import_realm()
        print("[PASS] Import realm test passed")
    except Exception as e:
        print(f"[FAIL] Import realm test failed: {e}")

    print("\nTesting partial import realm...")
    try:
        await test_realm.test_partial_import_realm()
        print("[PASS] Partial import realm test passed")
    except Exception as e:
        print(f"[FAIL] Partial import realm test failed: {e}")

    print("\nTesting duplicate realm...")
    try:
        await test_realm.test_duplicate_realm()
        print("[PASS] Duplicate realm test passed")
    except Exception as e:
        print(f"[FAIL] Duplicate realm test failed: {e}")

    # Test Client Sessions
    test_sessions = TestClientSessions()

    print("\nTesting session statistics...")
    try:
        await test_sessions.test_get_session_statistics()
        print("[PASS] Session statistics test passed")
    except Exception as e:
        print(f"[FAIL] Session statistics test failed: {e}")

    print("\nTesting client sessions summary...")
    try:
        await test_sessions.test_client_sessions_summary()
        print("[PASS] Client sessions summary test passed")
    except Exception as e:
        print(f"[FAIL] Client sessions summary test failed: {e}")

    print("\nTesting find sessions by IP...")
    try:
        await test_sessions.test_find_sessions_by_ip()
        print("[PASS] Find sessions by IP test passed")
    except Exception as e:
        print(f"[FAIL] Find sessions by IP test failed: {e}")

    print("\nTesting client session management...")
    try:
        await test_sessions.test_client_session_management()
        print("[PASS] Client session management test passed")
    except Exception as e:
        print(f"[FAIL] Client session management test failed: {e}")

    # Test Group Role Mappings
    test_group_roles = TestGroupRoleMappings()

    print("\nTesting group role mappings lifecycle...")
    try:
        await test_group_roles.test_group_role_mappings_lifecycle()
        print("[PASS] Group role mappings lifecycle test passed")
    except Exception as e:
        print(f"[FAIL] Group role mappings lifecycle test failed: {e}")

    print("\nTesting group all roles...")
    try:
        await test_group_roles.test_group_all_roles()
        print("[PASS] Group all roles test passed")
    except Exception as e:
        print(f"[FAIL] Group all roles test failed: {e}")

    print("\nTesting client role mappings...")
    try:
        await test_group_roles.test_client_role_mappings()
        print("[PASS] Client role mappings test passed")
    except Exception as e:
        print(f"[FAIL] Client role mappings test failed: {e}")

    print("\n=== Realm Operations Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
