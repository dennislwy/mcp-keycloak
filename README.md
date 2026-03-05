# Keycloak MCP Server 
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE.txt)
[![smithery badge](https://smithery.ai/badge/@idoyudha/mcp-keycloak)](https://smithery.ai/server/@idoyudha/mcp-keycloak)
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/idoyudha/mcp-keycloak)](https://archestra.ai/mcp-catalog/idoyudha__mcp-keycloak)

A Model Context Protocol (MCP) server that provides a natural language interface for managing Keycloak identity and access management through its REST API. This server enables AI agents to perform user management, client configuration, realm administration, and role-based access control operations seamlessly.

## Overview

The Keycloak MCP Server bridges the gap between AI applications and Keycloak's powerful identity management capabilities. Whether you're building an AI assistant that needs to manage users, configure clients, or handle complex authorization scenarios, this server provides the tools you need through simple, natural language commands.

## Features

### 🔐 Comprehensive User Management
Manage users lifecycle from creation to deletion, including password resets, session management, and user attribute updates.

### 🏢 Client Configuration
Create and configure OAuth2/OIDC clients, manage client secrets, and handle service accounts programmatically.

### 👥 Role-Based Access Control
Define and assign realm and client-specific roles, manage user permissions, and implement fine-grained access control.

### 🏛️ Realm Administration
Configure realm settings, manage default groups, handle event configurations, and control realm-wide policies.

### 🔐 Authentication Management
Comprehensive authentication flow management including creating, updating, and deleting flows, managing executions, and configuring authenticators.

### 🔄 Group Management
Organize users into groups, manage group hierarchies, handle group-based permissions efficiently, and navigate nested group structures.

### 🛡️ Attack Detection & Security
Monitor and manage brute force protection, clear login failures, and release temporarily locked users.

## Installation

### Installing via Smithery

To install mcp-keycloak for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-keycloak):

```bash
npx -y @smithery/cli install mcp-keycloak --client claude
```

### Quick Start

Install using pip:
```bash
pip install mcp-keycloak
```

### Development Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/idoyudha/mcp-keycloak.git
cd mcp-keycloak
pip install -e .
```

## Configuration

The server can be configured using environment variables or a `.env` file:

```bash
# Required configuration
SERVER_URL=https://your-keycloak-server.com
USERNAME=admin-username
PASSWORD=admin-password
REALM_NAME=your-realm

# Optional OAuth2 client configuration
CLIENT_ID=optional-client-id
CLIENT_SECRET=optional-client-secret
```

## Tools

The Keycloak MCP Server provides a comprehensive set of tools organized by functionality:

### User Management
Complete user lifecycle management with advanced search and filtering:
- `list_users` - List users with pagination, exact matching, name filters, email verification status, custom attributes, and IDP filtering
- `get_user` - Retrieve a single user by ID
- `create_user` / `update_user` / `delete_user` - Full CRUD operations with group and role assignment
- `reset_user_password` - Password management
- `get_user_sessions` / `logout_user` - Session control
- `count_users` - User statistics
- Support for required actions (VERIFY_EMAIL, UPDATE_PASSWORD, CONFIGURE_TOTP, etc.)

### User Profile Management
Declarative user profile configuration (attributes, validators, permissions, groups):
- `get_user_profile` - Get the full UPConfig (attributes, validators, permissions, groups, unmanaged attribute policy)
- `update_user_profile` - Update the profile configuration; merges provided keys with current config so only changed fields need to be supplied
- `get_user_profile_metadata` - Read-only metadata view of the profile as seen by account consoles and clients

### Client Management
OAuth2/OIDC client configuration with comprehensive single-step creation, zero-downtime secret rotation, fine-grained permissions, and optional scope management:
- `list_clients` - List clients with advanced filtering (client_id, q, search, pagination)
- `get_client` / `get_client_by_clientid` - Retrieve client details
- `create_client` - Create clients with 25 parameters including consent, scopes, attributes, and URLs (single-step configuration)
- `update_client` - Full client updates with 24+ parameters
- `update_client_advanced` - Raw ClientRepresentation update for full control over any property
- `delete_client` - Client removal
- `get_client_secret` / `regenerate_client_secret` - Secret management with rotation support
- `get_client_secret_rotated` / `delete_client_secret_rotated` - Manage rotated secrets for seamless rotation
- `get_client_service_account` - Service account access
- `list_client_default_client_scopes` / `update_client_default_client_scope` / `delete_client_default_client_scope` - Default client scope management
- `list_optional_client_scopes` / `add_optional_client_scope` / `delete_optional_client_scope` - Optional client scope management (use these dedicated endpoints — `update_client` does not persist optional scopes)
- `get_client_management_permissions` / `update_client_management_permissions` - Fine-grained authorization control
- Support for consent, full scope control, custom attributes, authentication types, zero-downtime secret rotation, and delegated management

### Client Protocol Mappers
Protocol mapper management for clients:
- `list_client_protocol_mappers` / `get_client_protocol_mapper` - List and retrieve mappers
- `create_client_protocol_mapper` / `update_client_protocol_mapper` - Mapper CRUD operations
- `delete_client_protocol_mapper` - Remove protocol mappers
- `create_client_protocol_mappers_bulk` - Bulk mapper creation
- `get_client_protocol_mappers_by_protocol` - Filter mappers by protocol type

### Client Scopes
Client scope management:
- `list_client_scopes` / `get_client_scope` - List and retrieve scopes
- `create_client_scope` / `update_client_scope` - Scope CRUD operations
- `delete_client_scope` - Remove client scopes

### Client Scope Protocol Mappers
Protocol mapper management for client scopes:
- `list_client_scope_protocol_mappers` / `get_client_scope_protocol_mapper` - List and retrieve mappers
- `create_client_scope_protocol_mapper` / `update_client_scope_protocol_mapper` - Mapper CRUD operations
- `delete_client_scope_protocol_mapper` - Remove protocol mappers
- `create_client_scope_protocol_mappers_bulk` - Bulk mapper creation
- `get_client_scope_protocol_mappers_by_protocol` - Filter mappers by protocol type

### Client Role Mappings
Group and user client role mapping management:
- `list_available_client_role_mappings` - List available client roles for groups/users
- `list_composite_client_role_mappings` - List effective (composite) client role mappings
- `get_client_role_mappings` - Retrieve current role mappings
- `add_client_role_mappings` / `delete_client_role_mappings` - Manage role assignments

### Role Management
Fine-grained permission control:
- `list_realm_roles` / `get_realm_role` / `create_realm_role` / `update_realm_role` / `delete_realm_role` - Full realm role CRUD
- `list_client_roles` / `create_client_role` - Client-specific roles
- `assign_realm_role_to_user` / `remove_realm_role_from_user` - Role assignments
- `get_user_realm_roles` / `assign_client_role_to_user` - User role queries
- `list_role_composites` / `add_role_composites` / `delete_role_composites` - Composite role management
- `get_role_composites_realm` / `get_role_composites_clients` - Query composite role hierarchies

### Group Management
Hierarchical user organization with advanced search and hierarchy support:
- `list_groups` / `get_group` / `create_group` / `update_group` / `delete_group` - Full group CRUD with exact matching and hierarchy control
- `list_subgroups` / `create_subgroup` - Navigate and build nested group structures
- `get_group_members` / `add_user_to_group` / `remove_user_from_group` - Membership management
- `get_user_groups` - List all groups a user belongs to

### Realm Administration
System-wide configuration:
- `get_accessible_realms` - List of accessible realms
- `get_realm_info` / `update_realm_settings` - Realm configuration (themes, login settings, brute-force, OTP policy, WebAuthn Passwordless policy, flow bindings)
- `update_realm_settings_advanced` - Power-user tool accepting a raw `RealmRepresentation` dict for full control over any realm property
- `get_realm_events_config` / `update_realm_events_config` - Event listeners, admin events, and enabled event types
- `get_realm_default_groups` / `add_realm_default_group` / `remove_realm_default_group` - Default group settings
- `remove_all_user_sessions` - Invalidate all active sessions in a realm

### OIDC Protocol
Complete OAuth2/OpenID Connect protocol operations:
- `request_token` - Request access tokens using various OAuth2 grant types (password, client_credentials, authorization_code, refresh_token)
- `introspect_token` - Introspect tokens to validate state and retrieve metadata (RFC 7662 compliant)
- `get_userinfo` - Retrieve user claims using Bearer token authentication
- `revoke_token` - Revoke access or refresh tokens (RFC 7009 compliant)
- `logout` - End user sessions and invalidate refresh tokens
- `exchange_token` - Exchange a token for another targeting a different audience/service (RFC 8693 Token Exchange)
- `get_certs` - Get JWKS for JWT signature verification
- `get_openid_configuration` - Get OpenID Connect Discovery document with all endpoints and capabilities

### Authentication Management
Complete authentication flow and execution control, organized by sub-category:

**Authentication Flows**
- `list_authentication_flows` / `get_authentication_flow` - Flow listing and retrieval
- `create_authentication_flow` / `update_authentication_flow` / `delete_authentication_flow` - Flow CRUD
- `copy_authentication_flow` - Duplicate an existing flow as a starting point

**Flow Executions**
- `get_flow_executions` / `update_flow_executions` - Manage execution ordering and requirements within a flow
- `add_execution_to_flow` / `add_subflow_to_flow` - Add executions or nested sub-flows
- `create_execution` / `get_execution` / `delete_execution` - Standalone execution management
- `raise_execution_priority` / `lower_execution_priority` - Reorder executions within a flow
- `get_execution_config` / `update_execution_config` - Execution-level configuration management

**Authenticator Configuration**
- `get_authenticator_config` / `create_authenticator_config` / `update_authenticator_config` / `delete_authenticator_config` - Authenticator configuration CRUD

**Authenticator Providers**
- `get_authenticator_providers` / `get_client_authenticator_providers` - List available authenticator providers
- `get_provider_config_description` - Get configuration schema for a specific provider

**Required Actions**
- `get_required_actions` / `get_required_action` / `update_required_action` / `delete_required_action` - Full required action CRUD
- `register_required_action` / `get_unregistered_required_actions` - Register new required action providers
- `raise_required_action_priority` / `lower_required_action_priority` - Reorder required actions
- `get_required_action_config_description` - Get configuration schema for a required action provider
- `get_required_action_config` / `update_required_action_config` / `delete_required_action_config` - Required action configuration management

**Form Providers**
- `get_form_providers` / `get_form_action_providers` - List available form and form-action providers

**Per-Client Configuration**
- `get_per_client_config_description` - Get configuration schema for per-client authentication overrides

### Attack Detection
Brute force protection and security monitoring:
- `get_user_brute_force_status` - Monitor failed login attempts and lockout status
- `clear_user_login_failures` - Release individual locked users
- `clear_all_login_failures` - Bulk unlock all temporarily disabled users

### General Server Operations
Server-wide information and monitoring:
- `get_server_info` - Get comprehensive server information including version, memory, features, themes, providers, and system metadata

## Usage

### Running the Server

The server supports both stdio (default) and HTTP transports. The smithery.yaml configuration file enables deployment on the Smithery platform and automatic installation via Smithery CLI:

```bash
# Run in stdio mode (default, for local CLI tools)
python -m src.main

# Run in HTTP mode with streamable HTTP transport
TRANSPORT=http python -m src.main

# Run HTTP mode on a custom port
TRANSPORT=http PORT=8080 python -m src.main

# Or use the convenience script:
./scripts/run_server.sh         # stdio mode (default)
./scripts/run_server.sh http    # HTTP mode
PORT=8080 ./scripts/run_server.sh http  # HTTP mode on custom port
```

When using HTTP transport, the server will be accessible at `http://127.0.0.1:8000/mcp/` (or your custom PORT).

### HTTP Transport

The Keycloak MCP Server supports HTTP transport mode, which offers several advantages:

- **Network Accessibility**: Access the server from any machine on your network
- **Multiple Clients**: Support concurrent connections from multiple AI clients
- **Integration Flexibility**: Easy integration with web applications and APIs
- **Load Balancing**: Deploy behind a reverse proxy for scalability

#### HTTP Protocol Details

The HTTP transport follows the MCP specification for Streamable HTTP. FastMCP automatically handles all protocol requirements:

- **Endpoint**: All communication happens through `/mcp/` endpoint
- **Request Method**: POST requests with JSON-RPC 2.0 messages
- **Content Types**: 
  - Server returns `Content-Type: application/json` for single responses
  - Server returns `Content-Type: text/event-stream` for streaming responses
- **Accept Headers**: Clients must include `Accept: application/json, text/event-stream`
- **Message Format**: All messages use JSON-RPC 2.0 format, UTF-8 encoded

FastMCP automatically determines whether to return a single JSON response or an SSE stream based on the request type and whether the response needs streaming capabilities.

#### Connecting to HTTP Server

When running in HTTP mode, clients can connect to:
```
http://127.0.0.1:8000/mcp/
```

Example client request:
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "list_tools", "id": 1}'
```

#### Security Implementation

The HTTP transport implements all MCP specification security requirements:

**✅ Origin Header Validation (REQUIRED)**
- Automatically validates Origin headers to prevent DNS rebinding attacks
- Only allows connections from `localhost` and `127.0.0.1` origins
- Blocks unauthorized cross-origin requests

**✅ Localhost Binding (RECOMMENDED)**
- Binds to `127.0.0.1` only to prevent network-based attacks
- Follows MCP specification security recommendations

**✅ No Authentication Required**
- The server runs without authentication requirements for simplified local development
- Suitable for localhost usage and trusted environments

For production deployments, additional considerations:
- Use HTTPS with proper certificates
- Deploy behind a reverse proxy (nginx, Apache)
- Set appropriate firewall rules
- Implement authentication at the reverse proxy level if needed

### Integration Examples

#### Prerequisites

Before integrating the Keycloak MCP Server, ensure you have one of the following installed:

- **uvx** (recommended): Install via `pip install uvx` or `pipx install uvx`
- **uv**: Follow [installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
- **npm/npx**: For Smithery installation (comes with [Node.js](https://nodejs.org/))

#### Option 1: Using Smithery CLI (Recommended)

The easiest way - automatically configures everything for Claude Desktop:

```bash
npx @smithery/cli install @idoyudha/mcp-keycloak --client claude
```

This command will prompt you for the required configuration values and set up the server automatically.

#### Option 2: Using uvx (Manual Setup)

No cloning required! Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "keycloak": {
      "command": "uvx",
      "args": ["mcp-keycloak"],
      "env": {
        "SERVER_URL": "https://your-keycloak.com",
        "USERNAME": "admin",
        "PASSWORD": "admin-password",
        "REALM_NAME": "your-realm"
      }
    }
  }
}
```

#### Option 3: Local Development Setup

For development or customization:

1. Clone the repository:
```bash
git clone https://github.com/idoyudha/mcp-keycloak.git
cd mcp-keycloak
```

2. Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "keycloak": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-keycloak",
        "run",
        "python",
        "-m",
        "src"
      ],
      "env": {
        "SERVER_URL": "https://your-keycloak.com",
        "USERNAME": "admin",
        "PASSWORD": "admin-password",
        "REALM_NAME": "your-realm"
      }
    }
  }
}
```

💡 **Quick Tips:**
- Replace `/path/to/mcp-keycloak` with the actual path where you cloned the repository
- Ensure your Keycloak server URL includes the protocol (`https://` or `http://`)
- The `REALM_NAME` should match an existing realm in your Keycloak instance

## Example Use Cases

### 🤖 AI-Powered Identity Management
Build AI assistants that can handle user onboarding, permission management, and access control through natural language commands.

### 🔄 Automated User Provisioning
Create workflows that automatically provision users, assign roles, and configure client applications based on business rules.

### 📊 Identity Analytics
Query and analyze user data, session information, and access patterns to gain insights into your identity infrastructure.

### 🚀 DevOps Integration
Integrate Keycloak management into your CI/CD pipelines, allowing automated configuration of identity services.

## Testing

The project includes a comprehensive test suite with 130 integration tests covering all tool categories including server information, OIDC protocol operations, client secret rotation, default and optional scope management, fine-grained permissions, and authentication management. For detailed information, see [tests/README.md](tests/README.md).

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_user_tools.py -v

# Run with coverage
uv run pytest --cov=src tests/

# Skip integration tests (for quick checks)
uv run pytest -m "not integration"
```

## Requirements

- Python 3.12 or higher
- Keycloak server (tested with Keycloak 18+)
- Admin access to Keycloak realm

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/idoyudha/mcp-keycloak).

## Reference
- [Keycloak REST API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak Documentation](https://www.keycloak.org/documentation)