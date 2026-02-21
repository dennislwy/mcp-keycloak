# Client Tool Enhancements

This document describes the enhanced functionality added to client management tools based on the Keycloak REST API capabilities.

## Overview

The client tools have been enhanced to achieve parity between `create_client` and `update_client`, eliminating the need for two-step client creation. Additionally, `list_clients` now supports advanced filtering options.

## Enhanced create_client Function

### New Parameters

The `create_client` function now includes **9 additional medium-priority parameters**, bringing the total from 16 to 25 parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | None | Base URL for the client |
| `admin_url` | str | None | Admin URL for callbacks and management |
| `client_authenticator_type` | str | "client-secret" | Type of client authenticator (e.g., 'client-secret', 'client-jwt') |
| `full_scope_allowed` | bool | True | Whether client can access all roles (true) or only assigned scopes (false) |
| `consent_required` | bool | False | Whether user consent is required |
| `frontchannel_logout` | bool | False | Enable front-channel logout |
| `attributes` | Dict[str, str] | None | Custom key-value attributes |
| `default_client_scopes` | List[str] | None | List of default client scope names |
| `optional_client_scopes` | List[str] | None | List of optional client scope names |

### Benefits

1. **Single-Step Creation**: Configure clients completely in one operation, no update needed
2. **Enterprise-Ready**: Support for consent, scope management, and custom attributes from creation
3. **Parity with update_client**: Both functions now support the same comprehensive parameter set
4. **Backward Compatible**: All new parameters are optional with sensible defaults

### Usage Examples

#### Basic Client Creation (Unchanged)

```python
# Still works as before - backward compatible
await create_client(
    client_id="my-app",
    name="My Application",
    redirect_uris=["http://localhost:3000/*"]
)
```

#### Single-Step Advanced Configuration

```python
# Before: Required two steps (create + update)
# Now: Single step with all settings

await create_client(
    client_id="enterprise-app",
    name="Enterprise Application",
    description="Production application with full config",

    # URLs
    base_url="https://app.example.com",
    admin_url="https://app.example.com/admin",
    root_url="https://app.example.com",
    redirect_uris=["https://app.example.com/callback"],
    web_origins=["https://app.example.com"],

    # OAuth2/OIDC Settings
    protocol="openid-connect",
    public_client=False,
    standard_flow_enabled=True,
    direct_access_grants_enabled=False,
    service_accounts_enabled=True,

    # Security & Consent
    full_scope_allowed=False,  # Restrict to assigned scopes only
    consent_required=True,     # Require user consent
    client_authenticator_type="client-secret",
    frontchannel_logout=True,

    # Custom Configuration
    attributes={
        "app.environment": "production",
        "app.version": "2.0.0",
        "custom.setting": "enabled"
    },

    # Scopes
    default_client_scopes=["openid", "profile"],
    optional_client_scopes=["email", "address"]
)
```

#### Consent-Required Client

```python
# Create a client that requires user consent
await create_client(
    client_id="third-party-app",
    name="Third Party Integration",
    consent_required=True,
    full_scope_allowed=False,  # Only allow specific scopes
    default_client_scopes=["openid"],
    optional_client_scopes=["email", "profile"]
)
```

#### Client with Custom Attributes

```python
# Create client with custom configuration attributes
await create_client(
    client_id="api-client",
    name="API Client",
    service_accounts_enabled=True,
    attributes={
        "rate.limit.per.minute": "100",
        "api.version": "v2",
        "environment": "staging"
    }
)
```

#### Multi-Tenant Application

```python
# Create client for multi-tenant SaaS with tenant-specific config
await create_client(
    client_id=f"tenant-{tenant_id}",
    name=f"Tenant {tenant_name}",
    base_url=f"https://{tenant_subdomain}.app.com",
    admin_url=f"https://{tenant_subdomain}.app.com/admin",
    redirect_uris=[f"https://{tenant_subdomain}.app.com/*"],
    web_origins=[f"https://{tenant_subdomain}.app.com"],
    attributes={
        "tenant.id": tenant_id,
        "tenant.plan": "enterprise",
        "tenant.created": "2024-03-15"
    }
)
```

---

## Enhanced list_clients Function

### New Parameters

The `list_clients` function now includes **2 additional parameters** for advanced filtering:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | str | None | Query parameter for advanced filtering |
| `search` | bool | False | Whether this is a search query (true) or getClientById query (false) |

### Usage Examples

#### Basic Listing (Unchanged)

```python
# Still works as before
clients = await list_clients(max=10)
```

#### Filter by Client ID

```python
# Partial match
clients = await list_clients(client_id="my-app")

# With search mode
clients = await list_clients(client_id="my-app", search=True)
```

#### Advanced Query

```python
# Query for specific clients
clients = await list_clients(q="production")

# Combine query with pagination
clients = await list_clients(q="api-client", first=0, max=20)
```

#### Paginated Results

```python
# Get first page
page1 = await list_clients(first=0, max=50)

# Get second page
page2 = await list_clients(first=50, max=50)
```

---

## Complete Examples

### Example 1: Enterprise OAuth2 Client

```python
"""
Create a production-ready OAuth2 client with full security configuration.
"""

result = await create_client(
    client_id="enterprise-oauth-client",
    name="Enterprise OAuth Client",
    description="Production OAuth2 client with consent and scope restrictions",
    enabled=True,

    # URLs
    base_url="https://app.company.com",
    admin_url="https://app.company.com/admin",
    root_url="https://app.company.com",
    redirect_uris=[
        "https://app.company.com/callback",
        "https://app.company.com/silent-renew"
    ],
    web_origins=["https://app.company.com"],

    # OAuth2 Flows
    protocol="openid-connect",
    public_client=False,  # Confidential client with secret
    standard_flow_enabled=True,  # Authorization code flow
    direct_access_grants_enabled=False,  # Disable password grant
    implicit_flow_enabled=False,  # Disable implicit flow

    # Security Configuration
    full_scope_allowed=False,  # Only assigned scopes
    consent_required=True,  # Require user consent
    client_authenticator_type="client-secret",
    frontchannel_logout=True,

    # Scopes
    default_client_scopes=["openid", "profile"],
    optional_client_scopes=["email", "address", "phone"],

    # Custom Metadata
    attributes={
        "app.environment": "production",
        "app.owner": "platform-team",
        "compliance.gdpr": "true",
        "support.email": "support@company.com"
    }
)
```

### Example 2: Service Account Client

```python
"""
Create a machine-to-machine client for backend services.
"""

result = await create_client(
    client_id="backend-service",
    name="Backend Service Account",
    description="Service account for automated backend processes",
    enabled=True,

    # Service Account Configuration
    public_client=False,
    service_accounts_enabled=True,
    standard_flow_enabled=False,  # No interactive login
    direct_access_grants_enabled=False,

    # Security
    full_scope_allowed=False,  # Restrict permissions
    consent_required=False,  # No user interaction
    client_authenticator_type="client-secret",

    # Metadata
    attributes={
        "service.type": "automated",
        "service.schedule": "hourly",
        "service.owner": "devops-team"
    }
)
```

### Example 3: Public SPA Client

```python
"""
Create a public client for a Single-Page Application (React, Vue, Angular).
"""

result = await create_client(
    client_id="spa-frontend",
    name="SPA Frontend Application",
    description="Public client for browser-based SPA",
    enabled=True,

    # URLs
    base_url="https://frontend.example.com",
    root_url="https://frontend.example.com",
    redirect_uris=["https://frontend.example.com/*"],
    web_origins=["https://frontend.example.com"],

    # Public Client Configuration
    public_client=True,  # No client secret (browser-based)
    standard_flow_enabled=True,  # Authorization code with PKCE
    implicit_flow_enabled=False,  # Not recommended for SPAs
    direct_access_grants_enabled=False,

    # Security
    full_scope_allowed=True,  # SPA can request any scope
    consent_required=False,
    frontchannel_logout=True,

    # Scopes
    default_client_scopes=["openid", "profile", "email"]
)
```

---

## Migration Guide

### Before and After Comparison

#### Before: Two-Step Client Creation

```python
# Step 1: Create basic client
result = await create_client(
    client_id="my-api",
    redirect_uris=["http://localhost:3000/*"]
)

# Step 2: Update with additional config (requires getting client ID first)
clients = await list_clients(client_id="my-api")
client = clients[0]
await update_client(
    id=client["id"],
    full_scope_allowed=False,
    consent_required=True,
    attributes={"myapp.setting": "value"}
)
```

#### After: Single-Step Client Creation

```python
# Single step with all configuration
result = await create_client(
    client_id="my-api",
    redirect_uris=["http://localhost:3000/*"],
    full_scope_allowed=False,
    consent_required=True,
    attributes={"myapp.setting": "value"}
)
```

### Updating Existing Code

All enhancements are **100% backward compatible**. Existing code will continue to work without modification:

```python
# Old code - still works perfectly
await create_client(
    client_id="legacy-app",
    name="Legacy Application"
)

# Enhanced code - more complete
await create_client(
    client_id="new-app",
    name="New Application",
    full_scope_allowed=False,
    consent_required=True
)
```

### Recommended Updates

1. **Eliminate two-step patterns:**
   ```python
   # Before: create + update
   await create_client(client_id="app")
   await update_client(id=client_id, full_scope_allowed=False)

   # After: single create
   await create_client(client_id="app", full_scope_allowed=False)
   ```

2. **Add consent for third-party clients:**
   ```python
   await create_client(
       client_id="third-party",
       consent_required=True,
       full_scope_allowed=False
   )
   ```

3. **Use custom attributes for metadata:**
   ```python
   await create_client(
       client_id="tracked-app",
       attributes={
           "owner": "team-name",
           "environment": "production",
           "cost-center": "12345"
       }
   )
   ```

---

## Testing

All enhancements include comprehensive test coverage:

```bash
# Run client tool tests
uv run pytest tests/test_client_tools.py -v

# Run all tests
uv run pytest -v
```

Test files:
- `tests/test_client_tools.py` - 11 tests covering all client functionality

Total test coverage:
- Basic CRUD: 2 tests
- Search/Listing: 3 tests
- Enhanced Creation: 5 tests
- Secrets: 1 test

All tests pass with 100% success rate and consistent idempotent results.

---

## Performance Considerations

### Use Specific Filters

```python
# More efficient - specific client_id filter
clients = await list_clients(client_id="exact-name")

# Less efficient - broad search
clients = await list_clients(q="app")
```

### Paginate Large Result Sets

```python
# Process clients in batches
first = 0
max_per_page = 50

while True:
    clients = await list_clients(first=first, max=max_per_page)
    if not clients:
        break

    # Process batch
    for client in clients:
        process_client(client)

    first += max_per_page
```

---

## Comparison with User/Group Tools

| Feature | User Tools | Group Tools | Client Tools |
|---------|-----------|-------------|--------------|
| Advanced search (exact, q) | ✅ Yes | ✅ Yes | ⚠️ Partial (q added, exact N/A) |
| Brief representation | ✅ Yes | ✅ Yes | ❌ Not applicable |
| Complete CRUD parity | ✅ Yes | ✅ Yes | ✅ Yes (NOW ACHIEVED) |
| Custom attributes support | ✅ create & update | ✅ create & update | ✅ create & update (NOW) |
| Lifecycle actions | ✅ required_actions | ✅ subgroups | ✅ scopes |

**Result**: Client tools now have feature parity with user and group tools for creation and configuration.

---

## Backward Compatibility

All enhancements are **100% backward compatible**:
- New parameters are optional with sensible defaults
- Existing code continues to work unchanged
- No breaking changes to function signatures
- Default values match Keycloak defaults

---

## Reference

- [Keycloak ClientRepresentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html#_clientrepresentation)
- [Keycloak Client REST API](https://www.keycloak.org/docs-api/latest/rest-api/index.html#_clients_resource)
