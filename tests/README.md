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

The test suite contains **141 integration tests** organized into **16 test files**, providing comprehensive coverage of all Keycloak MCP tools. Tests verify functionality against a live Keycloak server.

### Test Philosophy

- **Integration Tests**: All tests interact with a real Keycloak server
- **Isolated**: Each test creates and cleans up its own resources
- **Idempotent**: Tests can be run multiple times safely
- **Comprehensive**: Every tool category from README.md is tested

## Test Structure

### Test Files Organization

```
tests/
├── test_connection.py                      # Basic connectivity (4 tests)
├── test_imports.py                        # Module imports (5 tests)
├── test_user_management.py                # User CRUD operations (9 tests)
├── test_client_management.py              # OAuth2/OIDC clients (9 tests)
├── test_client_scopes.py                  # Scope configuration (4 tests)
├── test_protocol_mappers.py               # Token claim mapping (4 tests)
├── test_role_management.py                # RBAC operations (5 tests)
├── test_group_management.py               # Group hierarchy (7 tests)
├── test_realm_administration.py           # Realm settings (7 tests)
├── test_realm_operations.py               # Import/Export/Backup (15 tests)
├── test_authentication_management.py      # Auth flows (10 tests)
├── test_identity_providers_and_federation.py  # External auth (6 tests)
├── test_events.py                         # Audit logging (14 tests)
├── test_sessions_management.py            # Session control (9 tests)
├── test_attack_detection.py               # Brute force protection (6 tests)
├── test_keys_management.py                # Cryptographic keys (11 tests)
├── test_security_policies.py              # Security configuration (16 tests)
└── test_organization_management.py        # Multi-tenancy (8 tests)
```

### Test Categories

| Category | File | Tests | Focus |
|----------|------|-------|-------|
| **Core Operations** | | | |
| User Management | test_user_management.py | 9 | CRUD, passwords, sessions |
| Client Management | test_client_management.py | 9 | OAuth2/OIDC configuration |
| Role Management | test_role_management.py | 5 | RBAC, assignments |
| Group Management | test_group_management.py | 7 | Hierarchies, memberships |
| **Configuration** | | | |
| Realm Administration | test_realm_administration.py | 7 | Settings, events, defaults |
| Realm Operations | test_realm_operations.py | 15 | Import/Export, backup |
| Client Scopes | test_client_scopes.py | 4 | Reusable scopes |
| Protocol Mappers | test_protocol_mappers.py | 4 | Token customization |
| **Authentication** | | | |
| Authentication Flows | test_authentication_management.py | 10 | Flow configuration |
| Identity Providers | test_identity_providers_and_federation.py | 6 | External auth (Google, OIDC, SAML) |
| **Security** | | | |
| Attack Detection | test_attack_detection.py | 6 | Brute force protection |
| Keys Management | test_keys_management.py | 11 | Certificates, signing |
| Security Policies | test_security_policies.py | 16 | Passwords, OTP, WebAuthn |
| **Monitoring** | | | |
| Events | test_events.py | 14 | Audit logs, tracking |
| Sessions | test_sessions_management.py | 9 | Active sessions, timeouts |
| **Advanced** | | | |
| Organization Management | test_organization_management.py | 8 | Multi-tenancy (Keycloak 23+) |

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
uv run pytest tests/test_user_management.py -v

# Multiple files
uv run pytest tests/test_user_management.py tests/test_role_management.py -v
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

- ✅ User Management - 9 tests
- ✅ Client Management - 9 tests
- ✅ Client Scopes - 4 tests
- ✅ Protocol Mappers - 4 tests
- ✅ Identity Providers - 6 tests
- ✅ User Federation - 3 tests (in test_identity_providers_and_federation.py)
- ✅ Role Management - 5 tests
- ✅ Group Management - 7 tests
- ✅ Realm Administration - 7 tests
- ✅ Realm Operations - 15 tests
- ✅ Client Sessions Management - 4 tests (in test_realm_operations.py)
- ✅ Authentication Management - 10 tests
- ✅ Events Management - 14 tests
- ✅ Sessions Management - 9 tests
- ✅ Attack Detection & Brute Force Protection - 6 tests
- ✅ Keys & Certificate Management - 11 tests
- ✅ Security Policies & Configuration - 16 tests
- ✅ Organization Management - 8 tests

**Total: 141 tests covering 100% of README.md tool categories**

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
