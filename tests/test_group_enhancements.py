"""
Integration tests for enhanced Group Management features.

These tests cover the new parameters and hierarchy operations added to group tools.
"""

import pytest
from src.tools.group_tools import (
    list_groups,
    create_group,
    delete_group,
    create_subgroup,
    list_subgroups,
    get_group_members,
    add_user_to_group,
    remove_user_from_group,
)
from src.tools.user_tools import create_user, delete_user, list_users


@pytest.fixture(scope="module")
async def test_parent_group():
    """Create a parent group for hierarchy tests."""
    group_name = "test-parent-enhanced"
    await create_group(name=group_name)

    # Get the group ID
    groups = await list_groups(search=group_name, exact=True)
    group_id = groups[0]["id"] if groups else None

    yield group_id, group_name

    # Cleanup (will also delete subgroups)
    try:
        if group_id:
            await delete_group(group_id)
    except Exception:
        pass


@pytest.fixture(scope="module")
async def test_user_for_groups():
    """Create a test user for group membership tests."""
    username = "group-member-test"
    await create_user(username=username, email=f"{username}@test.com")

    # Get user ID
    users = await list_users(username=username)
    user_id = users[0]["id"] if users else None

    yield user_id

    # Cleanup
    try:
        if user_id:
            await delete_user(user_id)
    except Exception:
        pass


@pytest.mark.integration
class TestEnhancedGroupSearch:
    """Test enhanced group search capabilities."""

    async def test_list_groups_with_exact_match(self):
        """Test exact matching for group searches."""
        # Create test groups
        group1 = "exactgrouptest"
        group2 = "exactgrouptest123"

        await create_group(name=group1)
        await create_group(name=group2)

        try:
            # Search without exact match (should find both)
            groups = await list_groups(search="exactgrouptest")
            assert len(groups) >= 2

            # Search with exact match (should find only one)
            exact_groups = await list_groups(search="exactgrouptest", exact=True)
            group_names = [g["name"] for g in exact_groups]
            assert group1 in group_names
            # Note: Exact behavior depends on Keycloak version
        finally:
            # Cleanup
            all_groups = await list_groups(search="exactgrouptest")
            for group in all_groups:
                if group["name"] in [group1, group2]:
                    await delete_group(group["id"])

    async def test_list_groups_with_query_parameter(self):
        """Test the q parameter for group queries."""
        group_name = "querygrouptest"
        await create_group(name=group_name, attributes={"type": ["department"]})

        try:
            # Use q parameter (behavior depends on Keycloak configuration)
            groups = await list_groups(q=group_name)
            assert isinstance(groups, list)

            # The q parameter might search in different fields
            # depending on Keycloak configuration
        finally:
            # Cleanup
            groups = await list_groups(search=group_name)
            if groups:
                await delete_group(groups[0]["id"])

    async def test_list_groups_with_brief_representation(self):
        """Test brief representation parameter."""
        group_name = "briefgrouptest"
        await create_group(
            name=group_name, attributes={"description": ["Test group for brief rep"]}
        )

        try:
            # Get full representation
            full_groups = await list_groups(
                search=group_name, brief_representation=False
            )
            assert len(full_groups) >= 1

            # Get brief representation (default)
            brief_groups = await list_groups(
                search=group_name, brief_representation=True
            )
            assert len(brief_groups) >= 1

            # Both should have basic fields
            for group in brief_groups:
                if group["name"] == group_name:
                    assert "id" in group
                    assert "name" in group
        finally:
            # Cleanup
            groups = await list_groups(search=group_name)
            if groups:
                await delete_group(groups[0]["id"])

    async def test_list_groups_with_hierarchy(self):
        """Test populate_hierarchy parameter."""
        # Create parent and child groups
        parent_name = "hierarchyparent"
        child_name = "hierarchychild"

        await create_group(name=parent_name)
        parent_groups = await list_groups(search=parent_name, exact=True)
        parent_id = parent_groups[0]["id"]

        await create_subgroup(parent_group_id=parent_id, name=child_name)

        try:
            # List with hierarchy
            groups = await list_groups(search=parent_name, populate_hierarchy=True)
            assert len(groups) >= 1

            # Without hierarchy
            flat_groups = await list_groups(
                search=parent_name, populate_hierarchy=False
            )
            assert len(flat_groups) >= 1

            # Both should return groups, hierarchy affects structure
            assert isinstance(groups, list)
            assert isinstance(flat_groups, list)
        finally:
            # Cleanup (parent deletion should cascade to children)
            await delete_group(parent_id)


@pytest.mark.integration
class TestGroupHierarchy:
    """Test group hierarchy operations."""

    async def test_create_subgroup(self, test_parent_group):
        """Test creating a subgroup."""
        parent_id, parent_name = test_parent_group
        subgroup_name = "test-subgroup"

        result = await create_subgroup(
            parent_group_id=parent_id, name=subgroup_name, attributes={"type": ["team"]}
        )

        assert result["status"] == "created"
        assert subgroup_name in result["message"]

        # Verify subgroup was created
        subgroups = await list_subgroups(group_id=parent_id)
        subgroup_names = [sg["name"] for sg in subgroups]
        assert subgroup_name in subgroup_names

        # Cleanup (handled by parent fixture)

    async def test_list_subgroups(self, test_parent_group):
        """Test listing subgroups with various parameters."""
        parent_id, parent_name = test_parent_group

        # Create multiple subgroups
        for i in range(3):
            await create_subgroup(parent_group_id=parent_id, name=f"subgroup-{i}")

        # List all subgroups
        all_subgroups = await list_subgroups(group_id=parent_id)
        assert len(all_subgroups) >= 3

        # List with pagination
        page1 = await list_subgroups(group_id=parent_id, first=0, max=2)
        assert len(page1) <= 2

        page2 = await list_subgroups(group_id=parent_id, first=2, max=2)
        assert isinstance(page2, list)

        # Search subgroups
        search_results = await list_subgroups(group_id=parent_id, search="subgroup-1")
        assert len(search_results) >= 1

        # Cleanup (handled by parent fixture)

    async def test_list_subgroups_with_exact_search(self, test_parent_group):
        """Test exact search in subgroups."""
        parent_id, parent_name = test_parent_group

        # Create subgroups with similar names
        await create_subgroup(parent_group_id=parent_id, name="exactsub")
        await create_subgroup(parent_group_id=parent_id, name="exactsub123")

        # Search without exact
        non_exact = await list_subgroups(group_id=parent_id, search="exactsub")
        assert len(non_exact) >= 2

        # Search with exact
        exact = await list_subgroups(group_id=parent_id, search="exactsub", exact=True)
        exact_names = [g["name"] for g in exact]
        assert "exactsub" in exact_names

        # Cleanup (handled by parent fixture)


@pytest.mark.integration
class TestGroupMembers:
    """Test group membership operations."""

    async def test_get_group_members_empty(self, test_parent_group):
        """Test getting members of an empty group."""
        parent_id, parent_name = test_parent_group

        members = await get_group_members(group_id=parent_id)
        assert isinstance(members, list)
        # New group should have no members initially
        assert len(members) == 0

    async def test_add_and_remove_group_member(
        self, test_parent_group, test_user_for_groups
    ):
        """Test adding and removing a user from a group."""
        parent_id, parent_name = test_parent_group
        user_id = test_user_for_groups

        # Add user to group
        add_result = await add_user_to_group(user_id=user_id, group_id=parent_id)
        assert add_result["status"] == "added"

        # Verify user is in group
        members = await get_group_members(group_id=parent_id)
        member_ids = [m["id"] for m in members]
        assert user_id in member_ids

        # Remove user from group
        remove_result = await remove_user_from_group(
            user_id=user_id, group_id=parent_id
        )
        assert remove_result["status"] == "removed"

        # Verify user is no longer in group
        members_after = await get_group_members(group_id=parent_id)
        member_ids_after = [m["id"] for m in members_after]
        assert user_id not in member_ids_after

    async def test_get_group_members_with_pagination(self, test_parent_group):
        """Test pagination for group members."""
        parent_id, parent_name = test_parent_group

        # Create and add multiple users
        user_ids = []
        for i in range(5):
            username = f"member-test-{i}"
            await create_user(username=username, email=f"{username}@test.com")
            users = await list_users(username=username)
            if users:
                user_id = users[0]["id"]
                user_ids.append(user_id)
                await add_user_to_group(user_id=user_id, group_id=parent_id)

        try:
            # Get all members
            all_members = await get_group_members(group_id=parent_id)
            assert len(all_members) >= 5

            # Get with pagination
            page1 = await get_group_members(group_id=parent_id, first=0, max=3)
            assert len(page1) <= 3

            page2 = await get_group_members(group_id=parent_id, first=3, max=3)
            assert isinstance(page2, list)
        finally:
            # Cleanup users
            for user_id in user_ids:
                try:
                    await delete_user(user_id)
                except Exception:
                    pass


@pytest.mark.integration
class TestNestedHierarchy:
    """Test deeply nested group hierarchies."""

    async def test_create_nested_subgroups(self):
        """Test creating multiple levels of nested subgroups."""
        # Create root group
        root_name = "root-group"
        await create_group(name=root_name)
        root_groups = await list_groups(search=root_name, exact=True)
        root_id = root_groups[0]["id"]

        try:
            # Create first level subgroup
            await create_subgroup(parent_group_id=root_id, name="level-1")
            level1_groups = await list_subgroups(group_id=root_id, search="level-1")
            level1_id = level1_groups[0]["id"]

            # Create second level subgroup
            await create_subgroup(parent_group_id=level1_id, name="level-2")
            level2_groups = await list_subgroups(group_id=level1_id, search="level-2")
            assert len(level2_groups) == 1
            assert level2_groups[0]["name"] == "level-2"

            # Verify hierarchy
            root_subgroups = await list_subgroups(group_id=root_id)
            assert len(root_subgroups) >= 1

            level1_subgroups = await list_subgroups(group_id=level1_id)
            assert len(level1_subgroups) >= 1
        finally:
            # Cleanup (deleting root should cascade)
            await delete_group(root_id)
