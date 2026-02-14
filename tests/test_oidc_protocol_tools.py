"""
Integration tests for OIDC Protocol Tools.

These tests require a running Keycloak server with a configured client.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import client_tools, oidc_protocol_tools, user_tools

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
        def fixture(func=None, scope=None):
            if func:
                return func
            return lambda f: f

    pytest = MockPytest()


if PYTEST_AVAILABLE:

    @pytest.fixture(scope="module")
    async def test_client():
        """Create a test client for OIDC operations."""
        client_id = f"test-oidc-client-{uuid.uuid4().hex[:8]}"

        # Create a confidential client for testing token requests
        # Must have directAccessGrantsEnabled for password grant
        await client_tools.create_client(
            client_id=client_id,
            name="Test OIDC Client",
            enabled=True,
            protocol="openid-connect",
            public_client=False,  # Confidential client (has secret)
            direct_access_grants_enabled=True,  # CRITICAL: Enable password grant
            service_accounts_enabled=True,  # Enable client credentials grant
            standard_flow_enabled=True,  # Enable authorization code flow
            redirect_uris=["http://localhost:*"],  # Valid redirect URIs
        )

        # Get client database ID
        clients = await client_tools.list_clients(client_id=client_id)
        test_client = next((c for c in clients if c["clientId"] == client_id), None)
        client_db_id = test_client["id"]

        # Get client secret
        secret_response = await client_tools.get_client_secret(client_db_id)
        client_secret = secret_response.get("value")

        yield {
            "id": client_db_id,
            "clientId": client_id,
            "secret": client_secret,
        }

        # Cleanup
        try:
            await client_tools.delete_client(client_db_id)
        except Exception:
            pass

    @pytest.fixture(scope="module")
    async def test_user():
        """Create a test user for OIDC password grant testing."""
        username = f"test-oidc-user-{uuid.uuid4().hex[:8]}"
        password = "Test@Password123"

        # Create user with email verified
        await user_tools.create_user(
            username=username,
            email=f"{username}@example.com",
            first_name="Test",
            last_name="OIDC User",
            enabled=True,
            email_verified=True,  # CRITICAL: Mark email as verified
        )

        # Find user
        users = await user_tools.list_users(search=username)
        test_user = next((u for u in users if u["username"] == username), None)
        user_id = test_user["id"]

        # Set password (non-temporary)
        await user_tools.reset_user_password(
            user_id=user_id, password=password, temporary=False
        )

        yield {"id": user_id, "username": username, "password": password}

        # Cleanup
        try:
            await user_tools.delete_user(user_id)
        except Exception:
            pass


@pytest.mark.integration
class TestOIDCTokenRequest:
    """Test OIDC token request operations."""

    async def test_password_grant(self, test_client, test_user):
        """Test requesting tokens using password grant."""
        # Request token using password grant
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
            scope="openid profile email",
        )

        # Verify response structure
        assert "access_token" in token_response
        assert "refresh_token" in token_response
        assert "token_type" in token_response
        assert token_response["token_type"].lower() == "bearer"
        assert "expires_in" in token_response
        assert isinstance(token_response["expires_in"], int)
        assert token_response["expires_in"] > 0

        # Verify ID token is present for openid scope
        if "openid" in token_response.get("scope", ""):
            assert "id_token" in token_response

    async def test_client_credentials_grant(self, test_client):
        """Test requesting tokens using client credentials grant."""
        # Request token using client credentials grant
        token_response = await oidc_protocol_tools.request_token(
            grant_type="client_credentials",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            scope="openid",
        )

        # Verify response structure
        assert "access_token" in token_response
        assert "token_type" in token_response
        assert token_response["token_type"].lower() == "bearer"
        assert "expires_in" in token_response

        # Client credentials grant typically doesn't return refresh token
        # (depends on Keycloak configuration)

    async def test_refresh_token_grant(self, test_client, test_user):
        """Test refreshing tokens using refresh token grant."""
        # First, get initial tokens
        initial_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
            scope="openid",
        )

        refresh_token = initial_response["refresh_token"]

        # Use refresh token to get new tokens
        refreshed_response = await oidc_protocol_tools.request_token(
            grant_type="refresh_token",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            refresh_token=refresh_token,
        )

        # Verify new tokens were issued
        assert "access_token" in refreshed_response
        assert "refresh_token" in refreshed_response
        assert refreshed_response["access_token"] != initial_response["access_token"]

    async def test_password_grant_invalid_credentials(self, test_client):
        """Test password grant with invalid credentials."""
        try:
            await oidc_protocol_tools.request_token(
                grant_type="password",
                client_id=test_client["clientId"],
                client_secret=test_client["secret"],
                username="nonexistent_user",
                password="wrong_password",
            )
            # Should not reach here
            assert False, "Expected exception for invalid credentials"
        except Exception as e:
            # Verify error is related to invalid credentials
            error_msg = str(e).lower()
            assert (
                "401" in error_msg
                or "unauthorized" in error_msg
                or "invalid" in error_msg
            )

    async def test_password_grant_missing_params(self, test_client):
        """Test password grant with missing required parameters."""
        try:
            await oidc_protocol_tools.request_token(
                grant_type="password",
                client_id=test_client["clientId"],
                # Missing username and password
            )
            assert False, "Expected ValueError for missing parameters"
        except ValueError as e:
            assert "username" in str(e).lower() or "password" in str(e).lower()


@pytest.mark.integration
class TestOIDCTokenIntrospection:
    """Test OIDC token introspection operations."""

    async def test_introspect_active_token(self, test_client, test_user):
        """Test introspecting an active access token."""
        # First, get a token
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
            scope="openid profile email",
        )

        access_token = token_response["access_token"]

        # Introspect the token
        introspection_response = await oidc_protocol_tools.introspect_token(
            token=access_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            token_type_hint="access_token",
        )

        # Verify introspection response
        assert introspection_response["active"] is True
        assert "exp" in introspection_response
        assert "iat" in introspection_response
        assert "client_id" in introspection_response
        assert "username" in introspection_response
        assert introspection_response["username"] == test_user["username"]
        assert "scope" in introspection_response

    async def test_introspect_refresh_token(self, test_client, test_user):
        """Test introspecting a refresh token."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        refresh_token = token_response["refresh_token"]

        # Introspect the refresh token
        introspection_response = await oidc_protocol_tools.introspect_token(
            token=refresh_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            token_type_hint="refresh_token",
        )

        # Verify refresh token is active
        assert introspection_response["active"] is True
        assert "exp" in introspection_response

    async def test_introspect_invalid_token(self, test_client):
        """Test introspecting an invalid/expired token."""
        # Use a fake/invalid token
        fake_token = "invalid.token.value"

        introspection_response = await oidc_protocol_tools.introspect_token(
            token=fake_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
        )

        # Invalid token should return active=false
        assert introspection_response["active"] is False

    async def test_introspect_without_type_hint(self, test_client, test_user):
        """Test introspection without providing token type hint."""
        # Get token
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        access_token = token_response["access_token"]

        # Introspect without hint
        introspection_response = await oidc_protocol_tools.introspect_token(
            token=access_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            # No token_type_hint provided
        )

        # Should still work
        assert introspection_response["active"] is True


@pytest.mark.integration
class TestOIDCTokenLifecycle:
    """Test complete OIDC token lifecycle."""

    async def test_complete_token_lifecycle(self, test_client, test_user):
        """Test complete token lifecycle: request, introspect, refresh, introspect."""
        # 1. Request initial tokens
        initial_tokens = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
            scope="openid",
        )

        # 2. Introspect access token
        introspection1 = await oidc_protocol_tools.introspect_token(
            token=initial_tokens["access_token"],
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
        )
        assert introspection1["active"] is True

        # 3. Refresh tokens
        refreshed_tokens = await oidc_protocol_tools.request_token(
            grant_type="refresh_token",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            refresh_token=initial_tokens["refresh_token"],
        )

        # 4. Introspect new access token
        introspection2 = await oidc_protocol_tools.introspect_token(
            token=refreshed_tokens["access_token"],
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
        )
        assert introspection2["active"] is True

        # 5. Verify tokens are different
        assert initial_tokens["access_token"] != refreshed_tokens["access_token"]
