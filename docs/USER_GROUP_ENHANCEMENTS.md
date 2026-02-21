# User and Group Enhancement Documentation

This document describes the enhanced functionality added to user and group management tools based on the Keycloak REST API capabilities.

## User Tool Enhancements

### Enhanced list_users Function

The `list_users` function now supports advanced filtering and search options:

#### New Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `exact` | bool | Exact matching for username, email, firstName, lastName | `exact=True` |
| `first_name` | str | Filter by first name | `first_name="John"` |
| `last_name` | str | Filter by last name | `last_name="Doe"` |
| `email_verified` | bool | Filter by email verification status | `email_verified=True` |
| `q` | str | Query for custom attributes | `q="department:Engineering"` |
| `idp_alias` | str | Filter by identity provider alias | `idp_alias="google"` |
| `idp_user_id` | str | Filter by identity provider user ID | `idp_user_id="123456"` |
| `brief_representation` | bool | Return only id and username | `brief_representation=True` |

#### Usage Examples

```python
# Exact username match
users = await list_users(username="johndoe", exact=True)

# Search by name with exact matching
users = await list_users(
    first_name="John",
    last_name="Doe",
    exact=True
)

# Filter by email verification
verified_users = await list_users(email_verified=True)

# Search by custom attributes
engineers = await list_users(q="department:Engineering team:Backend")

# Get brief representation for performance
brief_users = await list_users(brief_representation=True, max=100)

# Filter by identity provider
google_users = await list_users(idp_alias="google")
```

### Enhanced create_user Function

The `create_user` function now supports immediate group and role assignment:

#### New Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `groups` | List[str] | Group names to assign | `groups=["admin", "developers"]` |
| `realm_roles` | List[str] | Realm role names to assign | `realm_roles=["user", "viewer"]` |
| `required_actions` | List[str] | Required actions for the user | `required_actions=["UPDATE_PASSWORD"]` |

#### Available Required Actions

- `VERIFY_EMAIL` - User must verify their email
- `UPDATE_PASSWORD` - User must update their password
- `UPDATE_PROFILE` - User must update their profile
- `CONFIGURE_TOTP` - User must configure two-factor authentication
- `VERIFY_PROFILE` - User must verify their profile
- `terms_and_conditions` - User must accept terms

#### Usage Examples

```python
# Create user with required actions
await create_user(
    username="newuser",
    email="user@example.com",
    required_actions=["VERIFY_EMAIL", "UPDATE_PASSWORD"]
)

# Create user with group assignment
await create_user(
    username="developer",
    email="dev@example.com",
    groups=["developers", "backend-team"]
)

# Create user with role assignment
await create_user(
    username="admin",
    email="admin@example.com",
    realm_roles=["administrator", "user-manager"]
)

# Complete user creation
await create_user(
    username="complete",
    email="complete@example.com",
    first_name="Complete",
    last_name="User",
    enabled=True,
    email_verified=False,
    temporary_password="changeme123",
    groups=["employees"],
    realm_roles=["employee"],
    required_actions=["UPDATE_PASSWORD", "VERIFY_EMAIL"],
    attributes={
        "department": ["Engineering"],
        "employee_id": ["EMP001"]
    }
)
```

### Enhanced update_user Function

The `update_user` function now supports updating groups, roles, and required actions:

#### New Parameters

Same as `create_user` new parameters.

#### Usage Examples

```python
# Update required actions
await update_user(
    user_id="user-uuid",
    required_actions=["CONFIGURE_TOTP"]
)

# Clear all required actions
await update_user(
    user_id="user-uuid",
    required_actions=[]
)

# Update group assignments
await update_user(
    user_id="user-uuid",
    groups=["new-group", "another-group"]
)
```

---

## Group Tool Enhancements

### Enhanced list_groups Function

The `list_groups` function now supports advanced search and hierarchy options:

#### New Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `exact` | bool | Exact matching for search | `exact=True` |
| `q` | str | Query string for groups | `q="type:department"` |
| `brief_representation` | bool | Return brief representation | `brief_representation=True` |
| `populate_hierarchy` | bool | Return groups in hierarchy | `populate_hierarchy=True` |

#### Usage Examples

```python
# Exact group name match
groups = await list_groups(search="developers", exact=True)

# Query groups
dept_groups = await list_groups(q="type:department")

# Get full representation
full_groups = await list_groups(brief_representation=False)

# Get flat list without hierarchy
flat_groups = await list_groups(populate_hierarchy=False)
```

### New Function: list_subgroups

List subgroups of a parent group with pagination and search:

```python
async def list_subgroups(
    group_id: str,
    first: Optional[int] = None,
    max: Optional[int] = None,
    search: Optional[str] = None,
    exact: Optional[bool] = None,
    brief_representation: Optional[bool] = None,
    realm: Optional[str] = None
) -> List[Dict[str, Any]]
```

#### Usage Examples

```python
# Get all subgroups
subgroups = await list_subgroups(group_id="parent-id")

# Search subgroups
teams = await list_subgroups(
    group_id="parent-id",
    search="team"
)

# Paginated subgroups
page1 = await list_subgroups(
    group_id="parent-id",
    first=0,
    max=10
)

# Exact match in subgroups
exact_match = await list_subgroups(
    group_id="parent-id",
    search="exact-name",
    exact=True
)
```

### New Function: create_subgroup

Create a subgroup under a parent group:

```python
async def create_subgroup(
    parent_group_id: str,
    name: str,
    path: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None
) -> Dict[str, str]
```

#### Usage Examples

```python
# Create simple subgroup
await create_subgroup(
    parent_group_id="parent-id",
    name="subteam"
)

# Create subgroup with attributes
await create_subgroup(
    parent_group_id="dept-id",
    name="backend-team",
    attributes={
        "type": ["team"],
        "location": ["NYC"]
    }
)

# Create nested hierarchy
dept_id = "department-id"
team_id_result = await create_subgroup(
    parent_group_id=dept_id,
    name="engineering-team"
)

# Get the created subgroup ID and create another level
teams = await list_subgroups(group_id=dept_id, search="engineering-team")
team_id = teams[0]["id"]

await create_subgroup(
    parent_group_id=team_id,
    name="backend-squad"
)
```

---

## Complete Examples

### Example 1: Advanced User Search

```python
# Find all unverified users from Engineering department
unverified_engineers = await list_users(
    email_verified=False,
    q="department:Engineering"
)

# Find exact user by full name
john_doe = await list_users(
    first_name="John",
    last_name="Doe",
    exact=True
)

# Get brief list for performance
all_users_brief = await list_users(
    brief_representation=True,
    max=1000
)
```

### Example 2: User Onboarding Flow

```python
# Create new employee with complete setup
result = await create_user(
    username="john.smith",
    email="john.smith@company.com",
    first_name="John",
    last_name="Smith",
    enabled=True,
    email_verified=False,
    temporary_password="Welcome123!",
    groups=["employees", "engineering"],
    realm_roles=["employee", "developer"],
    required_actions=["VERIFY_EMAIL", "UPDATE_PASSWORD", "CONFIGURE_TOTP"],
    attributes={
        "department": ["Engineering"],
        "employee_id": ["EMP2024001"],
        "start_date": ["2024-03-01"],
        "manager": ["jane.doe"]
    }
)
```

### Example 3: Group Hierarchy Management

```python
# Create department structure
await create_group(name="Engineering", attributes={"type": ["department"]})
eng_groups = await list_groups(search="Engineering", exact=True)
eng_id = eng_groups[0]["id"]

# Create teams under department
await create_subgroup(parent_group_id=eng_id, name="Backend Team")
await create_subgroup(parent_group_id=eng_id, name="Frontend Team")
await create_subgroup(parent_group_id=eng_id, name="DevOps Team")

# Get all teams
teams = await list_subgroups(group_id=eng_id)

# Create squads under teams
backend_teams = await list_subgroups(group_id=eng_id, search="Backend Team")
backend_id = backend_teams[0]["id"]

await create_subgroup(parent_group_id=backend_id, name="API Squad")
await create_subgroup(parent_group_id=backend_id, name="Database Squad")
```

### Example 4: Bulk User Operations

```python
# Find and update all unverified users
unverified = await list_users(email_verified=False)

for user in unverified:
    # Add email verification requirement
    await update_user(
        user_id=user["id"],
        required_actions=["VERIFY_EMAIL"]
    )

# Find users without 2FA and enforce it
users = await list_users(max=1000)
for user in users:
    user_detail = await get_user(user["id"])
    if not user_detail.get("totp", False):
        await update_user(
            user_id=user["id"],
            required_actions=user_detail.get("requiredActions", []) + ["CONFIGURE_TOTP"]
        )
```

---

## Performance Considerations

### Use Brief Representation

When listing large numbers of users or groups, use `brief_representation=True`:

```python
# Fast - returns only essential fields
brief_users = await list_users(brief_representation=True, max=1000)

# Slower - returns full user objects
full_users = await list_users(brief_representation=False, max=1000)
```

### Use Exact Matching

When you know the exact value, use `exact=True` for better performance:

```python
# More efficient
exact_user = await list_users(username="john.doe", exact=True)

# Less efficient (searches for partial matches)
partial_users = await list_users(username="john.doe")
```

### Paginate Large Results

Always use pagination for large datasets:

```python
# Process users in batches
first = 0
max_per_page = 100

while True:
    users = await list_users(first=first, max=max_per_page)
    if not users:
        break

    # Process batch
    for user in users:
        process_user(user)

    first += max_per_page
```

---

## Migration Guide

### Updating Existing Code

All enhancements are **backward compatible**. Existing code will continue to work without modification:

```python
# Old code - still works
users = await list_users(username="john")

# Enhanced code - more precise
users = await list_users(username="john", exact=True)
```

### Recommended Updates

1. **Add exact matching where appropriate:**
   ```python
   # Before
   users = await list_users(username=username)

   # After (when exact match needed)
   users = await list_users(username=username, exact=True)
   ```

2. **Use required_actions for user lifecycle:**
   ```python
   # Before
   await create_user(username="new", temporary_password="temp")

   # After
   await create_user(
       username="new",
       temporary_password="temp",
       required_actions=["UPDATE_PASSWORD"]
   )
   ```

3. **Leverage group hierarchy:**
   ```python
   # Before (flat groups)
   await create_group(name="team1")

   # After (hierarchical)
   await create_subgroup(parent_group_id=dept_id, name="team1")
   ```

---

## Testing

All enhancements include comprehensive test coverage:

```bash
# Run user tool tests
uv run pytest tests/test_user_tools.py -v

# Run group tool tests
uv run pytest tests/test_group_tools.py -v

# Run all tests
uv run pytest -v
```

Test files:
- `tests/test_user_tools.py` - 19 tests covering all user functionality
- `tests/test_group_tools.py` - 11 tests covering all group functionality

Total: 81 integration tests, all passing.