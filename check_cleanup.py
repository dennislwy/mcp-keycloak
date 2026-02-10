"""Check for remaining test artifacts after test run."""
import asyncio
from src.tools import organization_management_tools, user_tools


async def check_cleanup():
    """Check for leftover test organizations and users."""
    print("\n=== Checking for Test Artifacts ===\n")

    # Check organizations
    orgs = await organization_management_tools.list_organizations()
    test_orgs = [o for o in orgs if 'test-' in o.get('name', '').lower()]

    print(f"Total organizations: {len(orgs)}")
    print(f"Test organizations remaining: {len(test_orgs)}")

    if test_orgs:
        print("\nTest organizations found:")
        for org in test_orgs:
            print(f"  - {org['name']} (ID: {org['id']})")
    else:
        print("[OK] No test organizations remaining (cleanup successful!)")

    # Check users
    users = await user_tools.list_users()
    test_users = [u for u in users if 'test-' in u.get('username', '').lower()]

    print(f"\nTotal users: {len(users)}")
    print(f"Test users remaining: {len(test_users)}")

    if test_users:
        print("\nTest users found:")
        for user in test_users:
            print(f"  - {user['username']} (ID: {user['id']})")
    else:
        print("[OK] No test users remaining (cleanup successful!)")

    print("\n" + "="*40 + "\n")

    if not test_orgs and not test_users:
        print("[OK] All test artifacts cleaned up successfully!")
        return True
    else:
        print("[WARNING] Some test artifacts were not cleaned up")
        return False


if __name__ == "__main__":
    asyncio.run(check_cleanup())
