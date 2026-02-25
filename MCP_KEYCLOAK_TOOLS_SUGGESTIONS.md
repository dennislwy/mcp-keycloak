# Keycloak MCP Tools Suggestions

## Implementation Status

**Total Tools:** 47
- ✅ **Implemented:** 47 (100%)
- ✅ **Tested:** 47 (100%)
- 🔧 **Enhanced:** User and Group tools with advanced parameters

**Test Coverage:** 111 integration tests across 12 test files (all passing)

**Implementation Date:** 2025-02-14
**Last Updated:** 2026-02-24
- Added OIDC Protocol tools (5 new tools: userinfo, revoke, logout, certs, discovery)
- Added Client Secret Rotation tools (2 tools)
- Added Attack Detection tools (3 tools)
- Added Client Management Permissions tools (2 tools)
- Enhanced User tools with 9 new parameters
- Enhanced Group tools with 4 new parameters + 2 new hierarchy operations

---

## Client Management
**Tool File:** `client_tools.py`
**Base URL Path:** `/admin/realms/{realm}/clients/{client-uuid}`

| Tool Name                            | Method | Endpoint                                 | Purpose                                                          | Implemented | Tested |
| ------------------------------------ | ------ | ---------------------------------------- | ---------------------------------------------------------------- | ----------- | ------ |
| `get_client_secret`                  | GET    | `/client-secret`                         | Get the current client secret                                    | ✅           | ✅      |
| `regenerate_client_secret`           | POST   | `/client-secret`                         | Generate new secret (rotates old secret if policies configured)  | ✅           | ✅      |
| `get_client_secret_rotated`          | GET    | `/client-secret/rotated`                 | Get the rotated (previous) client secret                         | ✅           | ✅      |
| `delete_client_secret_rotated`       | DELETE | `/client-secret/rotated`                 | Invalidate the rotated client secret                             | ✅           | ✅      |
| `list_client_default_client_scopes`  | GET    | `/default-client-scopes`                 | List default client scopes for a client                          | ✅           | ✅      |
| `update_client_default_client_scope` | PUT    | `/default-client-scopes/{clientScopeId}` | Add default client scope to a client                             | ✅           | ✅      |
| `delete_client_default_client_scope` | DELETE | `/default-client-scopes/{clientScopeId}` | Remove default client scope from a client                        | ✅           | ✅      |
| `get_client_management_permissions`  | GET    | `/management/permissions`                | Get management permissions status for a client                   | ✅           | ✅      |
| `update_client_management_permissions`| PUT   | `/management/permissions`                | Enable/disable fine-grained management permissions               | ✅           | ✅      |

**Notes:**
- **Client secret rotation** preserves the old secret as a "rotated secret" when rotation policies are configured at the realm level. This enables zero-downtime secret rotation by allowing both secrets to work during a transition period.
- **Management permissions** require the `admin-fine-grained-authz` feature to be enabled in Keycloak. When enabled, these tools allow delegating client management to non-admin users through fine-grained authorization.

## Client Protocol Mappers
**Tool File:** `client_protocol_mapper_tools.py`  
**Base URL Path:** `/admin/realms/{realm}/clients/{client-uuid}/protocol-mappers`

| Tool Name                                 | Method | Endpoint               | Purpose                                                 | Implemented | Tested |
| ----------------------------------------- | ------ | ---------------------- | ------------------------------------------------------- | ----------- | ------ |
| `list_client_protocol_mappers`            | GET    | `/models`              | List all mappers for a client                           | ✅           | ✅      |
| `create_client_protocol_mapper`           | POST   | `/models`              | Create mapper for a client                              | ✅           | ✅      |
| `get_client_protocol_mapper`              | GET    | `/models/{id}`         | Get single mapper by ID for a client                    | ✅           | ✅      |
| `update_client_protocol_mapper`           | PUT    | `/models/{id}`         | Update existing mapper by ID for a client               | ✅           | ✅      |
| `delete_client_protocol_mapper`           | DELETE | `/models/{id}`         | Remove mapper by ID for a client                        | ✅           | ✅      |
| `create_client_protocol_mappers_bulk`     | POST   | `/add-models`          | Create multiple mappers for a client                    | ✅           | ✅      |
| `get_client_protocol_mappers_by_protocol` | GET    | `/protocol/{protocol}` | Get mappers by name for a specific protocol on a client | ✅           | ✅      |

## Client Role Mappings
**Tool File:** `client_role_mapping_tools.py`  
**Base URL Path:** `/admin/realms/{realm}/groups/{group-id}/role-mappings/clients/{client-id}`

| Tool Name                             | Method | Endpoint     | Purpose                                                                     | Implemented | Tested |
| ------------------------------------- | ------ | ------------ | --------------------------------------------------------------------------- | ----------- | ------ |
| `list_available_client_role_mappings` | GET    | `/available` | List available client-level roles that can be mapped to the user or group   | ✅           | ✅      |
| `list_composite_client_role_mappings` | GET    | `/composite` | List effective client-level role mappings This recurses any composite roles | ✅           | ✅      |
| `get_client_role_mappings`            | GET    |              | Get client-level role mappings for the user or group, and the app           | ✅           | ✅      |
| `add_client_role_mappings`            | POST   |              | Add client-level roles to the user or group role mapping                    | ✅           | ✅      |
| `delete_client_role_mappings`         | DELETE |              | Delete client-level roles from user or group role mapping                   | ✅           | ✅      |

## Client Scopes
**Tool File:** `client_scope_tools.py`  
**Base URL Path:** `/admin/realms/{realm}/client-scopes`

| Tool Name             | Method | Endpoint             | Purpose                                   | Implemented | Tested |
| --------------------- | ------ | -------------------- | ----------------------------------------- | ----------- | ------ |
| `list_client_scopes`  | GET    |                      | List client scopes belonging to the realm | ✅           | ✅      |
| `create_client_scope` | POST   |                      | Create a new client scope                 | ✅           | ✅      |
| `get_client_scope`    | GET    | `/{client-scope-id}` | Get single client scope by ID             | ✅           | ✅      |
| `update_client_scope` | PUT    | `/{client-scope-id}` | Update existing client scope by ID        | ✅           | ✅      |
| `delete_client_scope` | DELETE | `/{client-scope-id}` | Remove client scope by ID                 | ✅           | ✅      |


## Client Scope Protocol Mappers
**Tool File:** `client_scope_protocol_mapper_tools.py`  
**Base URL Path:** `/admin/realms/{realm}/client-scopes/{client-scope-id}/protocol-mappers`

| Tool Name                                       | Method | Endpoint               | Purpose                                                       | Implemented | Tested |
| ----------------------------------------------- | ------ | ---------------------- | ------------------------------------------------------------- | ----------- | ------ |
| `list_client_scope_protocol_mappers`            | GET    | `/models`              | List all mappers for a client scope                           | ✅           | ✅      |
| `create_client_scope_protocol_mapper`           | POST   | `/models`              | Create mapper for a client scope                              | ✅           | ✅      |
| `get_client_scope_protocol_mapper`              | GET    | `/models/{id}`         | Get single mapper by ID for a client scope                    | ✅           | ✅      |
| `update_client_scope_protocol_mapper`           | PUT    | `/models/{id}`         | Update existing mapper by ID for a client scope               | ✅           | ✅      |
| `delete_client_scope_protocol_mapper`           | DELETE | `/models/{id}`         | Remove mapper by ID for a client scope                        | ✅           | ✅      |
| `create_client_scope_protocol_mappers_bulk`     | POST   | `/add-models`          | Create multiple mappers for a client scope                    | ✅           | ✅      |
| `get_client_scope_protocol_mappers_by_protocol` | GET    | `/protocol/{protocol}` | Get mappers by name for a specific protocol on a client scope | ✅           | ✅      |

## Role Management
**Tool File:** `role_tools.py`  
**Base URL Path:** `/admin/realms/{realm}/roles`

| Tool Name                     | Method | Endpoint                                        | Purpose                                                                | Implemented | Tested |
| ----------------------------- | ------ | ----------------------------------------------- | ---------------------------------------------------------------------- | ----------- | ------ |
| `list_role_composites`        | GET    | `/{role-name}/composites`                       | List composites of the role                                            | ✅           | ✅      |
| `add_role_composites`         | POST   | `/{role-name}/composites`                       | Add a composite to the role                                            | ✅           | ✅      |
| `delete_role_composites`      | DELETE | `/{role-name}/composites`                       | Remove roles from the role's composite                                 | ✅           | ✅      |
| `get_role_composites_realm`   | GET    | `/{role-name}/composites/realm`                 | Get realm-level roles of the role's composite                          | ✅           | ✅      |
| `get_role_composites_clients` | GET    | `/{role-name}/composites/clients/{client-uuid}` | Get client-level roles for the client that are in the role's composite | ✅           | ✅      |

## OIDC Protocol Endpoints
**Tool File:** `oidc_protocol_tools.py`
**Base URL Path:** `/realms/{realm}/protocol/openid-connect`

| Tool Name                    | Method | Endpoint                      | Purpose                                                                                                                                                                                                | Implemented | Tested |
| ---------------------------- | ------ | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ------ |
| `request_token`              | POST   | `/token`                      | Request access tokens using various OAuth2 grant types (password, authorization_code, refresh_token, client_credentials)                                                                               | ✅           | ✅      |
| `introspect_token`           | POST   | `/token/introspect`           | Introspect OAuth2 tokens to validate their active state and retrieve associated metadata (exp, iat, scope, username, client_id, permissions). Compliant with RFC 7662. Requires client authentication. | ✅           | ✅      |
| `get_userinfo`               | GET    | `/userinfo`                   | Get user information from UserInfo endpoint using Bearer token authentication. Returns OIDC standard claims (sub, name, email, etc.)                                                                   | ✅           | ✅      |
| `revoke_token`               | POST   | `/revoke`                     | Revoke OAuth2 tokens (access or refresh tokens) to prevent further use. RFC 7009 compliant. Requires client authentication.                                                                            | ✅           | ✅      |
| `logout`                     | POST   | `/logout`                     | Logout and invalidate user session by revoking refresh token. OIDC logout endpoint.                                                                                                                    | ✅           | ✅      |
| `get_certs`                  | GET    | `/certs`                      | Get JSON Web Key Set (JWKS) for token signature verification. Returns public keys used to sign JWTs.                                                                                                   | ✅           | ✅      |
| `get_openid_configuration`   | GET    | `/.well-known/openid-configuration` | Get OpenID Connect Discovery document with all OIDC endpoints, supported features, and capabilities. Returns issuer, endpoints, grant types, scopes, and algorithms.                                   | ✅           | ✅      |

## General Server Operations
**Tool File:** `general_tools.py`
**Base URL Path:** `/admin/serverinfo`

| Tool Name         | Method | Endpoint | Purpose                                                                                                                                                                                                | Implemented | Tested |
| ----------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ------ |
| `get_server_info` | GET    |          | Get comprehensive Keycloak server information including system info, memory info, profile info, features, themes, providers, protocols, and other server metadata. Server-level endpoint (no realm). | ✅           | ✅      |

## Attack Detection
**Tool File:** `attack_detection_tools.py`
**Base URL Path:** `/admin/realms/{realm}/attack-detection/brute-force`

| Tool Name                     | Method | Endpoint          | Purpose                                                                        | Implemented | Tested |
| ----------------------------- | ------ | ----------------- | ------------------------------------------------------------------------------ | ----------- | ------ |
| `get_user_brute_force_status` | GET    | `/users/{userId}` | Get status of a user in brute force detection (numFailures, disabled, etc.)    | ✅           | ✅      |
| `clear_user_login_failures`   | DELETE | `/users/{userId}` | Clear login failures for a specific user (releases temporarily disabled users) | ✅           | ✅      |
| `clear_all_login_failures`    | DELETE | `/users`          | Clear login failures for all users in the realm (bulk release)                 | ✅           | ✅      |

## User Management Enhancements
**Tool File:** `user_tools.py`  
**Enhanced Parameters for `list_users`:**

| Parameter              | Type | Purpose                                                         | Implemented |
| ---------------------- | ---- | --------------------------------------------------------------- | ----------- |
| `exact`                | bool | Exact matching for username, email, firstName, lastName         | ✅           |
| `first_name`           | str  | Filter by first name                                            | ✅           |
| `last_name`            | str  | Filter by last name                                             | ✅           |
| `email_verified`       | bool | Filter by email verification status                             | ✅           |
| `q`                    | str  | Query for custom attributes (format: 'key1:value1 key2:value2') | ✅           |
| `idp_alias`            | str  | Filter by identity provider alias                               | ✅           |
| `idp_user_id`          | str  | Filter by identity provider user ID                             | ✅           |
| `brief_representation` | bool | Return only id and username                                     | ✅           |

**Enhanced Parameters for `create_user` and `update_user`:**

| Parameter          | Type      | Purpose                                                    | Implemented |
| ------------------ | --------- | ---------------------------------------------------------- | ----------- |
| `groups`           | List[str] | Assign user to groups                                      | ✅           |
| `realm_roles`      | List[str] | Assign realm roles to user                                 | ✅           |
| `required_actions` | List[str] | Set required actions (VERIFY_EMAIL, UPDATE_PASSWORD, etc.) | ✅           |

## Group Management Enhancements
**Tool File:** `group_tools.py`
**Enhanced Parameters for `list_groups`:**

| Parameter              | Type | Purpose                     | Implemented |
| ---------------------- | ---- | --------------------------- | ----------- |
| `exact`                | bool | Exact matching for search   | ✅           |
| `q`                    | str  | Query string for groups     | ✅           |
| `brief_representation` | bool | Return brief representation | ✅           |
| `populate_hierarchy`   | bool | Return groups in hierarchy  | ✅           |

**New Hierarchy Operations:**

| Tool Name         | Method | Purpose                                            | Implemented | Tested |
| ----------------- | ------ | -------------------------------------------------- | ----------- | ------ |
| `list_subgroups`  | GET    | Get paginated list of subgroups for a parent group | ✅           | ✅      |
| `create_subgroup` | POST   | Create a subgroup under a parent group             | ✅           | ✅      |

# References
- [Keycloak Admin REST API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak OpenAPI Specification](https://www.keycloak.org/docs-api/latest/rest-api/openapi.json)