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

        # Find user by email (works regardless of registrationEmailAsUsername setting)
        user_email = f"{username}@example.com"
        users = await user_tools.list_users(email=user_email)
        test_user = users[0] if users else None
        user_id = test_user["id"]

        # Clear any default required actions (e.g. CONFIGURE_TOTP) that block login
        from src.tools.user_tools import update_user
        await update_user(user_id=user_id, required_actions=[])

        # Set password (non-temporary)
        await user_tools.reset_user_password(
            user_id=user_id, password=password, temporary=False
        )

        # Use actual stored username for login (handles both plain and email-as-username realms)
        yield {"id": user_id, "username": test_user["username"], "password": password}

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


@pytest.mark.integration
class TestOIDCUserInfo:
    """Test OIDC UserInfo endpoint operations."""

    async def test_get_userinfo(self, test_client, test_user):
        """Test getting user information with access token."""
        # First, get a token with required scopes
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
            scope="openid profile email",
        )

        access_token = token_response["access_token"]

        # Get user info
        userinfo = await oidc_protocol_tools.get_userinfo(access_token=access_token)

        # Verify user info structure
        assert "sub" in userinfo  # Subject identifier
        assert "preferred_username" in userinfo
        assert userinfo["preferred_username"] == test_user["username"]

        # Verify profile claims (if scope included)
        if "profile" in token_response.get("scope", ""):
            assert "name" in userinfo or "given_name" in userinfo

        # Verify email claims (if scope included)
        if "email" in token_response.get("scope", ""):
            assert "email" in userinfo
            assert "email_verified" in userinfo

    async def test_get_userinfo_invalid_token(self):
        """Test getting user info with invalid token."""
        try:
            await oidc_protocol_tools.get_userinfo(access_token="invalid.token.value")
            assert False, "Expected exception for invalid token"
        except Exception as e:
            error_msg = str(e).lower()
            assert "401" in error_msg or "unauthorized" in error_msg


@pytest.mark.integration
class TestOIDCTokenRevocation:
    """Test OIDC token revocation operations."""

    async def test_revoke_refresh_token(self, test_client, test_user):
        """Test revoking a refresh token."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        refresh_token = token_response["refresh_token"]

        # Revoke the refresh token
        revoke_response = await oidc_protocol_tools.revoke_token(
            token=refresh_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            token_type_hint="refresh_token",
        )

        # Revocation endpoint returns empty response on success
        assert revoke_response == {} or revoke_response is None

        # Try to use the revoked refresh token (should fail)
        try:
            await oidc_protocol_tools.request_token(
                grant_type="refresh_token",
                client_id=test_client["clientId"],
                client_secret=test_client["secret"],
                refresh_token=refresh_token,
            )
            assert False, "Expected exception when using revoked refresh token"
        except Exception as e:
            error_msg = str(e).lower()
            assert (
                "400" in error_msg or "invalid" in error_msg or "revoked" in error_msg
            )

    async def test_revoke_access_token(self, test_client, test_user):
        """Test revoking an access token."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        access_token = token_response["access_token"]

        # Revoke the access token
        revoke_response = await oidc_protocol_tools.revoke_token(
            token=access_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            token_type_hint="access_token",
        )

        # Revocation endpoint returns empty response on success
        assert revoke_response == {} or revoke_response is None

    async def test_revoke_token_without_hint(self, test_client, test_user):
        """Test revoking a token without type hint."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        # Revoke without hint (should still work)
        revoke_response = await oidc_protocol_tools.revoke_token(
            token=token_response["refresh_token"],
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
        )

        assert revoke_response == {} or revoke_response is None


@pytest.mark.integration
class TestOIDCLogout:
    """Test OIDC logout operations."""

    async def test_logout(self, test_client, test_user):
        """Test logout with refresh token."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        refresh_token = token_response["refresh_token"]

        # Logout (invalidate session)
        logout_response = await oidc_protocol_tools.logout(
            refresh_token=refresh_token,
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
        )

        # Logout endpoint returns empty response on success
        assert logout_response == {} or logout_response is None

        # Try to use the refresh token after logout (should fail)
        try:
            await oidc_protocol_tools.request_token(
                grant_type="refresh_token",
                client_id=test_client["clientId"],
                client_secret=test_client["secret"],
                refresh_token=refresh_token,
            )
            assert False, "Expected exception when using refresh token after logout"
        except Exception as e:
            error_msg = str(e).lower()
            assert "400" in error_msg or "invalid" in error_msg

    async def test_logout_without_secret(self, test_client, test_user):
        """Test logout without client secret (should fail for confidential clients)."""
        # Get tokens
        token_response = await oidc_protocol_tools.request_token(
            grant_type="password",
            client_id=test_client["clientId"],
            client_secret=test_client["secret"],
            username=test_user["username"],
            password=test_user["password"],
        )

        # Logout without secret should fail for confidential clients
        try:
            await oidc_protocol_tools.logout(
                refresh_token=token_response["refresh_token"],
                client_id=test_client["clientId"],
            )
            assert False, "Expected exception when logging out without client secret"
        except Exception as e:
            error_msg = str(e).lower()
            assert "401" in error_msg or "unauthorized" in error_msg


@pytest.mark.integration
class TestOIDCCerts:
    """Test OIDC JWKS endpoint operations."""

    async def test_get_certs(self):
        """Test getting JWKS for token signature verification."""
        # Get JWKS
        jwks = await oidc_protocol_tools.get_certs()

        # Verify JWKS structure
        assert "keys" in jwks
        assert isinstance(jwks["keys"], list)
        assert len(jwks["keys"]) > 0

        # Verify at least one key has required JWK fields
        key = jwks["keys"][0]
        assert "kid" in key  # Key ID
        assert "kty" in key  # Key type
        assert "alg" in key  # Algorithm
        assert "use" in key  # Key usage (should be "sig" for signature)
        assert key["use"] == "sig"

        # For RSA keys, verify RSA-specific fields
        if key["kty"] == "RSA":
            assert "n" in key  # RSA modulus
            assert "e" in key  # RSA exponent

    async def test_get_certs_different_realm(self):
        """Test getting JWKS for a different realm."""
        # Get JWKS for master realm explicitly
        jwks = await oidc_protocol_tools.get_certs(realm="master")

        assert "keys" in jwks
        assert isinstance(jwks["keys"], list)


@pytest.mark.integration
class TestOIDCDiscovery:
    """Test OIDC discovery document operations."""

    async def test_get_openid_configuration(self):
        """Test getting OpenID Connect discovery document."""
        # Get OIDC configuration
        config = await oidc_protocol_tools.get_openid_configuration()

        # Verify required OpenID Connect Discovery fields
        assert "issuer" in config
        assert "authorization_endpoint" in config
        assert "token_endpoint" in config
        assert "userinfo_endpoint" in config
        assert "jwks_uri" in config
        assert "end_session_endpoint" in config

        # Verify optional but common fields
        assert "introspection_endpoint" in config  # Keycloak uses this name
        assert "revocation_endpoint" in config

        # Verify supported features
        assert "grant_types_supported" in config
        assert isinstance(config["grant_types_supported"], list)
        assert "authorization_code" in config["grant_types_supported"]
        assert "refresh_token" in config["grant_types_supported"]

        assert "response_types_supported" in config
        assert isinstance(config["response_types_supported"], list)

        assert "subject_types_supported" in config
        assert "id_token_signing_alg_values_supported" in config

        # Verify scopes and claims
        assert "scopes_supported" in config
        assert "openid" in config["scopes_supported"]

        assert "claims_supported" in config
        assert "sub" in config["claims_supported"]

    async def test_get_openid_configuration_different_realm(self):
        """Test getting discovery document for a different realm."""
        # Get configuration for master realm explicitly
        config = await oidc_protocol_tools.get_openid_configuration(realm="master")

        assert "issuer" in config
        assert "master" in config["issuer"]  # Should reference master realm
