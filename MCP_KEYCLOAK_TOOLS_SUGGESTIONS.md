# Keycloak MCP Tools Suggestions

## Implementation Status

**Total Tools:** 65
- ✅ **Implemented:** 65 (100%)
- ⚠️ **Tested:** 64 (98%) — `exchange_token` pending tests
- 🔧 **Enhanced:** User and Group tools with advanced parameters

**Test Coverage:** 130 integration tests across 13 test files (all passing)

**Implementation Date:** 2025-02-14
**Last Updated:** 2026-03-03
- Added 6 new Realm Administration tools (update_realm_settings expanded, update_realm_settings_advanced, events config CRUD, default group add/remove)
- Added 8 missing Authentication Management tools (required action CRUD, required action config, form providers, per-client config)
- Added OIDC Protocol tools (5 new tools: userinfo, revoke, logout, certs, discovery)
- Documented exchange_token (RFC 8693 Token Exchange, already implemented)
- Added Client Secret Rotation tools (2 tools)
- Added Attack Detection tools (3 tools)
- Added Client Management Permissions tools (2 tools)
- Enhanced User tools with 9 new parameters
- Enhanced Group tools with 4 new parameters + 2 new hierarchy operations

---

## Client Management
**Tool File:** `client_tools.py`
**Base URL Path:** `/admin/realms/{realm}/clients/{client-uuid}`

| Tool Name                              | Method | Endpoint                                        | Purpose                                                                                                                                                          | Implemented | Tested |
| -------------------------------------- | ------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ |
| `get_client_secret`                    | GET    | `/client-secret`                                | Get the current client secret                                                                                                                                    | ✅           | ✅      |
| `regenerate_client_secret`             | POST   | `/client-secret`                                | Generate new secret (rotates old secret if policies configured)                                                                                                  | ✅           | ✅      |
| `get_client_secret_rotated`            | GET    | `/client-secret/rotated`                        | Get the rotated (previous) client secret                                                                                                                         | ✅           | ✅      |
| `delete_client_secret_rotated`         | DELETE | `/client-secret/rotated`                        | Invalidate the rotated client secret                                                                                                                             | ✅           | ✅      |
| `list_client_default_client_scopes`    | GET    | `/default-client-scopes`                        | List default client scopes for a client                                                                                                                          | ✅           | ✅      |
| `update_client_default_client_scope`   | PUT    | `/default-client-scopes/{clientScopeId}`        | Add default client scope to a client                                                                                                                             | ✅           | ✅      |
| `delete_client_default_client_scope`   | DELETE | `/default-client-scopes/{clientScopeId}`        | Remove default client scope from a client                                                                                                                        | ✅           | ✅      |
| `get_client_management_permissions`    | GET    | `/management/permissions`                       | Get management permissions status for a client                                                                                                                   | ✅           | ✅      |
| `update_client_management_permissions` | PUT    | `/management/permissions`                       | Enable/disable fine-grained management permissions                                                                                                               | ✅           | ✅      |
| `add_optional_client_scope`            | PUT    | `/{client-id}/optional-client-scopes/{scopeId}` | Add a client scope to a client's optional scopes. Note: `update_client_advanced` does NOT persist `optionalClientScopes` — this dedicated endpoint must be used. | ✅           | ✅      |
| `delete_optional_client_scope`         | DELETE | `/{client-id}/optional-client-scopes/{scopeId}` | Remove a client scope from a client's optional scopes.                                                                                                           | ✅           | ✅      |
| `list_optional_client_scopes`          | GET    | `/{client-id}/optional-client-scopes`           | List all optional client scopes assigned to a client.                                                                                                            | ✅           | ✅      |

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

| Tool Name                  | Method | Endpoint                            | Purpose                                                                                                                                                                                                | Implemented | Tested |
| -------------------------- | ------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ------ |
| `request_token`            | POST   | `/token`                            | Request access tokens using various OAuth2 grant types (password, authorization_code, refresh_token, client_credentials)                                                                               | ✅           | ✅      |
| `introspect_token`         | POST   | `/token/introspect`                 | Introspect OAuth2 tokens to validate their active state and retrieve associated metadata (exp, iat, scope, username, client_id, permissions). Compliant with RFC 7662. Requires client authentication. | ✅           | ✅      |
| `get_userinfo`             | GET    | `/userinfo`                         | Get user information from UserInfo endpoint using Bearer token authentication. Returns OIDC standard claims (sub, name, email, etc.)                                                                   | ✅           | ✅      |
| `revoke_token`             | POST   | `/revoke`                           | Revoke OAuth2 tokens (access or refresh tokens) to prevent further use. RFC 7009 compliant. Requires client authentication.                                                                            | ✅           | ✅      |
| `logout`                   | POST   | `/logout`                           | Logout and invalidate user session by revoking refresh token. OIDC logout endpoint.                                                                                                                    | ✅           | ✅      |
| `exchange_token`           | POST   | `/token`                            | Exchange an OAuth2 token for another token targeting a different audience/service. RFC 8693 Token Exchange (`grant_type=urn:ietf:params:oauth:grant-type:token-exchange`). Requires the client to have Standard Token Exchange enabled and the subject token to include the client in its audience. | ✅           | ❌      |
| `get_certs`                | GET    | `/certs`                            | Get JSON Web Key Set (JWKS) for token signature verification. Returns public keys used to sign JWTs.                                                                                                   | ✅           | ✅      |
| `get_openid_configuration` | GET    | `/.well-known/openid-configuration` | Get OpenID Connect Discovery document with all OIDC endpoints, supported features, and capabilities. Returns issuer, endpoints, grant types, scopes, and algorithms.                                   | ✅           | ✅      |

## General Server Operations
**Tool File:** `general_tools.py`
**Base URL Path:** `/admin/serverinfo`

| Tool Name         | Method | Endpoint | Purpose                                                                                                                                                                                              | Implemented | Tested |
| ----------------- | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ |
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

## Realm Administration
**Tool File:** `realm_tools.py`
**Base URL Path:** `/admin/realms/{realm}`

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_accessible_realms` | GET | `/realms` | List all accessible realms | ✅ | ✅ |
| `get_realm_info` | GET | `` (realm root) | Get current realm configuration | ✅ | ✅ |
| `update_realm_settings` | PUT | `` (realm root) | Update realm settings (themes, login, brute-force, OTP policy, WebAuthn Passwordless policy, flow bindings) | ✅ | ✅ |
| `update_realm_settings_advanced` | PUT | `` (realm root) | Power-user tool: shallow-merge a raw `RealmRepresentation` dict for full control | ✅ | ❌ |
| `get_realm_events_config` | GET | `/events/config` | Get realm events configuration | ✅ | ❌ |
| `update_realm_events_config` | PUT | `/events/config` | Update event listeners, admin events, enabled event types | ✅ | ❌ |
| `get_realm_default_groups` | GET | `/default-groups` | List default groups assigned to new users | ✅ | ✅ |
| `add_realm_default_group` | PUT | `/default-groups/{group_id}` | Add a group as a realm default group | ✅ | ❌ |
| `remove_realm_default_group` | DELETE | `/default-groups/{group_id}` | Remove a group from realm default groups | ✅ | ❌ |
| `remove_all_user_sessions` | POST | `/logout-all` | Invalidate all active user sessions in the realm | ✅ | ✅ |

**Notes:**
- `update_realm_settings` supports authentication flow bindings (`browserFlow`, `registrationFlow`, etc.), OTP policy, and full WebAuthn Passwordless policy configuration
- `update_realm_settings_advanced` accepts any field from the [RealmRepresentation schema](https://www.keycloak.org/docs-api/latest/rest-api/index.html#RealmRepresentation) and merges it with the current config — use for fields not exposed by `update_realm_settings`
- ❌ `update_realm_settings_advanced`, `get_realm_events_config`, `update_realm_events_config`, `add_realm_default_group`, `remove_realm_default_group` — not yet covered by integration tests

## Authentication Management
**Tool File:** `authentication_management_tools.py`
**Base URL Path:** `/admin/realms/{realm}/authentication`

### Authentication Flows

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `list_authentication_flows` | GET | `/flows` | List all authentication flows in the realm | ✅ | ✅ |
| `get_authentication_flow` | GET | `/flows/{id}` | Get a specific flow by ID | ✅ | ✅ |
| `create_authentication_flow` | POST | `/flows` | Create a new authentication flow | ✅ | ✅ |
| `update_authentication_flow` | PUT | `/flows/{id}` | Update an existing flow | ✅ | ✅ |
| `delete_authentication_flow` | DELETE | `/flows/{id}` | Delete a flow | ✅ | ✅ |
| `copy_authentication_flow` | POST | `/flows/{flowAlias}/copy` | Duplicate a flow under a new name | ✅ | ✅ |

### Flow Executions

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_flow_executions` | GET | `/flows/{flowAlias}/executions` | Get executions for a flow | ✅ | ✅ |
| `update_flow_executions` | PUT | `/flows/{flowAlias}/executions` | Update execution ordering/requirements | ✅ | ✅ |
| `add_execution_to_flow` | POST | `/flows/{flowAlias}/executions/execution` | Add an authenticator execution to a flow | ✅ | ✅ |
| `add_subflow_to_flow` | POST | `/flows/{flowAlias}/executions/flow` | Add a nested sub-flow to a flow | ✅ | ✅ |
| `create_execution` | POST | `/executions` | Create a standalone execution | ✅ | ✅ |
| `get_execution` | GET | `/executions/{executionId}` | Get a single execution | ✅ | ✅ |
| `delete_execution` | DELETE | `/executions/{executionId}` | Delete an execution | ✅ | ✅ |
| `raise_execution_priority` | POST | `/executions/{executionId}/raise-priority` | Increase execution priority | ✅ | ✅ |
| `lower_execution_priority` | POST | `/executions/{executionId}/lower-priority` | Decrease execution priority | ✅ | ✅ |
| `get_execution_config` | GET | `/executions/{executionId}/config/{id}` | Get execution configuration | ✅ | ✅ |
| `update_execution_config` | POST | `/executions/{executionId}/config` | Update execution configuration | ✅ | ✅ |

### Authenticator Configuration

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_authenticator_config` | GET | `/config/{id}` | Get authenticator configuration by ID | ✅ | ✅ |
| `create_authenticator_config` | POST | `/config` | Create new authenticator configuration | ✅ | ✅ |
| `update_authenticator_config` | PUT | `/config/{id}` | Update authenticator configuration | ✅ | ✅ |
| `delete_authenticator_config` | DELETE | `/config/{id}` | Delete authenticator configuration | ✅ | ✅ |

### Authenticator Providers

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_authenticator_providers` | GET | `/authenticator-providers` | List all authenticator providers | ✅ | ✅ |
| `get_client_authenticator_providers` | GET | `/client-authenticator-providers` | List client authenticator providers | ✅ | ✅ |
| `get_provider_config_description` | GET | `/config-description/{providerId}` | Get config schema for a specific provider | ✅ | ✅ |

### Required Actions

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_required_actions` | GET | `/required-actions` | List all registered required actions | ✅ | ✅ |
| `get_unregistered_required_actions` | GET | `/unregistered-required-actions` | List unregistered required action providers | ✅ | ✅ |
| `register_required_action` | POST | `/register-required-action` | Register a new required action | ✅ | ✅ |
| `get_required_action` | GET | `/required-actions/{alias}` | Get a specific required action by alias | ✅ | ✅ |
| `update_required_action` | PUT | `/required-actions/{alias}` | Update required action settings | ✅ | ✅ |
| `delete_required_action` | DELETE | `/required-actions/{alias}` | Delete a required action | ✅ | ⚠️ |
| `raise_required_action_priority` | POST | `/required-actions/{alias}/raise-priority` | Raise required action priority | ✅ | ✅ |
| `lower_required_action_priority` | POST | `/required-actions/{alias}/lower-priority` | Lower required action priority | ✅ | ✅ |
| `get_required_action_config_description` | GET | `/required-actions/{alias}/config-description` | Get configuration schema for a required action | ✅ | ✅ |
| `get_required_action_config` | GET | `/required-actions/{alias}/config` | Get current config for a required action | ✅ | ✅ |
| `update_required_action_config` | PUT | `/required-actions/{alias}/config` | Update required action config | ✅ | ⚠️ |
| `delete_required_action_config` | DELETE | `/required-actions/{alias}/config` | Clear required action config | ✅ | ⚠️ |

**Notes:**
- ⚠️ `delete_required_action` — test skips when all available actions are already registered (no unregistered actions to test with)
- ⚠️ `update_required_action_config` / `delete_required_action_config` — test skips when no required action in the realm has a working config write endpoint (some Keycloak builds return 500 for `CONFIGURE_TOTP` config updates)

### Form Providers

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_form_providers` | GET | `/form-providers` | List available form providers | ✅ | ✅ |
| `get_form_action_providers` | GET | `/form-action-providers` | List available form action providers | ✅ | ✅ |

### Per-Client Configuration

| Tool Name | Method | Endpoint | Purpose | Implemented | Tested |
| --- | --- | --- | --- | --- | --- |
| `get_per_client_config_description` | GET | `/per-client-config-description` | Get config schema for per-client authentication | ✅ | ✅ |

# References
- [Keycloak Admin REST API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak OpenAPI Specification](https://www.keycloak.org/docs-api/latest/rest-api/openapi.json)