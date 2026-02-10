"""Cleanup leftover test artifacts."""
import asyncio
from src.tools import organization_management_tools, user_tools


async def cleanup_artifacts():
    """Delete all test organizations and users."""
    print("\n=== Cleaning Up Test Artifacts ===\n")

    # Clean up test organizations
    orgs = await organization_management_tools.list_organizations()
    test_orgs = [o for o in orgs if 'test-' in o.get('name', '').lower()]

    print(f"Found {len(test_orgs)} test organizations to delete")
    for org in test_orgs:
        try:
            print(f"  Deleting organization: {org['name']}")
            await organization_management_tools.delete_organization(org['id'])
            print(f"    [OK] Deleted")
        except Exception as e:
            print(f"    [ERROR] {e}")

    # Clean up test users (but keep test-admin)
    users = await user_tools.list_users()
    test_users = [
        u for u in users
        if 'test-' in u.get('username', '').lower() and u.get('username') != 'test-admin'
    ]

    print(f"\nFound {len(test_users)} test users to delete (excluding test-admin)")
    for user in test_users:
        try:
            print(f"  Deleting user: {user['username']}")
            await user_tools.delete_user(user['id'])
            print(f"    [OK] Deleted")
        except Exception as e:
            print(f"    [ERROR] {e}")

    print("\n[*] Cleanup complete!\n")


if __name__ == "__main__":
    asyncio.run(cleanup_artifacts())
