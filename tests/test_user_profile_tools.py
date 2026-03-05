"""
Integration tests for User Profile Management tools.

Covers:
- get_user_profile
- update_user_profile
- get_user_profile_metadata
"""

import pytest
from src.tools.user_profile_tools import (
    get_user_profile,
    update_user_profile,
    get_user_profile_metadata,
)


# ---------------------------------------------------------------------------
# get_user_profile tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGetUserProfile:
    """Tests for get_user_profile — GET /users/profile."""

    async def test_returns_dict(self):
        """Should return a non-empty dict."""
        result = await get_user_profile()
        assert isinstance(result, dict)
        assert len(result) > 0

    async def test_contains_attributes_key(self):
        """UPConfig must include an 'attributes' list."""
        result = await get_user_profile()
        assert "attributes" in result
        assert isinstance(result["attributes"], list)

    async def test_attributes_have_name(self):
        """Each attribute definition must include a 'name' field."""
        result = await get_user_profile()
        for attr in result["attributes"]:
            assert "name" in attr, f"Attribute missing 'name': {attr}"

    async def test_contains_groups_key(self):
        """UPConfig must include a 'groups' key (list, possibly empty)."""
        result = await get_user_profile()
        assert "groups" in result
        assert isinstance(result["groups"], list)

    async def test_unmanaged_attribute_policy_valid(self):
        """unmanagedAttributePolicy should be one of the known values if present."""
        result = await get_user_profile()
        if "unmanagedAttributePolicy" in result:
            valid = {"DISABLED", "ENABLED", "ADMIN_VIEW", "ADMIN_EDIT"}
            assert result["unmanagedAttributePolicy"] in valid, (
                f"Unexpected unmanagedAttributePolicy: {result['unmanagedAttributePolicy']}"
            )

    async def test_realm_parameter(self):
        """Explicit realm=None should return the same result as default."""
        result_default = await get_user_profile()
        result_explicit = await get_user_profile(realm=None)
        assert result_default == result_explicit


# ---------------------------------------------------------------------------
# update_user_profile tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestUpdateUserProfile:
    """Tests for update_user_profile — PUT /users/profile."""

    async def test_update_returns_status(self):
        """update_user_profile should return a status dict."""
        # Fetch current profile and write it back unchanged (no-op update)
        current = await get_user_profile()
        result = await update_user_profile(current)
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "updated"

    async def test_update_is_idempotent(self):
        """Applying the same config twice should leave the profile unchanged."""
        original = await get_user_profile()

        await update_user_profile(original)
        after_first = await get_user_profile()

        await update_user_profile(original)
        after_second = await get_user_profile()

        assert after_first == after_second

    async def test_update_unmanaged_attribute_policy(self):
        """Changing unmanagedAttributePolicy should persist and be retrievable."""
        original = await get_user_profile()
        original_policy = original.get("unmanagedAttributePolicy")

        # Pick a value different from the current one
        new_policy = "ADMIN_VIEW" if original_policy != "ADMIN_VIEW" else "ENABLED"

        try:
            await update_user_profile({"unmanagedAttributePolicy": new_policy})
            updated = await get_user_profile()
            assert updated.get("unmanagedAttributePolicy") == new_policy
        finally:
            # Restore by putting back the full original profile so no key mismatch
            await update_user_profile(original)
            restored = await get_user_profile()
            assert restored.get("unmanagedAttributePolicy") == original_policy

    async def test_realm_parameter(self):
        """Explicit realm=None should work identically to the default."""
        current = await get_user_profile()
        result = await update_user_profile(current, realm=None)
        assert result["status"] == "updated"


# ---------------------------------------------------------------------------
# get_user_profile_metadata tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGetUserProfileMetadata:
    """Tests for get_user_profile_metadata — GET /users/profile/metadata."""

    async def test_returns_dict(self):
        """Should return a non-empty dict."""
        result = await get_user_profile_metadata()
        assert isinstance(result, dict)
        assert len(result) > 0

    async def test_contains_attributes(self):
        """Metadata should include an 'attributes' list."""
        result = await get_user_profile_metadata()
        assert "attributes" in result
        assert isinstance(result["attributes"], list)

    async def test_attributes_have_required_fields(self):
        """Each attribute metadata entry should have at minimum a 'name'."""
        result = await get_user_profile_metadata()
        for attr in result["attributes"]:
            assert "name" in attr, f"Attribute metadata missing 'name': {attr}"

    async def test_metadata_attributes_match_profile(self):
        """Attribute names in metadata should be a subset of those in UPConfig."""
        profile = await get_user_profile()
        metadata = await get_user_profile_metadata()

        profile_names = {a["name"] for a in profile.get("attributes", [])}
        metadata_names = {a["name"] for a in metadata.get("attributes", [])}

        # All metadata attribute names must exist in the full profile
        assert metadata_names.issubset(profile_names), (
            f"Metadata contains unknown attributes: {metadata_names - profile_names}"
        )

    async def test_realm_parameter(self):
        """Explicit realm=None should return the same result as default."""
        result_default = await get_user_profile_metadata()
        result_explicit = await get_user_profile_metadata(realm=None)
        assert result_default == result_explicit
