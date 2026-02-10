"""
Integration tests for Authentication Management.

These tests require a running Keycloak server.
Configure the server details in your .env file.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools import authentication_management_tools as auth_tools

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


if PYTEST_AVAILABLE:

    @pytest.fixture
    def unique_flow_alias():
        """Generate a unique flow alias for testing."""
        return f"test-flow-{uuid.uuid4().hex[:8]}"


@pytest.mark.integration
class TestAuthenticationFlows:
    """Test authentication flow operations."""

    async def test_list_authentication_flows(self):
        """Test listing authentication flows."""
        flows = await auth_tools.list_authentication_flows()
        assert isinstance(flows, list)
        assert len(flows) > 0
        # Check that built-in flows exist
        flow_aliases = [f["alias"] for f in flows]
        assert "browser" in flow_aliases

    async def test_get_authentication_flow(self):
        """Test getting a specific authentication flow."""
        # First list flows to get an ID
        flows = await auth_tools.list_authentication_flows()
        browser_flow = next(f for f in flows if f["alias"] == "browser")
        flow_id = browser_flow["id"]

        # Get the browser flow by ID
        flow = await auth_tools.get_authentication_flow(flow_id)
        assert flow["alias"] == "browser"
        assert "id" in flow

    async def test_copy_authentication_flow(self, unique_flow_alias):
        """Test copying an authentication flow."""
        # Copy the browser flow
        copy_result = await auth_tools.copy_authentication_flow(
            flow_alias="browser", new_name=unique_flow_alias
        )
        assert "status" in copy_result
        assert "copied" in copy_result["status"].lower()

        # List flows and find our copied flow
        flows = await auth_tools.list_authentication_flows()
        copied_flow = next((f for f in flows if f["alias"] == unique_flow_alias), None)
        assert copied_flow is not None
        assert copied_flow["alias"] == unique_flow_alias

        # Clean up by deleting the copied flow (using ID)
        flow_id = copied_flow["id"]
        delete_result = await auth_tools.delete_authentication_flow(flow_id)
        assert "status" in delete_result


@pytest.mark.integration
class TestFlowExecutions:
    """Test flow execution operations."""

    async def test_get_flow_executions(self):
        """Test getting flow executions."""
        # Get executions for the browser flow
        executions = await auth_tools.get_flow_executions("browser")
        assert isinstance(executions, list)
        assert len(executions) > 0


@pytest.mark.integration
class TestAuthenticatorProviders:
    """Test authenticator provider operations."""

    async def test_get_authenticator_providers(self):
        """Test listing authenticator providers."""
        providers = await auth_tools.get_authenticator_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0

    async def test_get_client_authenticator_providers(self):
        """Test listing client authenticator providers."""
        providers = await auth_tools.get_client_authenticator_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0


@pytest.mark.integration
class TestRequiredActions:
    """Test required actions operations."""

    async def test_list_required_actions(self):
        """Test listing required actions."""
        actions = await auth_tools.get_required_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0
        # Check for common required actions
        action_aliases = [a["alias"] for a in actions]
        assert "VERIFY_EMAIL" in action_aliases or "UPDATE_PASSWORD" in action_aliases

    async def test_get_required_action(self):
        """Test getting a specific required action."""
        # Get VERIFY_EMAIL action which should exist
        action = await auth_tools.get_required_action("VERIFY_EMAIL")
        assert action["alias"] == "VERIFY_EMAIL"
        assert "name" in action
        assert "enabled" in action

    async def test_update_required_action(self):
        """Test updating a required action."""
        # Get current state of VERIFY_EMAIL
        current_action = await auth_tools.get_required_action("VERIFY_EMAIL")
        original_enabled = current_action.get("enabled", False)

        try:
            # Toggle the enabled state
            new_enabled = not original_enabled
            update_result = await auth_tools.update_required_action(
                alias="VERIFY_EMAIL",
                name=current_action["name"],
                enabled=new_enabled,
            )
            assert "status" in update_result
            assert "updated" in update_result["status"].lower()

            # Verify the update
            updated_action = await auth_tools.get_required_action("VERIFY_EMAIL")
            assert updated_action["enabled"] == new_enabled

        finally:
            # Restore original state
            await auth_tools.update_required_action(
                alias="VERIFY_EMAIL",
                name=current_action["name"],
                enabled=original_enabled,
            )

    async def test_get_unregistered_required_actions(self):
        """Test getting unregistered required actions."""
        unregistered = await auth_tools.get_unregistered_required_actions()
        assert isinstance(unregistered, list)
