"""Integration tests for user credentials and consents management."""
import pytest
from src.tools import user_tools, user_credentials_tools, client_tools


@pytest.fixture(scope="module")
async def credentials_test_user():
    """Set up test user for credentials tests."""
    test_username = "test-creds-user"

    # Create test user with password
    await user_tools.create_user(
        username=test_username,
        email="test-creds@example.com",
        first_name="Test",
        last_name="Credentials",
        enabled=True,
        temporary_password="TestPass123!",
    )

    # Find the created user
    users = await user_tools.list_users(search=test_username)
    test_user = next((u for u in users if u["username"] == test_username), None)
    assert test_user is not None
    test_user_id = test_user["id"]

    yield test_user_id

    # Clean up
    try:
        await user_tools.delete_user(test_user_id)
    except Exception:
        pass


@pytest.mark.usefixtures("credentials_test_user")
class TestUserCredentialsManagement:
    """Test user credentials management functionality."""

    async def test_list_user_credentials(self, credentials_test_user):
        """Test listing user credentials."""
        credentials = await user_credentials_tools.list_user_credentials(
            credentials_test_user
        )

        assert isinstance(credentials, list)
        # User should have at least a password credential
        assert len(credentials) > 0

        # Check credential structure
        cred = credentials[0]
        assert "id" in cred
        assert "type" in cred

    async def test_update_credential_label(self, credentials_test_user):
        """Test updating credential label."""
        # Get credentials
        credentials = await user_credentials_tools.list_user_credentials(
            credentials_test_user
        )
        assert len(credentials) > 0

        credential_id = credentials[0]["id"]

        # Update label
        result = await user_credentials_tools.update_credential_label(
            credentials_test_user, credential_id, "My Password"
        )

        assert result["status"] == "updated"
        assert "My Password" in result["message"]

    async def test_move_credential_to_first(self, credentials_test_user):
        """Test moving credential to first position."""
        # Get credentials
        credentials = await user_credentials_tools.list_user_credentials(
            credentials_test_user
        )

        if len(credentials) > 0:
            credential_id = credentials[0]["id"]

            # Move to first (should succeed even if already first)
            result = await user_credentials_tools.move_credential_to_first(
                credentials_test_user, credential_id
            )

            assert result["status"] == "updated"


@pytest.fixture(scope="module")
async def actions_test_user():
    """Set up test user for required actions tests."""
    test_username = "test-actions-user"

    # Create test user
    await user_tools.create_user(
        username=test_username,
        email="test-actions@example.com",
        enabled=True,
    )

    # Find the created user
    users = await user_tools.list_users(search=test_username)
    test_user = next((u for u in users if u["username"] == test_username), None)
    assert test_user is not None
    test_user_id = test_user["id"]

    yield test_user_id

    # Clean up
    try:
        await user_tools.delete_user(test_user_id)
    except Exception:
        pass


@pytest.mark.usefixtures("actions_test_user")
class TestUserRequiredActions:
    """Test user required actions management."""

    async def test_get_user_required_actions(self, actions_test_user):
        """Test getting required actions."""
        actions = await user_credentials_tools.get_user_required_actions(
            actions_test_user
        )

        assert isinstance(actions, list)

    async def test_add_user_required_action(self, actions_test_user):
        """Test adding a required action."""
        result = await user_credentials_tools.add_user_required_action(
            actions_test_user, "UPDATE_PASSWORD"
        )

        assert result["status"] in ["added", "skipped"]

        # Verify
        actions = await user_credentials_tools.get_user_required_actions(
            actions_test_user
        )
        assert "UPDATE_PASSWORD" in actions

    async def test_add_multiple_required_actions(self, actions_test_user):
        """Test adding multiple required actions."""
        result = await user_credentials_tools.add_user_required_action(
            actions_test_user, "VERIFY_EMAIL"
        )

        assert result["status"] in ["added", "skipped"]

        # Verify both actions
        actions = await user_credentials_tools.get_user_required_actions(
            actions_test_user
        )
        assert "UPDATE_PASSWORD" in actions
        assert "VERIFY_EMAIL" in actions

    async def test_set_user_required_actions(self, actions_test_user):
        """Test setting required actions (replace all)."""
        result = await user_credentials_tools.set_user_required_actions(
            actions_test_user, ["UPDATE_PROFILE"]
        )

        assert result["status"] == "updated"

        # Verify
        actions = await user_credentials_tools.get_user_required_actions(
            actions_test_user
        )
        assert actions == ["UPDATE_PROFILE"]

    async def test_remove_user_required_action(self, actions_test_user):
        """Test removing a required action."""
        result = await user_credentials_tools.remove_user_required_action(
            actions_test_user, "UPDATE_PROFILE"
        )

        assert result["status"] == "removed"

        # Verify
        actions = await user_credentials_tools.get_user_required_actions(
            actions_test_user
        )
        assert "UPDATE_PROFILE" not in actions


@pytest.fixture(scope="module")
async def consents_test_setup():
    """Set up test user and client for consents tests."""
    test_username = "test-consents-user"

    # Check if user already exists, if not create it
    users = await user_tools.list_users(search=test_username)
    test_user = next((u for u in users if u["username"] == test_username), None)

    if not test_user:
        # Create test user
        await user_tools.create_user(
            username=test_username,
            email="test-consents@example.com",
            enabled=True,
            temporary_password="TestPass123!",
        )

        # Find the created user
        users = await user_tools.list_users(search=test_username)
        test_user = next((u for u in users if u["username"] == test_username), None)

    assert test_user is not None
    test_user_id = test_user["id"]

    # Check if client already exists, if not create it
    clients = await client_tools.list_clients()
    test_client = next(
        (c for c in clients if c["clientId"] == "test-consent-client"), None
    )

    if not test_client:
        # Create test client for consent
        await client_tools.create_client(
            client_id="test-consent-client",
            name="Test Consent Client",
            enabled=True,
        )

        # Get client database ID
        clients = await client_tools.list_clients()
        test_client = next(
            (c for c in clients if c["clientId"] == "test-consent-client"), None
        )

    assert test_client is not None
    test_client_db_id = test_client["id"]

    yield {"user_id": test_user_id, "client_db_id": test_client_db_id}

    # Clean up
    try:
        await user_tools.delete_user(test_user_id)
    except Exception:
        pass

    try:
        await client_tools.delete_client(test_client_db_id)
    except Exception:
        pass


@pytest.mark.usefixtures("consents_test_setup")
class TestUserConsents:
    """Test user consents management."""

    async def test_list_user_consents(self, consents_test_setup):
        """Test listing user consents."""
        user_id = consents_test_setup["user_id"]
        consents = await user_credentials_tools.list_user_consents(user_id)

        assert isinstance(consents, list)
        # May be empty if no consents granted yet


@pytest.fixture(scope="module")
async def offline_sessions_test_setup():
    """Set up test user and client for offline sessions tests."""
    test_username = "test-offline-user"

    # Create test user
    await user_tools.create_user(
        username=test_username,
        email="test-offline@example.com",
        enabled=True,
    )

    # Find the created user
    users = await user_tools.list_users(search=test_username)
    test_user = next((u for u in users if u["username"] == test_username), None)
    assert test_user is not None
    test_user_id = test_user["id"]

    # Create test client
    await client_tools.create_client(
        client_id="test-offline-client",
        name="Test Offline Client",
    )

    clients = await client_tools.list_clients()
    test_client = next(
        (c for c in clients if c["clientId"] == "test-offline-client"), None
    )
    assert test_client is not None
    test_client_db_id = test_client["id"]

    yield {"user_id": test_user_id, "client_db_id": test_client_db_id}

    # Clean up
    try:
        await user_tools.delete_user(test_user_id)
    except Exception:
        pass

    try:
        await client_tools.delete_client(test_client_db_id)
    except Exception:
        pass


@pytest.mark.usefixtures("offline_sessions_test_setup")
class TestUserOfflineSessions:
    """Test user offline sessions management."""

    async def test_list_user_offline_sessions(self, offline_sessions_test_setup):
        """Test listing user offline sessions."""
        user_id = offline_sessions_test_setup["user_id"]
        client_db_id = offline_sessions_test_setup["client_db_id"]

        sessions = await user_credentials_tools.list_user_offline_sessions(
            user_id, client_db_id
        )

        assert isinstance(sessions, list)
        # Will be empty unless user has active offline sessions


@pytest.fixture(scope="module")
async def bulk_operations_test_setup():
    """Set up multiple test users for bulk operations tests."""
    test_usernames = [
        "test-bulk-user-1",
        "test-bulk-user-2",
        "test-bulk-user-3",
    ]

    test_user_ids = []

    # Create multiple test users
    for username in test_usernames:
        await user_tools.create_user(
            username=username,
            email=f"{username}@example.com",
            enabled=True,
        )

        # Find the created user
        users = await user_tools.list_users(search=username)
        test_user = next((u for u in users if u["username"] == username), None)
        if test_user:
            test_user_ids.append(test_user["id"])

    yield test_user_ids

    # Clean up
    for user_id in test_user_ids:
        try:
            await user_tools.delete_user(user_id)
        except Exception:
            pass


@pytest.mark.usefixtures("bulk_operations_test_setup")
class TestBulkUserOperations:
    """Test bulk user operations."""

    async def test_bulk_reset_user_passwords(self, bulk_operations_test_setup):
        """Test bulk password reset."""
        test_user_ids = bulk_operations_test_setup

        result = await user_credentials_tools.bulk_reset_user_passwords(
            test_user_ids, "NewBulkPass123!", temporary=True
        )

        assert result["status"] == "completed"
        assert result["total"] == len(test_user_ids)
        assert result["successes"] == len(test_user_ids)
        assert result["failures"] == 0

    async def test_bulk_update_user_attributes(self, bulk_operations_test_setup):
        """Test bulk attribute update."""
        test_user_ids = bulk_operations_test_setup
        attributes = {"department": ["Engineering"], "team": ["Platform"]}

        result = await user_credentials_tools.bulk_update_user_attributes(
            test_user_ids, attributes, merge=True
        )

        assert result["status"] == "completed"
        assert result["total"] == len(test_user_ids)
        assert result["successes"] == len(test_user_ids)
        assert result["failures"] == 0

    async def test_bulk_add_required_actions(self, bulk_operations_test_setup):
        """Test bulk required actions addition."""
        test_user_ids = bulk_operations_test_setup

        result = await user_credentials_tools.bulk_add_required_actions(
            test_user_ids, ["UPDATE_PASSWORD", "VERIFY_EMAIL"]
        )

        assert result["status"] == "completed"
        assert result["total"] == len(test_user_ids)
        assert result["successes"] == len(test_user_ids)

        # Verify actions were added
        actions = await user_credentials_tools.get_user_required_actions(
            test_user_ids[0]
        )
        assert "UPDATE_PASSWORD" in actions
        assert "VERIFY_EMAIL" in actions

    async def test_bulk_update_with_merge_false(self, bulk_operations_test_setup):
        """Test bulk attribute update with merge=False."""
        test_user_ids = bulk_operations_test_setup
        new_attributes = {"location": ["Remote"]}

        result = await user_credentials_tools.bulk_update_user_attributes(
            test_user_ids, new_attributes, merge=False
        )

        assert result["status"] == "completed"
        assert result["total"] == len(test_user_ids)
        assert result["successes"] == len(test_user_ids)
        assert result["failures"] == 0
