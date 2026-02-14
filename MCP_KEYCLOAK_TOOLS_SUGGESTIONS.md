# Keycloak MCP Tools Suggestions

## Implementation Status

**Total Tools:** 31
- ✅ **Implemented:** 31 (100%)
- ✅ **Tested:** 31 (100%)

**Test Coverage:** 53 integration tests across 9 test files (all passing)

**Implementation Date:** 2025-02-14

---

## Client Management
**Tool File:** `client_tools.py`
**Base URL Path:** `/admin/realms/{realm}/clients/{client-uuid}`

| Tool Name                            | Method | Endpoint                                 | Purpose                                        | Implemented | Tested |
| ------------------------------------ | ------ | ---------------------------------------- | ---------------------------------------------- | ----------- | ------ |
| `list_client_default_client_scopes`  | GET    | `/default-client-scopes`                 | List default client scopes for a client        | ✅           | ⏳      |
| `update_client_default_client_scope` | PUT    | `/default-client-scopes/{clientScopeId}` | Update default client scope by ID for a client | ✅           | ⏳      |
| `delete_client_default_client_scope` | DELETE | `/default-client-scopes/{clientScopeId}` | Delete default client scope by ID for a client | ✅           | ⏳      |

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

| Tool Name          | Method | Endpoint            | Purpose                                                                                                                                                                                                | Implemented | Tested |
| ------------------ | ------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ------ |
| `request_token`    | POST   | `/token`            | Request access tokens using various OAuth2 grant types (password, authorization_code, refresh_token, client_credentials)                                                                               | ✅          | ✅     |
| `introspect_token` | POST   | `/token/introspect` | Introspect OAuth2 tokens to validate their active state and retrieve associated metadata (exp, iat, scope, username, client_id, permissions). Compliant with RFC 7662. Requires client authentication. | ✅          | ✅     |

# References
- [Keycloak Admin REST API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak OpenAPI Specification](https://www.keycloak.org/docs-api/latest/rest-api/openapi.json)