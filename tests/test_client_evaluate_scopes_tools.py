"""
Integration tests for Client Scope Evaluation tools.

Covers:
- generate_example_access_token
- generate_example_id_token
- generate_example_userinfo
- get_client_evaluate_scopes_protocol_mappers
- get_client_evaluate_scopes_granted_roles
- get_client_evaluate_scopes_not_granted_roles
"""

import uuid

import pytest
from src.tools import client_tools, user_tools
from src.tools.client_evaluate_scopes_tools import (
    generate_example_access_token,
    generate_example_id_token,
    generate_example_userinfo,
    get_client_evaluate_scopes_granted_roles,
    get_client_evaluate_scopes_not_granted_roles,
    get_client_evaluate_scopes_protocol_mappers,
)
from src.tools.keycloak_client import KeycloakClient

# Realm name used as roleContainerId for realm-level scope-mappings queries
_REALM_NAME = KeycloakClient().realm_name


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
async def eval_client():
    """Create a confidential test client for scope evaluation."""
    client_id = f"test-eval-client-{uuid.uuid4().hex[:8]}"

    await client_tools.create_client(
        client_id=client_id,
        name="Test Evaluate Scopes Client",
        enabled=True,
        protocol="openid-connect",
        public_client=False,
        direct_access_grants_enabled=True,
        service_accounts_enabled=True,
        standard_flow_enabled=True,
        redirect_uris=["http://localhost:*"],
    )

    clients = await client_tools.list_clients(client_id=client_id)
    test_client = next((c for c in clients if c["clientId"] == client_id), None)
    client_db_id = test_client["id"]

    yield {"id": client_db_id, "clientId": client_id}

    try:
        await client_tools.delete_client(client_db_id)
    except Exception:
        pass


@pytest.fixture(scope="module")
async def eval_user():
    """Create a test user for scope evaluation (email verified, no required actions)."""
    username = f"test-eval-user-{uuid.uuid4().hex[:8]}"
    user_email = f"{username}@example.com"

    await user_tools.create_user(
        username=username,
        email=user_email,
        first_name="Eval",
        last_name="User",
        enabled=True,
        email_verified=True,
    )

    users = await user_tools.list_users(email=user_email)
    test_user = users[0] if users else None
    user_id = test_user["id"]

    # Clear any default required actions (e.g. CONFIGURE_TOTP) that would affect results
    await user_tools.update_user(user_id=user_id, required_actions=[])

    yield {"id": user_id, "username": username}

    try:
        await user_tools.delete_user(user_id)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# generate_example_access_token
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGenerateExampleAccessToken:
    """Tests for generate_example_access_token."""

    async def test_returns_dict(self, eval_client, eval_user):
        """Should return a non-empty dict."""
        result = await generate_example_access_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
        )
        assert isinstance(result, dict)
        assert len(result) > 0

    async def test_contains_standard_claims(self, eval_client, eval_user):
        """Access token must contain standard JWT claims."""
        result = await generate_example_access_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
        )
        assert "sub" in result
        assert "iss" in result
        assert "iat" in result
        assert "exp" in result

    async def test_with_scope_parameter(self, eval_client, eval_user):
        """Passing an explicit scope should still return a valid token."""
        result = await generate_example_access_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid profile email",
        )
        assert isinstance(result, dict)
        assert "sub" in result

    async def test_realm_parameter(self, eval_client, eval_user):
        """realm=None should behave identically to the default."""
        result = await generate_example_access_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            realm=None,
        )
        assert isinstance(result, dict)
        assert "sub" in result


# ---------------------------------------------------------------------------
# generate_example_id_token
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGenerateExampleIdToken:
    """Tests for generate_example_id_token."""

    async def test_returns_dict(self, eval_client, eval_user):
        """Should return a non-empty dict."""
        result = await generate_example_id_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid",
        )
        assert isinstance(result, dict)
        assert len(result) > 0

    async def test_contains_sub_claim(self, eval_client, eval_user):
        """ID token must contain the 'sub' claim."""
        result = await generate_example_id_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid",
        )
        assert "sub" in result

    async def test_with_profile_scope(self, eval_client, eval_user):
        """Requesting 'openid profile' should return profile claims."""
        result = await generate_example_id_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid profile",
        )
        assert isinstance(result, dict)
        assert "sub" in result

    async def test_realm_parameter(self, eval_client, eval_user):
        """realm=None should behave identically to the default."""
        result = await generate_example_id_token(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid",
            realm=None,
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# generate_example_userinfo
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGenerateExampleUserinfo:
    """Tests for generate_example_userinfo."""

    async def test_returns_dict(self, eval_client, eval_user):
        """Should return a non-empty dict."""
        result = await generate_example_userinfo(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
        )
        assert isinstance(result, dict)
        assert len(result) > 0

    async def test_contains_sub_claim(self, eval_client, eval_user):
        """UserInfo response must always contain 'sub'."""
        result = await generate_example_userinfo(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
        )
        assert "sub" in result

    async def test_with_scope_parameter(self, eval_client, eval_user):
        """Passing scope='openid email' should return the email claim if mapped."""
        result = await generate_example_userinfo(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            scope="openid email",
        )
        assert isinstance(result, dict)
        assert "sub" in result

    async def test_realm_parameter(self, eval_client, eval_user):
        """realm=None should behave identically to the default."""
        result = await generate_example_userinfo(
            client_id=eval_client["id"],
            user_id=eval_user["id"],
            realm=None,
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# get_client_evaluate_scopes_protocol_mappers
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGetProtocolMappers:
    """Tests for get_client_evaluate_scopes_protocol_mappers."""

    async def test_returns_list(self, eval_client):
        """Should return a list (possibly empty for a bare client)."""
        result = await get_client_evaluate_scopes_protocol_mappers(
            client_id=eval_client["id"]
        )
        assert isinstance(result, list)

    async def test_mappers_have_required_fields(self, eval_client):
        """Each mapper entry must contain the standard evaluation fields."""
        result = await get_client_evaluate_scopes_protocol_mappers(
            client_id=eval_client["id"]
        )
        for mapper in result:
            assert "mapperId" in mapper or "mapperName" in mapper, (
                f"Mapper missing identity fields: {mapper}"
            )
            assert "containerName" in mapper
            assert "containerType" in mapper

    async def test_with_scope_parameter(self, eval_client):
        """Passing a scope should filter mappers to those effective for that scope."""
        result = await get_client_evaluate_scopes_protocol_mappers(
            client_id=eval_client["id"],
            scope="openid profile email",
        )
        assert isinstance(result, list)

    async def test_realm_parameter(self, eval_client):
        """realm=None should behave identically to the default."""
        result = await get_client_evaluate_scopes_protocol_mappers(
            client_id=eval_client["id"],
            realm=None,
        )
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_client_evaluate_scopes_granted_roles
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGrantedRoles:
    """Tests for get_client_evaluate_scopes_granted_roles."""

    async def test_returns_list(self, eval_client):
        """Should return a list for the realm role container."""
        result = await get_client_evaluate_scopes_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        assert isinstance(result, list)

    async def test_roles_have_required_fields(self, eval_client):
        """Each granted role must have standard RoleRepresentation fields."""
        result = await get_client_evaluate_scopes_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        for role in result:
            assert "id" in role
            assert "name" in role

    async def test_with_scope_parameter(self, eval_client):
        """Passing a scope should return roles granted within that scope."""
        result = await get_client_evaluate_scopes_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
            scope="openid",
        )
        assert isinstance(result, list)

    async def test_realm_parameter(self, eval_client):
        """realm=None should behave identically to the default."""
        result = await get_client_evaluate_scopes_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
            realm=None,
        )
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_client_evaluate_scopes_not_granted_roles
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestNotGrantedRoles:
    """Tests for get_client_evaluate_scopes_not_granted_roles."""

    async def test_returns_list(self, eval_client):
        """Should return a list for the realm role container."""
        result = await get_client_evaluate_scopes_not_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        assert isinstance(result, list)

    async def test_roles_have_required_fields(self, eval_client):
        """Each not-granted role must have standard RoleRepresentation fields."""
        result = await get_client_evaluate_scopes_not_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        for role in result:
            assert "id" in role
            assert "name" in role

    async def test_with_scope_parameter(self, eval_client):
        """Passing a scope should return roles not granted within that scope."""
        result = await get_client_evaluate_scopes_not_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
            scope="openid",
        )
        assert isinstance(result, list)

    async def test_granted_and_not_granted_are_disjoint(self, eval_client):
        """Granted and not-granted role sets must not overlap."""
        granted = await get_client_evaluate_scopes_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        not_granted = await get_client_evaluate_scopes_not_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
        )
        granted_ids = {r["id"] for r in granted}
        not_granted_ids = {r["id"] for r in not_granted}
        overlap = granted_ids & not_granted_ids
        assert not overlap, f"Roles appear in both granted and not-granted: {overlap}"

    async def test_realm_parameter(self, eval_client):
        """realm=None should behave identically to the default."""
        result = await get_client_evaluate_scopes_not_granted_roles(
            client_id=eval_client["id"],
            role_container_id=_REALM_NAME,
            realm=None,
        )
        assert isinstance(result, list)
