#!/usr/bin/env python
"""
Script to create a dedicated test admin account with relaxed brute force protection.

This script:
1. Creates a new admin user for testing purposes
2. Assigns full admin roles (realm-admin and admin roles)
3. Configures relaxed brute force protection settings for the realm
4. Sets a permanent password for the test user

Usage:
    python scripts/create_test_admin.py

Environment variables required (from .env):
    SERVER_URL - Keycloak server URL
    USERNAME - Current admin username
    PASSWORD - Current admin password
    REALM_NAME - Target realm (defaults to "master")
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configuration
SERVER_URL = os.getenv("SERVER_URL")
ADMIN_USERNAME = os.getenv("USERNAME")
ADMIN_PASSWORD = os.getenv("PASSWORD")
REALM_NAME = os.getenv("REALM_NAME", "master")

# Test admin account details
TEST_ADMIN_USERNAME = "test-admin"
TEST_ADMIN_PASSWORD = "password123"
TEST_ADMIN_EMAIL = "test-admin@example.com"
TEST_ADMIN_FIRSTNAME = "Test"
TEST_ADMIN_LASTNAME = "Administrator"


class KeycloakAdminSetup:
    def __init__(self):
        self.server_url = SERVER_URL
        self.username = ADMIN_USERNAME
        self.password = ADMIN_PASSWORD
        self.realm = REALM_NAME
        self.client = httpx.AsyncClient()
        self.token = None

    async def __aenter__(self):
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def authenticate(self):
        """Authenticate with Keycloak and get access token"""
        token_url = f"{self.server_url}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.username,
            "password": self.password,
        }

        print(f"[*] Authenticating as {self.username}...")
        response = await self.client.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.token = token_data["access_token"]
        print("[+] Authentication successful")

    async def create_user(
        self, username: str, email: str, first_name: str, last_name: str, password: str
    ):
        """Create a new user in the realm"""
        url = f"{self.server_url}/admin/realms/{self.realm}/users"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        user_data = {
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }

        print(f"[*] Creating user '{username}'...")
        response = await self.client.post(url, headers=headers, json=user_data)

        if response.status_code == 201:
            # Extract user ID from Location header
            location = response.headers.get("Location", "")
            user_id = location.split("/")[-1] if location else None
            print(f"[+] User created successfully (ID: {user_id})")
            return user_id
        elif response.status_code == 409:
            print(f"[!] User '{username}' already exists, fetching existing user...")
            return await self.get_user_id(username)
        else:
            response.raise_for_status()

    async def get_user_id(self, username: str):
        """Get user ID by username"""
        url = f"{self.server_url}/admin/realms/{self.realm}/users"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"username": username, "exact": "true"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()

        users = response.json()
        if users and len(users) > 0:
            return users[0]["id"]
        return None

    async def get_realm_roles(self):
        """Get all realm-level roles"""
        url = f"{self.server_url}/admin/realms/{self.realm}/roles"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = await self.client.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    async def get_client_by_clientid(self, client_id: str):
        """Get client by clientId"""
        url = f"{self.server_url}/admin/realms/{self.realm}/clients"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"clientId": client_id}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()

        clients = response.json()
        if clients and len(clients) > 0:
            return clients[0]
        return None

    async def get_client_roles(self, client_uuid: str):
        """Get all roles for a client"""
        url = f"{self.server_url}/admin/realms/{self.realm}/clients/{client_uuid}/roles"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = await self.client.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    async def assign_realm_roles(self, user_id: str, roles: list):
        """Assign realm-level roles to a user"""
        url = f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        # Filter roles to only include id and name
        role_representations = [{"id": role["id"], "name": role["name"]} for role in roles]

        print(f"[*] Assigning {len(role_representations)} realm roles...")
        response = await self.client.post(url, headers=headers, json=role_representations)
        response.raise_for_status()
        print("[+] Realm roles assigned successfully")

    async def assign_client_roles(self, user_id: str, client_uuid: str, roles: list):
        """Assign client-specific roles to a user"""
        url = f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/clients/{client_uuid}"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        # Filter roles to only include id and name
        role_representations = [{"id": role["id"], "name": role["name"]} for role in roles]

        print(f"[*] Assigning {len(role_representations)} client roles...")
        response = await self.client.post(url, headers=headers, json=role_representations)
        response.raise_for_status()
        print("[+] Client roles assigned successfully")

    async def configure_brute_force_protection(self, enabled: bool = True, relaxed: bool = True):
        """
        Configure brute force protection settings for the realm.

        Args:
            enabled: Whether brute force protection is enabled
            relaxed: If True, use relaxed settings suitable for testing
        """
        url = f"{self.server_url}/admin/realms/{self.realm}"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        if relaxed:
            # Relaxed settings for testing - very high thresholds
            settings = {
                "bruteForceProtected": enabled,
                "permanentLockout": False,
                "maxFailureWaitSeconds": 900,  # 15 minutes wait after failures
                "minimumQuickLoginWaitSeconds": 60,  # 1 minute minimum wait
                "waitIncrementSeconds": 60,  # 1 minute increment
                "quickLoginCheckMilliSeconds": 1000,  # 1 second
                "maxDeltaTimeSeconds": 43200,  # 12 hours
                "failureFactor": 100,  # Allow 100 failures before lockout (very high for testing)
            }
            protection_type = "relaxed (100 failures allowed)" if enabled else "disabled"
        else:
            # Standard protection settings
            settings = {
                "bruteForceProtected": enabled,
                "permanentLockout": False,
                "maxFailureWaitSeconds": 900,
                "minimumQuickLoginWaitSeconds": 60,
                "waitIncrementSeconds": 60,
                "quickLoginCheckMilliSeconds": 1000,
                "maxDeltaTimeSeconds": 43200,
                "failureFactor": 30,  # Standard threshold
            }
            protection_type = "standard (30 failures allowed)" if enabled else "disabled"

        print(f"[*] Configuring brute force protection ({protection_type})...")
        response = await self.client.get(
            f"{self.server_url}/admin/realms/{self.realm}", headers=headers
        )
        response.raise_for_status()
        realm_config = response.json()

        # Update only the brute force settings
        realm_config.update(settings)

        response = await self.client.put(url, headers=headers, json=realm_config)
        response.raise_for_status()
        print("[+] Brute force protection configured successfully")

    async def clear_user_login_failures(self, user_id: str):
        """Clear any existing login failures for a user"""
        url = f"{self.server_url}/admin/realms/{self.realm}/attack-detection/brute-force/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        print("[*] Clearing login failures for user...")
        response = await self.client.delete(url, headers=headers)
        if response.status_code == 204:
            print("[+] Login failures cleared")
        else:
            print("[i] No login failures to clear")


async def setup_test_admin():
    """Main setup function"""
    print("=" * 70)
    print("Keycloak Test Admin Account Setup")
    print("=" * 70)
    print()

    async with KeycloakAdminSetup() as setup:
        # Step 1: Create test admin user
        print("Step 1: Creating test admin user")
        print("-" * 70)
        user_id = await setup.create_user(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            first_name=TEST_ADMIN_FIRSTNAME,
            last_name=TEST_ADMIN_LASTNAME,
            password=TEST_ADMIN_PASSWORD,
        )
        print()

        # Step 2: Assign admin roles
        print("Step 2: Assigning admin roles")
        print("-" * 70)

        # Get all realm roles and assign 'admin' role
        all_realm_roles = await setup.get_realm_roles()
        admin_role = next((r for r in all_realm_roles if r["name"] == "admin"), None)

        if admin_role:
            await setup.assign_realm_roles(user_id, [admin_role])
        else:
            print("[!] Warning: 'admin' realm role not found")

        # Get realm-management client and assign all its roles
        realm_mgmt_client = await setup.get_client_by_clientid("realm-management")

        if realm_mgmt_client:
            realm_mgmt_roles = await setup.get_client_roles(realm_mgmt_client["id"])
            await setup.assign_client_roles(user_id, realm_mgmt_client["id"], realm_mgmt_roles)
        else:
            print("[!] Warning: 'realm-management' client not found")

        # Get master-realm client (for master realm) and assign admin roles
        if setup.realm == "master":
            master_realm_client = await setup.get_client_by_clientid("master-realm")
            if master_realm_client:
                master_realm_roles = await setup.get_client_roles(master_realm_client["id"])
                await setup.assign_client_roles(
                    user_id, master_realm_client["id"], master_realm_roles
                )

        print()

        # Step 3: Configure brute force protection
        print("Step 3: Configuring brute force protection")
        print("-" * 70)
        await setup.configure_brute_force_protection(enabled=True, relaxed=True)
        print()

        # Step 4: Clear any existing login failures
        print("Step 4: Clearing existing login failures")
        print("-" * 70)
        await setup.clear_user_login_failures(user_id)
        print()

        # Summary
        print("=" * 70)
        print("[+] Test Admin Account Setup Complete!")
        print("=" * 70)
        print()
        print("Account Details:")
        print(f"  Username: {TEST_ADMIN_USERNAME}")
        print(f"  Password: {TEST_ADMIN_PASSWORD}")
        print(f"  Email:    {TEST_ADMIN_EMAIL}")
        print(f"  Realm:    {setup.realm}")
        print()
        print("Brute Force Protection:")
        print("  Status:           Enabled (Relaxed)")
        print("  Failure Limit:    100 attempts")
        print("  Max Wait Time:    15 minutes")
        print("  Permanent Lock:   Disabled")
        print()
        print("Next Steps:")
        print("  1. Update your .env file with the test admin credentials:")
        print(f"     USERNAME={TEST_ADMIN_USERNAME}")
        print(f"     PASSWORD={TEST_ADMIN_PASSWORD}")
        print("  2. Run your test suite without account lockout issues")
        print("  3. Consider creating separate test users for destructive tests")
        print()


if __name__ == "__main__":
    asyncio.run(setup_test_admin())
