# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides a natural language interface for managing Keycloak identity and access management through its REST API. The server is built with FastMCP and supports both stdio and HTTP transports.

## Development Commands

### Running the Server

```bash
# Start in stdio mode (default, for local CLI tools)
uv run python -m src
# Or using the script:
./scripts/run_server.sh

# Start in HTTP mode (for network access and multiple clients)
TRANSPORT=http uv run python -m src
# Or using the script:
./scripts/run_server.sh http

# HTTP mode on custom port
TRANSPORT=http PORT=8080 uv run python -m src
# Or:
PORT=8080 ./scripts/run_server.sh http
```

### Code Quality

```bash
# Fix formatting issues with ruff
uv run ruff format .
# Or using the script:
./scripts/fix_lint.sh

# Check and fix linting issues
uv run ruff check --fix .
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_connection.py

# Skip integration tests
uv run pytest -m "not integration"
```

### Development Setup

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Keycloak server details
```

## Architecture

### Core Components

**FastMCP Server** (`src/common/server.py`): The MCP server instance is initialized as a singleton using FastMCP. This server object is imported by all tool modules to register their functions.

**KeycloakClient** (`src/tools/keycloak_client.py`): Centralized HTTP client that handles:
- OAuth2 authentication using password grant (admin-cli client)
- Automatic token refresh on 401 responses
- Request building with proper headers and URL structure
- Connection pooling with httpx AsyncClient

**Tool Modules** (`src/tools/`): Each tool module defines MCP tools using the `@mcp.tool()` decorator:
- `user_tools.py` - User lifecycle management
- `client_tools.py` - OAuth2/OIDC client configuration
- `role_tools.py` - Role-based access control
- `group_tools.py` - Group management
- `realm_tools.py` - Realm administration
- `authentication_management_tools.py` - Authentication flow management

### Transport Modes

The server supports two transport modes configured via the `TRANSPORT` environment variable:

**Stdio Mode (default)**: For local CLI integration (e.g., Claude Desktop). The server communicates via standard input/output.

**HTTP Mode**: Runs a web server on `127.0.0.1:8000` (configurable via `PORT`). Implements:
- Streamable HTTP transport following MCP specification
- Origin header validation to prevent DNS rebinding attacks
- CORS middleware for browser-based clients
- Localhost-only binding for security

### Configuration

Environment variables are loaded from `.env` file via `src/common/config.py`:
- `SERVER_URL` - Keycloak server URL (required)
- `USERNAME` - Admin username (required)
- `PASSWORD` - Admin password (required)
- `REALM_NAME` - Target realm (defaults to "master")
- `CLIENT_ID` - Optional OAuth2 client ID
- `CLIENT_SECRET` - Optional OAuth2 client secret
- `TRANSPORT` - "stdio" or "http" (defaults to "stdio")
- `PORT` - HTTP server port (defaults to 8000)

### Entry Points

**CLI Entry Point** (`pyproject.toml`): The package is installable via pip and provides the `mcp-keycloak` command that maps to `mcp_keycloak.main:main`.

**Module Entry Point** (`src/__main__.py`): Allows running as `python -m src` which delegates to the main function.

**Main Function** (`src/main.py`): Imports all tool modules to register them with the MCP server, configures logging, sets up middleware for HTTP mode, and runs the appropriate transport.

## Development Guidelines

### Adding New Tools

1. Create tool function in the appropriate module under `src/tools/`
2. Use the `@mcp.tool()` decorator from `src/common/server.py`
3. Follow naming convention: `verb_noun` (e.g., `create_user`, `list_clients`)
4. Use the shared `KeycloakClient` instance for API calls
5. Accept optional `realm` parameter for cross-realm operations
6. Add comprehensive docstrings with Args and Returns sections
7. Handle errors with clear messages

Example:
```python
from ..common.server import mcp
from .keycloak_client import KeycloakClient

client = KeycloakClient()

@mcp.tool()
async def example_tool(
    param1: str,
    param2: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool description.

    Args:
        param1: Description
        param2: Optional description
        realm: Target realm (uses default if not specified)

    Returns:
        Description of return value
    """
    return await client._make_request("GET", "/endpoint", realm=realm)
```

### KeycloakClient Request Patterns

The `_make_request` method handles URL construction:
- Default: `/auth/admin/realms/{realm}{endpoint}`
- With `skip_realm=True`: `/auth/admin{endpoint}`
- The `realm` parameter overrides the configured default realm

All tool functions should accept an optional `realm` parameter and pass it to `_make_request` to allow cross-realm operations.

### Tool Organization

Tools are organized by functional domain:
- User management: CRUD operations, sessions, password resets
- Client management: OAuth2/OIDC client configuration
- Role management: Realm and client-specific roles
- Group management: Hierarchical organization
- Realm management: System-wide settings
- Authentication management: Flow and execution configuration

### Testing Approach

Tests are pytest-based with fixtures for common setup. Integration tests are marked with `@pytest.mark.integration` and can be skipped with `-m "not integration"`.

#### Testing Requirements and Quality Standards

**Critical Testing Flow:**
1. **100% Pass Rate Required**: All tests must pass completely. Skipped tests are acceptable, but failing tests must be fixed.
2. **Run Tests Twice**: Always run test suites twice to verify:
   - Consistent idempotent results
   - Proper cleanup with no test data pollution
   - Tests can run multiple times without conflicts
3. **Handle Warnings**: If tests complete with warnings, fix them with best effort to maintain code quality.

**Example Testing Flow:**
```bash
# Run tests twice to verify consistency
uv run pytest tests/test_new_feature.py -v
uv run pytest tests/test_new_feature.py -v

# Both runs should show identical results:
# ============================= 14 passed in 3.03s ==============================
# ============================= 14 passed in 2.94s ==============================
```

**Test Fixture Best Practices:**
- Use module-level fixtures (`scope="module"`) with proper cleanup
- Make fixtures idempotent (check if resources exist before creating)
- Always clean up test artifacts in fixture teardown
- Track created resources for guaranteed cleanup
- Avoid class-based setup/teardown (use pytest fixtures instead)

**Test Data Cleanup Verification:**
```bash
# After test runs, verify no pollution
uv run python check_cleanup.py

# Should show:
# [OK] No test organizations remaining (cleanup successful!)
# [OK] No test users remaining (cleanup successful!)
```

For manual testing, use a local Keycloak instance:
```bash
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:latest start-dev
```

## Git Commit Guidelines

When creating git commits, use standard commit messages without attribution to external tools:

```bash
git commit -m "Add organization management features

- Implement complete organization CRUD operations
- Add domain verification and member management
- Include comprehensive integration tests
- Update documentation and roadmap"
```

Do NOT include attribution lines like:
- "Generated with [Claude Code](https://claude.ai/code)"
- "via [Happy](https://happy.engineering)"
- "Co-Authored-By: Claude <noreply@anthropic.com>"
- "Co-Authored-By: Happy <yesreply@happy.engineering>"

Keep commit messages focused on the technical changes and their business value.

## Important Notes

- Python 3.12+ required
- The project uses `uv` for package management (fast, modern alternative to pip)
- Code formatting follows Ruff defaults (88 character line length)
- All API requests use async/await patterns with httpx
- FastMCP automatically handles MCP protocol details (JSON-RPC, SSE streaming)
- The server binds to localhost only for security (use reverse proxy for production)
