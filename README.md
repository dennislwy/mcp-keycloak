# Keycloak MCP Server 
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
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

### 🎯 Client Scopes & Protocol Mappers
Define reusable client scopes, create custom protocol mappers for token claims, and control what information is included in access tokens and ID tokens.

### 🌐 Identity Providers
Configure external identity providers (Google, Facebook, OIDC, SAML), manage attribute mappers, and handle federated user identities for seamless SSO integration.

### 📁 User Federation
Connect external user stores (LDAP, Kerberos), configure user storage providers, and manage attribute mappings for centralized user management.

### 👥 Role-Based Access Control
Define and assign realm and client-specific roles, manage user permissions, and implement fine-grained access control.

### 🏛️ Realm Administration
Configure realm settings, manage default groups, handle event configurations, and control realm-wide policies.

### 🔐 Authentication Management
Comprehensive authentication flow management including creating, updating, and deleting flows, managing executions, and configuring authenticators.

### 📊 Events Management
Track and audit user activities and administrative changes with comprehensive event logging. Query user events (login, logout, registration), admin events (configuration changes), and manage event retention policies.

### 🔐 Sessions Management
Comprehensive session control and monitoring across all clients and users. Monitor active sessions, configure session timeouts, track user activity by IP address, and perform emergency logout operations for security incidents.

### 🛡️ Attack Detection & Brute Force Protection
Advanced security monitoring and attack detection capabilities. Monitor failed login attempts, configure brute force protection settings, analyze attack patterns, and manage user lockouts for enhanced security.

### 🔑 Keys & Certificate Management
Comprehensive cryptographic keys and certificate management. Monitor key expiration, manage signing algorithms, export and validate certificates, and rotate realm keys for maintaining security.

### ⚙️ Security Policies & Configuration
Complete security policy configuration including password policies, OTP policies, WebAuthn settings, browser security headers, SMTP configuration, and comprehensive realm security settings.

### 🏢 Organization Management
Multi-tenant organization management with domain verification and member control. Create and manage organizations, associate domains with automatic user assignment, manage organization members, and link identity providers for organization-specific authentication flows. (Requires Keycloak 23+ with organizations feature enabled)

### 🔄 Group Management
Organize users into groups, manage group hierarchies, and handle group-based permissions efficiently.

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
Complete user lifecycle management including:
- `list_users` - List users with pagination and filtering
- `create_user` / `update_user` / `delete_user` - Full CRUD operations
- `reset_user_password` - Password management
- `get_user_sessions` / `logout_user` - Session control
- `count_users` - User statistics

### Client Management
OAuth2/OIDC client configuration:
- `list_clients` / `get_client` / `create_client` - Client operations
- `get_client_secret` / `regenerate_client_secret` - Secret management
- `get_client_service_account` - Service account access
- `update_client` / `delete_client` - Client modifications

### Client Scopes
Reusable scope configuration and token customization:
- `list_client_scopes` / `get_client_scope` / `create_client_scope` - Scope CRUD
- `update_client_scope` / `delete_client_scope` - Scope modifications
- `get_realm_default_client_scopes` / `add_realm_default_client_scope` - Realm defaults
- `get_realm_optional_client_scopes` / `add_realm_optional_client_scope` - Realm optional
- `get_client_default_scopes` / `add_client_default_scope` - Client default scopes
- `get_client_optional_scopes` / `add_client_optional_scope` - Client optional scopes

### Protocol Mappers
Token claim customization for clients and scopes:
- `list_client_scope_protocol_mappers` / `create_client_scope_protocol_mapper` - Scope mappers
- `list_client_protocol_mappers` / `create_client_protocol_mapper` - Client mappers
- `update_client_scope_protocol_mapper` / `delete_client_scope_protocol_mapper` - Mapper CRUD
- `add_client_scope_protocol_mappers` / `add_client_protocol_mappers` - Batch operations
- `evaluate_client_scope_mappers` - Effective mapper evaluation
- `create_user_attribute_mapper` / `create_role_mapper` / `create_audience_mapper` - Quick templates

### Identity Providers
External authentication provider integration:
- `list_identity_providers` / `get_identity_provider` / `create_identity_provider` - Provider CRUD
- `update_identity_provider` / `delete_identity_provider` - Provider management
- `export_identity_provider` / `import_identity_provider_config` - Import/export
- `list_identity_provider_mappers` / `create_identity_provider_mapper` - Mapper management
- `get_user_federated_identities` / `add_user_federated_identity` - User identity linking
- `create_google_identity_provider` / `create_oidc_identity_provider` - Convenience functions

### User Federation
External user store integration:
- `list_components` / `get_component` / `create_component` - Component management
- `update_component` / `delete_component` / `get_component_sub_types` - Component operations
- `list_user_storage_providers` / `get_user_storage_credential_types` - Storage providers
- `create_ldap_user_storage` / `create_kerberos_user_storage` - Provider setup
- `get_ldap_mappers` / `create_ldap_attribute_mapper` - LDAP mapping

### Role Management
Fine-grained permission control:
- `list_realm_roles` / `create_realm_role` - Realm role operations
- `list_client_roles` / `create_client_role` - Client-specific roles
- `assign_realm_role_to_user` / `remove_realm_role_from_user` - Role assignments
- `get_user_realm_roles` / `assign_client_role_to_user` - User role queries

### Group Management
Hierarchical user organization and role mappings:
- `list_groups` / `create_group` / `update_group` - Group operations
- `get_group_members` / `add_user_to_group` - Membership management
- `get_user_groups` / `remove_user_from_group` - User group associations
- `get_group_role_mappings` / `add_realm_roles_to_group` - Role assignments
- `get_group_client_roles` / `add_client_roles_to_group` - Client role mappings
- `copy_group_roles` - Role copying between groups

### Realm Administration
System-wide configuration and operations:
- `get_accessible_realms` / `list_realms` - List accessible realms
- `get_realm_info` / `update_realm_settings` - Realm configuration
- `get_realm_events_config` / `update_realm_events_config` - Event management
- `add_realm_default_group` / `remove_realm_default_group` - Default settings

### Realm Operations
Complete realm lifecycle management:
- `create_realm` / `delete_realm` - Realm creation and deletion
- `import_realm` / `export_realm` - Full realm import/export
- `partial_import_realm` / `partial_export_realm` - Selective import/export
- `duplicate_realm` - Realm duplication with customization
- `backup_realm` / `restore_realm_backup` - Backup and restore operations

### Client Sessions Management
Session monitoring and control:
- `get_client_sessions` / `get_client_offline_sessions` - Session queries
- `get_client_session_count` / `get_all_client_sessions_summary` - Statistics
- `find_user_sessions_across_clients` / `find_sessions_by_ip` - Session search
- `revoke_user_consent_for_client` / `cleanup_offline_sessions` - Session management
- `get_active_session_statistics` - Comprehensive session analytics

### Authentication Management
Complete authentication flow control:
- `list_authentication_flows` / `get_authentication_flow` - Flow management
- `create_authentication_flow` / `update_authentication_flow` - Flow CRUD operations
- `delete_authentication_flow` / `copy_authentication_flow` - Flow modifications
- `get_flow_executions` / `update_flow_executions` - Execution management
- `create_execution` / `delete_execution` - Execution lifecycle
- `get_authenticator_config` / `create_authenticator_config` - Configuration management
- `get_required_actions` / `update_required_action` - Required actions control

### Events Management
Comprehensive event tracking and auditing:
- `get_user_events` / `clear_user_events` - User event queries and management
- `get_admin_events` / `clear_admin_events` - Admin event queries and management
- `get_events_config` / `update_events_config` - Event configuration
- `enable_user_events` / `enable_admin_events` - Convenience functions
- `get_recent_login_events` / `get_recent_admin_changes` - Quick queries

### Sessions Management
Comprehensive session control and monitoring:
- `get_realm_session_stats` / `get_realm_sessions_summary` - Realm-wide session analytics
- `get_user_session_details` / `logout_user_sessions` - User session management
- `find_user_sessions` / `get_sessions_by_client` - Session search and filtering
- `get_session_configuration` / `update_session_configuration` - Timeout management
- `monitor_active_sessions` / `logout_all_users` - Monitoring and control
- `cleanup_inactive_sessions` - Session maintenance and analysis

### Attack Detection & Brute Force Protection
Advanced security monitoring and threat detection:
- `get_user_brute_force_status` / `clear_user_login_failures` - User lockout management
- `configure_brute_force_protection` / `get_brute_force_configuration` - Protection settings
- `monitor_failed_login_attempts` / `get_failed_login_events` - Attack monitoring
- `analyze_brute_force_patterns` / `get_brute_force_statistics` - Pattern analysis
- `enable_brute_force_protection` / `get_security_monitoring_summary` - Security overview

### Keys & Certificate Management
Cryptographic keys and certificate operations:
- `get_realm_keys` / `get_realm_certificates` - Key and certificate inventory
- `analyze_key_security` / `monitor_key_expiration` - Security analysis
- `get_key_providers` / `get_signing_algorithms` - Provider and algorithm management
- `rotate_realm_keys` / `export_realm_certificate` - Key rotation and export
- `get_client_certificates` / `validate_certificate_chain` - Certificate validation
- `get_keys_summary` / `get_comprehensive_keys_report` - Comprehensive reporting

### Security Policies & Configuration
Complete security policy management:
- `get_password_policy` / `update_password_policy` - Password policy configuration
- `get_otp_policy` / `update_otp_policy` - OTP policy management
- `get_webauthn_policy` / `update_webauthn_policy` - WebAuthn policy configuration
- `get_browser_security_headers` / `update_browser_security_headers` - Browser security
- `get_smtp_configuration` / `update_smtp_configuration` / `test_smtp_connection` - SMTP setup
- `get_realm_security_settings` / `update_realm_security_settings` - Realm security
- `get_realm_attributes` / `update_realm_attributes` - Custom attributes
- `get_comprehensive_security_summary` - Complete security overview

### Organization Management
Multi-tenant organization lifecycle and domain management:
- `create_organization` / `list_organizations` / `get_organization` - Organization CRUD operations
- `update_organization` / `delete_organization` / `search_organizations` - Organization management
- `list_organization_members` / `add_organization_member` / `remove_organization_member` - Member management
- `get_organization_member` - Member details retrieval
- `list_organization_domains` / `add_organization_domain` / `remove_organization_domain` - Domain management
- `verify_organization_domain` - Domain verification for automatic user assignment
- `list_organization_identity_providers` / `link_organization_identity_provider` - Identity provider linking
- `unlink_organization_identity_provider` / `get_organization_identity_provider` - Provider management
- `get_organization_summary` - Comprehensive organization analytics and overview

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

The project includes a comprehensive test suite with 141 integration tests covering all tool categories. For detailed information, see [tests/README.md](tests/README.md).

### Prerequisites

1. **Keycloak Server** - You need a running Keycloak server:
   ```bash
   # Quick start with Docker
   docker run -p 8080:8080 \
     -e KEYCLOAK_ADMIN=admin \
     -e KEYCLOAK_ADMIN_PASSWORD=admin \
     quay.io/keycloak/keycloak:latest start-dev
   ```

2. **Environment Configuration** - Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your Keycloak credentials
   ```

3. **Install Dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or with pip
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_user_management.py -v

# Run with coverage
uv run pytest --cov=src tests/

# Skip integration tests (for quick checks)
uv run pytest -m "not integration"
```

### Test Coverage

All tool categories have comprehensive test coverage:
- ✅ User Management (9 tests)
- ✅ Client Management (9 tests)
- ✅ Role Management (5 tests)
- ✅ Group Management (7 tests)
- ✅ Realm Administration (7 tests)
- ✅ Realm Operations (15 tests)
- ✅ Authentication Management (10 tests)
- ✅ Identity Providers (6 tests)
- ✅ Events Management (14 tests)
- ✅ Sessions Management (9 tests)
- ✅ Attack Detection (6 tests)
- ✅ Keys Management (11 tests)
- ✅ Security Policies (16 tests)
- ✅ Organization Management (8 tests)
- ✅ Client Scopes (4 tests)
- ✅ Protocol Mappers (4 tests)

**Total: 141 tests across 16 test files**

For troubleshooting, detailed setup instructions, and contribution guidelines, see [tests/README.md](tests/README.md).

## Requirements

- Python 3.8 or higher
- Keycloak server (tested with Keycloak 18+)
- Admin access to Keycloak realm

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/idoyudha/mcp-keycloak).

## Reference
- [Keycloak Admin REST API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak Admin REST API OpenAPI Spec](https://www.keycloak.org/docs-api/latest/rest-api/openapi.yaml)
- [Keycloak Documentation](https://www.keycloak.org/documentation)