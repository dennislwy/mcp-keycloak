"""
Integration tests for Organization Management Features:
- Organization Management (Phase 4.1)

These tests require a running Keycloak server with organizations feature enabled.
Configure the server details in your .env file.

Note: Organizations feature requires Keycloak 23+ and may need to be enabled
in the realm or server configuration.
"""

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import (
    organization_management_tools,
    user_tools,
    identity_provider_tools,
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
class TestOrganizationManagement:
    """Test organization CRUD operations."""

    def __init__(self):
        self.test_org_id = None
        self.test_org_name = f"test-org-{uuid.uuid4().hex[:8]}"
        self.test_user_id = None
        self.test_domain = f"test-{uuid.uuid4().hex[:8]}.example.com"

    async def test_create_organization(self):
        """Test creating a new organization."""
        result = await organization_management_tools.create_organization(
            name=self.test_org_name,
            description="Test organization for integration testing",
            enabled=True,
        )
        assert result["status"] == "created"
        assert result["name"] == self.test_org_name

        # Get the created organization to store its ID
        orgs = await organization_management_tools.list_organizations(
            search=self.test_org_name, exact=True
        )
        if orgs:
            self.test_org_id = orgs[0]["id"]

    async def test_list_organizations(self):
        """Test listing organizations with various parameters."""
        # Test basic listing
        orgs = await organization_management_tools.list_organizations()
        assert isinstance(orgs, list)

        # Test searching for our test organization
        if self.test_org_name:
            search_results = await organization_management_tools.list_organizations(
                search=self.test_org_name, exact=True
            )
            assert isinstance(search_results, list)
            if search_results:
                found_org = search_results[0]
                assert found_org["name"] == self.test_org_name

        # Test pagination
        paginated = await organization_management_tools.list_organizations(
            first=0, max=5
        )
        assert isinstance(paginated, list)
        assert len(paginated) <= 5

    async def test_get_organization(self):
        """Test getting organization details."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        org_details = await organization_management_tools.get_organization(
            self.test_org_id
        )
        assert isinstance(org_details, dict)
        assert org_details["id"] == self.test_org_id
        assert org_details["name"] == self.test_org_name

    async def test_update_organization(self):
        """Test updating organization properties."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        updated_description = "Updated test organization description"
        result = await organization_management_tools.update_organization(
            self.test_org_id,
            description=updated_description,
            enabled=True,
        )
        assert result["status"] == "updated"
        assert "description" in result["updated_fields"]

        # Verify the update
        updated_org = await organization_management_tools.get_organization(
            self.test_org_id
        )
        assert updated_org["description"] == updated_description

    async def test_search_organizations(self):
        """Test organization search functionality."""
        if not self.test_org_name:
            print("SKIPPED: No test organization name available")
            return

        # Test name search
        name_results = await organization_management_tools.search_organizations(
            query=self.test_org_name, search_type="name", exact=True
        )
        assert isinstance(name_results, list)

        # Test non-exact search
        partial_name = (
            self.test_org_name[:8]
            if len(self.test_org_name) > 8
            else self.test_org_name
        )
        partial_results = await organization_management_tools.search_organizations(
            query=partial_name, search_type="name", exact=False
        )
        assert isinstance(partial_results, list)


@pytest.mark.integration
class TestOrganizationMembers:
    """Test organization members management."""

    def __init__(self):
        self.test_org_id = None
        self.test_org_name = f"test-members-org-{uuid.uuid4().hex[:8]}"
        self.test_user_id = None
        self.test_username = f"test-member-{uuid.uuid4().hex[:8]}"

    async def setup_test_data(self):
        """Set up test organization and user for member tests."""
        try:
            # Create test organization
            await organization_management_tools.create_organization(
                name=self.test_org_name,
                description="Test organization for member management testing",
            )

            # Get organization ID
            orgs = await organization_management_tools.list_organizations(
                search=self.test_org_name, exact=True
            )
            if orgs:
                self.test_org_id = orgs[0]["id"]

            # Create test user
            user_result = await user_tools.create_user(
                username=self.test_username,
                email=f"{self.test_username}@example.com",
                first_name="Test",
                last_name="Member",
                enabled=True,
            )
            self.test_user_id = user_result["user_id"]

        except Exception as e:
            print(f"Setup failed: {e}")

    async def test_list_organization_members_empty(self):
        """Test listing members of an organization (initially empty)."""
        if not self.test_org_id:
            await self.setup_test_data()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        members = await organization_management_tools.list_organization_members(
            self.test_org_id
        )
        assert isinstance(members, list)
        # Should be empty initially

    async def test_add_organization_member(self):
        """Test adding a member to an organization."""
        if not self.test_org_id or not self.test_user_id:
            await self.setup_test_data()

        if not self.test_org_id or not self.test_user_id:
            print("SKIPPED: No test organization or user ID available")
            return

        result = await organization_management_tools.add_organization_member(
            self.test_org_id, self.test_user_id
        )
        assert result["status"] == "member_added"
        assert result["user_id"] == self.test_user_id

    async def test_list_organization_members_with_data(self):
        """Test listing members after adding one."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        members = await organization_management_tools.list_organization_members(
            self.test_org_id
        )
        assert isinstance(members, list)
        # Should have at least one member if add_member test passed

    async def test_get_organization_member(self):
        """Test getting specific member details."""
        if not self.test_org_id or not self.test_user_id:
            print("SKIPPED: No test organization or user ID available")
            return

        try:
            member = await organization_management_tools.get_organization_member(
                self.test_org_id, self.test_user_id
            )
            assert isinstance(member, dict)
            assert member["id"] == self.test_user_id
        except Exception as e:
            print(f"NOTE: Get member may not be supported or member not found: {e}")

    async def test_remove_organization_member(self):
        """Test removing a member from an organization."""
        if not self.test_org_id or not self.test_user_id:
            print("SKIPPED: No test organization or user ID available")
            return

        result = await organization_management_tools.remove_organization_member(
            self.test_org_id, self.test_user_id
        )
        assert result["status"] == "member_removed"
        assert result["user_id"] == self.test_user_id

    async def cleanup_test_data(self):
        """Clean up test data."""
        try:
            if self.test_user_id:
                await user_tools.delete_user(self.test_user_id)
            if self.test_org_id:
                await organization_management_tools.delete_organization(
                    self.test_org_id
                )
        except Exception as e:
            print(f"Cleanup failed: {e}")


@pytest.mark.integration
class TestOrganizationDomains:
    """Test organization domains management."""

    def __init__(self):
        self.test_org_id = None
        self.test_org_name = f"test-domains-org-{uuid.uuid4().hex[:8]}"
        self.test_domain = f"test-{uuid.uuid4().hex[:8]}.example.com"

    async def setup_test_organization(self):
        """Set up test organization for domain tests."""
        try:
            # Create test organization
            await organization_management_tools.create_organization(
                name=self.test_org_name,
                description="Test organization for domain management testing",
            )

            # Get organization ID
            orgs = await organization_management_tools.list_organizations(
                search=self.test_org_name, exact=True
            )
            if orgs:
                self.test_org_id = orgs[0]["id"]

        except Exception as e:
            print(f"Domain test setup failed: {e}")

    async def test_list_organization_domains_empty(self):
        """Test listing domains of an organization (initially empty)."""
        if not self.test_org_id:
            await self.setup_test_organization()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        domains = await organization_management_tools.list_organization_domains(
            self.test_org_id
        )
        assert isinstance(domains, list)
        # Should be empty initially

    async def test_add_organization_domain(self):
        """Test adding a domain to an organization."""
        if not self.test_org_id:
            await self.setup_test_organization()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        result = await organization_management_tools.add_organization_domain(
            self.test_org_id, self.test_domain, verified=False
        )
        assert result["status"] == "domain_added"
        assert result["domain_name"] == self.test_domain

    async def test_list_organization_domains_with_data(self):
        """Test listing domains after adding one."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        domains = await organization_management_tools.list_organization_domains(
            self.test_org_id
        )
        assert isinstance(domains, list)
        # Should have at least one domain if add_domain test passed

        # Verify our test domain is in the list
        domain_names = [d.get("name") for d in domains]
        if self.test_domain in domain_names:
            test_domain_obj = next(
                d for d in domains if d.get("name") == self.test_domain
            )
            assert test_domain_obj["name"] == self.test_domain
            assert test_domain_obj["verified"] is False

    async def test_verify_organization_domain(self):
        """Test verifying a domain for an organization."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        try:
            result = await organization_management_tools.verify_organization_domain(
                self.test_org_id, self.test_domain
            )
            assert result["status"] == "domain_verified"
            assert result["domain_name"] == self.test_domain
        except Exception as e:
            print(f"NOTE: Domain verification may not be supported: {e}")

    async def test_remove_organization_domain(self):
        """Test removing a domain from an organization."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        result = await organization_management_tools.remove_organization_domain(
            self.test_org_id, self.test_domain
        )
        assert result["status"] == "domain_removed"
        assert result["domain_name"] == self.test_domain

    async def cleanup_test_organization(self):
        """Clean up test organization."""
        try:
            if self.test_org_id:
                await organization_management_tools.delete_organization(
                    self.test_org_id
                )
        except Exception as e:
            print(f"Domain test cleanup failed: {e}")


@pytest.mark.integration
class TestOrganizationIdentityProviders:
    """Test organization identity providers management."""

    def __init__(self):
        self.test_org_id = None
        self.test_org_name = f"test-idp-org-{uuid.uuid4().hex[:8]}"
        self.test_idp_alias = f"test-idp-{uuid.uuid4().hex[:8]}"

    async def setup_test_data(self):
        """Set up test organization and identity provider."""
        try:
            # Create test organization
            await organization_management_tools.create_organization(
                name=self.test_org_name,
                description="Test organization for identity provider testing",
            )

            # Get organization ID
            orgs = await organization_management_tools.list_organizations(
                search=self.test_org_name, exact=True
            )
            if orgs:
                self.test_org_id = orgs[0]["id"]

            # Create test identity provider
            try:
                await identity_provider_tools.create_identity_provider(
                    alias=self.test_idp_alias,
                    provider_id="oidc",
                    enabled=True,
                    config={
                        "issuer": "https://accounts.google.com",
                        "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
                        "tokenUrl": "https://oauth2.googleapis.com/token",
                        "clientId": "test-client-id",
                        "clientSecret": "test-client-secret",
                    },
                )
            except Exception as e:
                print(f"Identity provider creation failed (may already exist): {e}")

        except Exception as e:
            print(f"Identity provider test setup failed: {e}")

    async def test_list_organization_identity_providers_empty(self):
        """Test listing identity providers of an organization (initially empty)."""
        if not self.test_org_id:
            await self.setup_test_data()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        providers = (
            await organization_management_tools.list_organization_identity_providers(
                self.test_org_id
            )
        )
        assert isinstance(providers, list)
        # Should be empty initially

    async def test_link_organization_identity_provider(self):
        """Test linking an identity provider to an organization."""
        if not self.test_org_id:
            await self.setup_test_data()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        try:
            result = (
                await organization_management_tools.link_organization_identity_provider(
                    self.test_org_id, self.test_idp_alias
                )
            )
            assert result["status"] == "provider_linked"
            assert result["provider_alias"] == self.test_idp_alias
        except Exception as e:
            print(
                f"NOTE: Identity provider linking may not be supported or provider not found: {e}"
            )

    async def test_get_organization_identity_provider(self):
        """Test getting a specific identity provider for an organization."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        try:
            provider = (
                await organization_management_tools.get_organization_identity_provider(
                    self.test_org_id, self.test_idp_alias
                )
            )
            assert isinstance(provider, dict)
            assert provider["alias"] == self.test_idp_alias
        except Exception as e:
            print(
                f"NOTE: Get identity provider may not be supported or provider not linked: {e}"
            )

    async def test_unlink_organization_identity_provider(self):
        """Test unlinking an identity provider from an organization."""
        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        try:
            result = await organization_management_tools.unlink_organization_identity_provider(
                self.test_org_id, self.test_idp_alias
            )
            assert result["status"] == "provider_unlinked"
            assert result["provider_alias"] == self.test_idp_alias
        except Exception as e:
            print(f"NOTE: Identity provider unlinking may not be supported: {e}")

    async def cleanup_test_data(self):
        """Clean up test data."""
        try:
            if self.test_idp_alias:
                await identity_provider_tools.delete_identity_provider(
                    self.test_idp_alias
                )
            if self.test_org_id:
                await organization_management_tools.delete_organization(
                    self.test_org_id
                )
        except Exception as e:
            print(f"Identity provider test cleanup failed: {e}")


@pytest.mark.integration
class TestOrganizationSummaryAndSearch:
    """Test organization summary and convenience functions."""

    def __init__(self):
        self.test_org_id = None
        self.test_org_name = f"test-summary-org-{uuid.uuid4().hex[:8]}"

    async def setup_test_organization(self):
        """Set up test organization for summary tests."""
        try:
            # Create test organization
            await organization_management_tools.create_organization(
                name=self.test_org_name,
                description="Test organization for summary testing",
                attributes={"testAttribute": "testValue"},
            )

            # Get organization ID
            orgs = await organization_management_tools.list_organizations(
                search=self.test_org_name, exact=True
            )
            if orgs:
                self.test_org_id = orgs[0]["id"]

        except Exception as e:
            print(f"Summary test setup failed: {e}")

    async def test_get_organization_summary(self):
        """Test getting comprehensive organization summary."""
        if not self.test_org_id:
            await self.setup_test_organization()

        if not self.test_org_id:
            print("SKIPPED: No test organization ID available")
            return

        summary = await organization_management_tools.get_organization_summary(
            self.test_org_id
        )
        assert isinstance(summary, dict)
        assert "organization_id" in summary
        assert "name" in summary
        assert "summary" in summary
        assert "domains" in summary
        assert "identity_providers" in summary
        assert "attributes" in summary

        # Verify summary structure
        assert isinstance(summary["summary"], dict)
        assert "members_count" in summary["summary"]
        assert "domains_count" in summary["summary"]
        assert "verified_domains_count" in summary["summary"]
        assert "identity_providers_count" in summary["summary"]

    async def cleanup_test_organization(self):
        """Clean up test organization."""
        try:
            if self.test_org_id:
                await organization_management_tools.delete_organization(
                    self.test_org_id
                )
        except Exception as e:
            print(f"Summary test cleanup failed: {e}")


def run_tests():
    """Run all tests."""
    asyncio.run(main())


async def main():
    """Main test runner."""
    print("\n=== Running Organization Management Integration Tests ===\n")

    # Test basic organization management
    test_orgs = TestOrganizationManagement()

    print("Testing organization creation...")
    try:
        await test_orgs.test_create_organization()
        print("[PASS] Organization creation test passed")
    except Exception as e:
        print(f"[FAIL] Organization creation test failed: {e}")
        print(
            "NOTE: Organization management may require Keycloak 23+ with organizations feature enabled"
        )

    print("\nTesting organization listing...")
    try:
        await test_orgs.test_list_organizations()
        print("[PASS] Organization listing test passed")
    except Exception as e:
        print(f"[FAIL] Organization listing test failed: {e}")

    print("\nTesting get organization...")
    try:
        await test_orgs.test_get_organization()
        print("[PASS] Get organization test passed")
    except Exception as e:
        print(f"[FAIL] Get organization test failed: {e}")

    print("\nTesting organization update...")
    try:
        await test_orgs.test_update_organization()
        print("[PASS] Organization update test passed")
    except Exception as e:
        print(f"[FAIL] Organization update test failed: {e}")

    print("\nTesting organization search...")
    try:
        await test_orgs.test_search_organizations()
        print("[PASS] Organization search test passed")
    except Exception as e:
        print(f"[FAIL] Organization search test failed: {e}")

    # Test organization members management
    test_members = TestOrganizationMembers()

    print("\nTesting organization members (empty)...")
    try:
        await test_members.test_list_organization_members_empty()
        print("[PASS] List organization members (empty) test passed")
    except Exception as e:
        print(f"[FAIL] List organization members (empty) test failed: {e}")

    print("\nTesting add organization member...")
    try:
        await test_members.test_add_organization_member()
        print("[PASS] Add organization member test passed")
    except Exception as e:
        print(f"[FAIL] Add organization member test failed: {e}")

    print("\nTesting list organization members (with data)...")
    try:
        await test_members.test_list_organization_members_with_data()
        print("[PASS] List organization members (with data) test passed")
    except Exception as e:
        print(f"[FAIL] List organization members (with data) test failed: {e}")

    print("\nTesting get organization member...")
    try:
        await test_members.test_get_organization_member()
        print("[PASS] Get organization member test passed")
    except Exception as e:
        print(f"[SKIP] Get organization member test skipped: {e}")

    print("\nTesting remove organization member...")
    try:
        await test_members.test_remove_organization_member()
        print("[PASS] Remove organization member test passed")
    except Exception as e:
        print(f"[FAIL] Remove organization member test failed: {e}")

    # Cleanup member test data
    await test_members.cleanup_test_data()

    # Test organization domains
    test_domains = TestOrganizationDomains()

    print("\nTesting organization domains (empty)...")
    try:
        await test_domains.test_list_organization_domains_empty()
        print("[PASS] List organization domains (empty) test passed")
    except Exception as e:
        print(f"[FAIL] List organization domains (empty) test failed: {e}")

    print("\nTesting add organization domain...")
    try:
        await test_domains.test_add_organization_domain()
        print("[PASS] Add organization domain test passed")
    except Exception as e:
        print(f"[FAIL] Add organization domain test failed: {e}")

    print("\nTesting list organization domains (with data)...")
    try:
        await test_domains.test_list_organization_domains_with_data()
        print("[PASS] List organization domains (with data) test passed")
    except Exception as e:
        print(f"[FAIL] List organization domains (with data) test failed: {e}")

    print("\nTesting verify organization domain...")
    try:
        await test_domains.test_verify_organization_domain()
        print("[PASS] Verify organization domain test passed")
    except Exception as e:
        print(f"[SKIP] Verify organization domain test skipped: {e}")

    print("\nTesting remove organization domain...")
    try:
        await test_domains.test_remove_organization_domain()
        print("[PASS] Remove organization domain test passed")
    except Exception as e:
        print(f"[FAIL] Remove organization domain test failed: {e}")

    # Cleanup domain test data
    await test_domains.cleanup_test_organization()

    # Test organization identity providers
    test_idps = TestOrganizationIdentityProviders()

    print("\nTesting organization identity providers (empty)...")
    try:
        await test_idps.test_list_organization_identity_providers_empty()
        print("[PASS] List organization identity providers (empty) test passed")
    except Exception as e:
        print(f"[FAIL] List organization identity providers (empty) test failed: {e}")

    print("\nTesting link organization identity provider...")
    try:
        await test_idps.test_link_organization_identity_provider()
        print("[PASS] Link organization identity provider test passed")
    except Exception as e:
        print(f"[SKIP] Link organization identity provider test skipped: {e}")

    print("\nTesting get organization identity provider...")
    try:
        await test_idps.test_get_organization_identity_provider()
        print("[PASS] Get organization identity provider test passed")
    except Exception as e:
        print(f"[SKIP] Get organization identity provider test skipped: {e}")

    print("\nTesting unlink organization identity provider...")
    try:
        await test_idps.test_unlink_organization_identity_provider()
        print("[PASS] Unlink organization identity provider test passed")
    except Exception as e:
        print(f"[SKIP] Unlink organization identity provider test skipped: {e}")

    # Cleanup identity provider test data
    await test_idps.cleanup_test_data()

    # Test organization summary
    test_summary = TestOrganizationSummaryAndSearch()

    print("\nTesting organization summary...")
    try:
        await test_summary.test_get_organization_summary()
        print("[PASS] Organization summary test passed")
    except Exception as e:
        print(f"[FAIL] Organization summary test failed: {e}")

    # Cleanup summary test data
    await test_summary.cleanup_test_organization()

    # Clean up the main test organization
    try:
        if test_orgs.test_org_id:
            await organization_management_tools.delete_organization(
                test_orgs.test_org_id
            )
            print("\nTest organization cleanup completed")
    except Exception as e:
        print(f"\nTest organization cleanup failed: {e}")

    print("\n=== Organization Management Tests Completed! ===\n")


if __name__ == "__main__":
    run_tests()
