"""Integration tests for composite roles management."""
import pytest
from src.tools import role_tools, client_tools


@pytest.fixture(scope="module")
async def composite_realm_roles_setup():
    """Set up test data for composite realm roles tests."""
    # Create base roles
    await role_tools.create_realm_role("test-role-base-1", description="Base role 1")
    await role_tools.create_realm_role("test-role-base-2", description="Base role 2")
    await role_tools.create_realm_role("test-role-base-3", description="Base role 3")

    # Create composite role
    await role_tools.create_realm_role(
        "test-composite-role", description="Composite role", composite=True
    )

    yield

    # Clean up test data
    try:
        await role_tools.delete_realm_role("test-composite-role")
    except Exception:
        pass

    for role in ["test-role-base-1", "test-role-base-2", "test-role-base-3"]:
        try:
            await role_tools.delete_realm_role(role)
        except Exception:
            pass


@pytest.mark.usefixtures("composite_realm_roles_setup")
class TestCompositeRealmRoles:
    """Test composite realm roles functionality."""

    async def test_add_realm_roles_to_composite(self):
        """Test adding realm roles to a composite role."""
        result = await role_tools.add_realm_roles_to_composite(
            "test-composite-role", ["test-role-base-1", "test-role-base-2"]
        )

        assert result["status"] == "added"
        assert "test-role-base-1" in result["message"]

    async def test_get_realm_role_composites(self):
        """Test getting composite role members."""
        composites = await role_tools.get_realm_role_composites("test-composite-role")

        assert isinstance(composites, list)
        assert len(composites) >= 2

        role_names = [r["name"] for r in composites]
        assert "test-role-base-1" in role_names
        assert "test-role-base-2" in role_names

    async def test_get_realm_role_composite_realm_roles(self):
        """Test getting only realm-level composites."""
        composites = await role_tools.get_realm_role_composite_realm_roles(
            "test-composite-role"
        )

        assert isinstance(composites, list)
        assert len(composites) >= 2

    async def test_add_more_roles_to_composite(self):
        """Test adding additional roles to composite."""
        result = await role_tools.add_realm_roles_to_composite(
            "test-composite-role", ["test-role-base-3"]
        )

        assert result["status"] == "added"

        # Verify
        composites = await role_tools.get_realm_role_composites("test-composite-role")
        role_names = [r["name"] for r in composites]
        assert "test-role-base-3" in role_names

    async def test_remove_realm_roles_from_composite(self):
        """Test removing roles from composite."""
        result = await role_tools.remove_realm_roles_from_composite(
            "test-composite-role", ["test-role-base-3"]
        )

        assert result["status"] == "removed"

        # Verify
        composites = await role_tools.get_realm_role_composites("test-composite-role")
        role_names = [r["name"] for r in composites]
        assert "test-role-base-3" not in role_names


@pytest.fixture(scope="module")
async def composite_client_roles_setup():
    """Set up test data for composite client roles tests."""
    # Create test client
    await client_tools.create_client(
        client_id="test-composite-client",
        name="Test Composite Client",
        description="Client for composite role tests",
    )

    # Get the client database ID
    clients = await client_tools.list_clients()
    test_client = next(
        (c for c in clients if c["clientId"] == "test-composite-client"), None
    )
    assert test_client is not None
    test_client_db_id = test_client["id"]

    # Create base client roles
    await role_tools.create_client_role(
        test_client_db_id, "test-client-base-1", description="Client base role 1"
    )
    await role_tools.create_client_role(
        test_client_db_id, "test-client-base-2", description="Client base role 2"
    )

    # Create composite client role
    await role_tools.create_client_role(
        test_client_db_id,
        "test-client-composite",
        description="Composite client role",
        composite=True,
    )

    # Create a realm role for mixed composite
    await role_tools.create_realm_role(
        "test-realm-for-client-composite", description="Realm role for client composite"
    )

    yield test_client_db_id

    # Clean up test data
    try:
        await client_tools.delete_client(test_client_db_id)
    except Exception:
        pass

    try:
        await role_tools.delete_realm_role("test-realm-for-client-composite")
    except Exception:
        pass


@pytest.mark.usefixtures("composite_client_roles_setup")
class TestCompositeClientRoles:
    """Test composite client roles functionality."""

    async def test_add_client_roles_to_client_composite(self, composite_client_roles_setup):
        """Test adding client roles to a client composite role."""
        test_client_db_id = composite_client_roles_setup

        result = await role_tools.add_roles_to_client_role_composite(
            test_client_db_id,
            "test-client-composite",
            client_role_names=["test-client-base-1"],
            source_client_id=test_client_db_id,
        )

        assert result["status"] == "added"

    async def test_add_realm_role_to_client_composite(self, composite_client_roles_setup):
        """Test adding realm role to a client composite role."""
        test_client_db_id = composite_client_roles_setup

        result = await role_tools.add_roles_to_client_role_composite(
            test_client_db_id,
            "test-client-composite",
            realm_role_names=["test-realm-for-client-composite"],
        )

        assert result["status"] == "added"

    async def test_get_client_role_composites(self, composite_client_roles_setup):
        """Test getting client role composites."""
        test_client_db_id = composite_client_roles_setup

        composites = await role_tools.get_client_role_composites(
            test_client_db_id, "test-client-composite"
        )

        assert isinstance(composites, list)
        assert len(composites) >= 2

        role_names = [r["name"] for r in composites]
        assert "test-client-base-1" in role_names
        assert "test-realm-for-client-composite" in role_names

    async def test_remove_roles_from_client_composite(self, composite_client_roles_setup):
        """Test removing roles from client composite."""
        test_client_db_id = composite_client_roles_setup

        result = await role_tools.remove_roles_from_client_role_composite(
            test_client_db_id,
            "test-client-composite",
            client_role_names=["test-client-base-1"],
            source_client_id=test_client_db_id,
        )

        assert result["status"] == "removed"

        # Verify
        composites = await role_tools.get_client_role_composites(
            test_client_db_id, "test-client-composite"
        )
        role_names = [r["name"] for r in composites]
        assert "test-client-base-1" not in role_names


@pytest.fixture(scope="module")
async def mixed_composite_setup():
    """Set up test data for mixed composite roles tests."""
    # Create test client
    await client_tools.create_client(
        client_id="test-mixed-composite-client",
        name="Test Mixed Composite Client",
    )

    clients = await client_tools.list_clients()
    test_client = next(
        (c for c in clients if c["clientId"] == "test-mixed-composite-client"), None
    )
    assert test_client is not None
    test_client_db_id = test_client["id"]

    # Create base roles
    await role_tools.create_realm_role("test-realm-base", description="Realm base")
    await role_tools.create_client_role(
        test_client_db_id, "test-client-base", description="Client base"
    )

    # Create composite realm role
    await role_tools.create_realm_role(
        "test-mixed-composite", description="Mixed composite", composite=True
    )

    yield test_client_db_id

    # Clean up test data
    try:
        await role_tools.delete_realm_role("test-mixed-composite")
    except Exception:
        pass

    try:
        await role_tools.delete_realm_role("test-realm-base")
    except Exception:
        pass

    try:
        await client_tools.delete_client(test_client_db_id)
    except Exception:
        pass


@pytest.mark.usefixtures("mixed_composite_setup")
class TestCompositeRolesWithRealmRoles:
    """Test mixing realm and client roles in composites."""

    async def test_add_client_roles_to_realm_composite(self, mixed_composite_setup):
        """Test adding client roles to a realm composite role."""
        test_client_db_id = mixed_composite_setup

        result = await role_tools.add_client_roles_to_realm_composite(
            "test-mixed-composite",
            test_client_db_id,
            ["test-client-base"],
        )

        assert result["status"] == "added"

    async def test_add_realm_role_to_realm_composite(self, mixed_composite_setup):
        """Test adding realm role to realm composite."""
        result = await role_tools.add_realm_roles_to_composite(
            "test-mixed-composite", ["test-realm-base"]
        )

        assert result["status"] == "added"

    async def test_get_all_composites(self, mixed_composite_setup):
        """Test getting all composites (realm and client)."""
        composites = await role_tools.get_realm_role_composites("test-mixed-composite")

        assert isinstance(composites, list)
        assert len(composites) >= 2

        role_names = [r["name"] for r in composites]
        assert "test-realm-base" in role_names
        assert "test-client-base" in role_names

    async def test_get_composite_client_roles_only(self, mixed_composite_setup):
        """Test getting only client composites for a realm role."""
        test_client_db_id = mixed_composite_setup

        composites = await role_tools.get_realm_role_composite_client_roles(
            "test-mixed-composite", test_client_db_id
        )

        assert isinstance(composites, list)
        role_names = [r["name"] for r in composites]
        assert "test-client-base" in role_names

    async def test_get_composite_realm_roles_only(self, mixed_composite_setup):
        """Test getting only realm composites for a realm role."""
        composites = await role_tools.get_realm_role_composite_realm_roles(
            "test-mixed-composite"
        )

        assert isinstance(composites, list)
        role_names = [r["name"] for r in composites]
        assert "test-realm-base" in role_names
