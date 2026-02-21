# Keycloak MCP Server - Test Suite Documentation

Comprehensive integration tests for the Keycloak MCP Server covering all tool categories and functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Prerequisites](#prerequisites)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Overview

The test suite provides comprehensive coverage of all Keycloak MCP tools. Tests verify functionality against a live Keycloak server.

### Test Philosophy

- **Integration Tests**: All tests interact with a real Keycloak server
- **Isolated**: Each test creates and cleans up its own resources
- **Idempotent**: Tests can be run multiple times safely
- **Comprehensive**: Every tool category from README.md is tested

## Test Structure

### Test Files Organization

```
tests/
├── test_attack_detection_tools.py          # Attack detection & brute force protection (7 tests)
├── test_client_protocol_mapper_tools.py    # Client protocol mappers (5 tests)
├── test_client_role_mapping_tools.py       # Client role mappings for groups (5 tests)
├── test_client_scope_protocol_mapper_tools.py # Client scope protocol mappers (5 tests)
├── test_client_scope_tools.py              # Client scope management (4 tests)
├── test_client_tools.py                    # Client CRUD & enhanced creation (11 tests)
├── test_connection.py                      # Basic connectivity (4 tests)
├── test_group_tools.py                     # Group management & hierarchy (11 tests)
├── test_imports.py                         # Module imports (5 tests)
├── test_oidc_protocol_tools.py             # OIDC token operations (10 tests)
├── test_role_composites.py                 # Role composite operations (6 tests)
└── test_user_tools.py                      # User management & lifecycle (19 tests)
```

### Test Categories

| Category | File | Tests | Focus |
| -------- | ---- | ----- | ----- |
| **User Management** | `test_user_tools.py` | 19 | User lifecycle, advanced search, required actions, groups/roles |
| **Client Management** | `test_client_tools.py` | 11 | Client CRUD, enhanced creation with 25 params, OAuth2 settings |
| **Group Management** | `test_group_tools.py` | 11 | Group lifecycle, hierarchy, subgroups, advanced search |
| **OIDC Protocol** | `test_oidc_protocol_tools.py` | 10 | Token requests, introspection, grant types |
| **Attack Detection** | `test_attack_detection_tools.py` | 7 | Brute force status, login failure management |
| **Role Composites** | `test_role_composites.py` | 6 | Composite role management, realm/client composites |
| **Client Protocol Mappers** | `test_client_protocol_mapper_tools.py` | 5 | Mapper lifecycle, bulk operations, protocol filtering |
| **Client Role Mappings** | `test_client_role_mapping_tools.py` | 5 | Group role mappings, available/composite roles |
| **Client Scope Mappers** | `test_client_scope_protocol_mapper_tools.py` | 5 | Scope mapper lifecycle, bulk operations |
| **Module Imports** | `test_imports.py` | 5 | Module import verification |
| **Client Scopes** | `test_client_scope_tools.py` | 4 | Client scope CRUD, attributes |
| **Connectivity** | `test_connection.py` | 4 | Server connectivity, authentication |


## Prerequisites

### 1. Keycloak Server

You need a running Keycloak server (version 18+):

**Option A: Docker (Recommended for Testing)**
```bash
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

**Option B: Existing Server**
Use your existing Keycloak installation with admin credentials.

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required
SERVER_URL=http://localhost:8080
USERNAME=admin
PASSWORD=admin
REALM_NAME=master

# Optional (for OAuth2 client authentication)
CLIENT_ID=admin-cli
CLIENT_SECRET=your-secret-here
```

**Important:**
- `SERVER_URL` should NOT include `/auth` - the client adds it automatically
- `USERNAME` and `PASSWORD` must have admin privileges
- `REALM_NAME` is the target realm for operations (usually "master")

### 3. Python Dependencies

```bash
# Install test dependencies
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Running Tests

### Run All Tests

```bash
# Using uv (recommended)
uv run pytest tests/

# Using pytest directly
pytest tests/

# With coverage
uv run pytest --cov=src tests/
```

### Run Specific Test Files

```bash
# Single test file
uv run pytest tests/test_connection.py -v

# Multiple files
uv run pytest tests/test_connection.py tests/test_imports.py -v
```

### Run Specific Tests

```bash
# Specific test class
uv run pytest tests/test_user_management.py::TestUserLifecycle -v

# Specific test method
uv run pytest tests/test_user_management.py::TestUserLifecycle::test_create_and_delete_user -v
```

### Filter by Markers

```bash
# Run only integration tests (all tests are integration tests)
uv run pytest -m integration

# Skip integration tests (for quick smoke tests)
uv run pytest -m "not integration"
```

### Useful Options

```bash
# Verbose output
uv run pytest tests/ -v

# Show print statements
uv run pytest tests/ -v -s

# Stop on first failure
uv run pytest tests/ -x

# Run failed tests from last run
uv run pytest tests/ --lf

# Parallel execution (requires pytest-xdist)
uv run pytest tests/ -n auto
```

## Test Coverage

### Coverage by README.md Tool Categories

All tool categories listed in README.md have comprehensive test coverage:
- ✅ User Management (19 tests) - CRUD, search, lifecycle, required actions
- ✅ Client Management (11 tests) - CRUD, enhanced creation, OAuth2 settings
- ✅ Group Management (11 tests) - Hierarchy, subgroups, advanced search
- ✅ OIDC Protocol (10 tests) - Token operations, grant types
- ✅ Attack Detection (7 tests) - Brute force protection, login failures
- ✅ Role Composites (6 tests) - Composite roles, realm/client
- ✅ Client Protocol Mappers (5 tests) - Mapper lifecycle, bulk operations
- ✅ Client Role Mappings (5 tests) - Group role assignments
- ✅ Client Scope Mappers (5 tests) - Scope mapper operations
- ✅ Module Imports (5 tests) - Import verification
- ✅ Client Scopes (4 tests) - Scope CRUD operations
- ✅ Basic Connectivity (4 tests) - Authentication, server connection

**Total: 92 tests (84 integration tests) covering all major tool categories** (all passing ✅)

### What's Tested

Each test file covers:
- **GET operations**: Retrieving data from Keycloak
- **CREATE operations**: Creating new resources
- **UPDATE operations**: Modifying existing resources
- **DELETE operations**: Removing resources
- **Lifecycle tests**: Complete CRUD workflows with cleanup
- **Error cases**: Permission errors, invalid inputs (where applicable)

## Troubleshooting

### Common Issues

#### 1. Authentication Errors (400/401)

```
httpx.HTTPStatusError: Client error '400 Bad Request'
```

**Causes:**
- Incorrect credentials in `.env`
- Wrong `SERVER_URL` format
- OAuth2 client misconfiguration

**Solutions:**
```bash
# Verify credentials
curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password"

# Check .env file format
cat .env

# Ensure SERVER_URL doesn't include /auth
SERVER_URL=http://localhost:8080  # ✅ Correct
SERVER_URL=http://localhost:8080/auth  # ❌ Wrong
```

#### 2. Permission Errors (403/405)

```
pytest.skip: Realm creation not permitted on this server: 403
```

**Causes:**
- User lacks admin privileges
- Server restricts certain operations

**Solutions:**
- Use master realm admin account
- Some tests gracefully skip when permissions are insufficient
- This is expected behavior for non-master admin users

#### 3. Connection Refused

```
httpx.ConnectError: [Errno 111] Connection refused
```

**Causes:**
- Keycloak server not running
- Wrong SERVER_URL

**Solutions:**
```bash
# Check if Keycloak is running
curl http://localhost:8080/

# Verify port
docker ps | grep keycloak

# Check .env SERVER_URL matches actual server
```

#### 4. Event Loop Errors

```
RuntimeError: Event loop is closed
```

**Cause:**
- pytest-asyncio configuration issue

**Solution:**
Already fixed in `pytest.ini`:
```ini
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
asyncio_default_test_loop_scope = session
```

#### 5. Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Reinstall in development mode
uv sync

# Or with pip
pip install -e .
```

### Test-Specific Issues

#### Realm Operations Tests Skip

Many realm operations tests may skip with:
```
pytest.skip: Realm creation not permitted on this server
```

**Reason:** Realm creation requires master realm admin privileges.

**Solution:** This is expected. Tests verify functionality without requiring destructive operations.

#### Keys Management Test Skips

Some tests may skip with:
```
pytest.skip: Function has compatibility issues
```

**Reason:** Certain key management functions may not be available on all Keycloak versions.

**Solution:** This is expected. Tests gracefully handle version differences.

### Getting Help

1. **Check logs**: Run tests with `-v -s` for verbose output
2. **Verify server**: Ensure Keycloak is accessible and configured correctly
3. **Review .env**: Double-check environment variables
4. **Run subset**: Test with a single file first: `uv run pytest tests/test_connection.py -v`

## Contributing

When adding new tests:

1. **Follow naming convention**: `test_<category>.py`
2. **Use fixtures**: Create reusable test data with unique IDs
3. **Clean up**: Always delete created resources in `finally` blocks
4. **Document**: Add docstrings explaining what each test verifies
5. **Handle errors**: Skip tests gracefully when operations aren't permitted
6. **Be idempotent**: Tests should be runnable multiple times

### Example Test Pattern

```python
import uuid
import pytest

@pytest.fixture
def unique_name():
    """Generate unique resource name."""
    return f"test-resource-{uuid.uuid4().hex[:8]}"

@pytest.mark.integration
class TestResourceManagement:
    """Test resource CRUD operations."""

    async def test_resource_lifecycle(self, unique_name):
        """Test creating, reading, updating, and deleting a resource."""
        resource_id = None

        try:
            # Create
            result = await create_resource(name=unique_name)
            assert result["status"] == "created"
            resource_id = result["id"]

            # Read
            resource = await get_resource(resource_id)
            assert resource["name"] == unique_name

            # Update
            await update_resource(resource_id, name=f"{unique_name}-updated")

            # Verify update
            updated = await get_resource(resource_id)
            assert updated["name"] == f"{unique_name}-updated"

        finally:
            # Clean up
            if resource_id:
                try:
                    await delete_resource(resource_id)
                except Exception:
                    pass  # Ignore cleanup errors
```

## License

Tests are part of the mcp-keycloak project and follow the same MIT license.
