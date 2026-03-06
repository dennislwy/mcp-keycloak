from typing import Any, Dict, List, Optional

from ..common.server import mcp
from .keycloak_client import KeycloakClient

client = KeycloakClient()


@mcp.tool()
async def generate_example_access_token(
    client_id: str,
    user_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an example access token for a user and client, simulating what
    Keycloak would issue for the given scope parameter value.

    Useful for inspecting which claims and role mappings would be included in a
    real access token before issuing one. Reflects all currently effective
    protocol mappers and scope mappings for the client.

    Args:
        client_id: UUID of the client (not clientId, but the internal database UUID)
        user_id: UUID of the user to generate the token for
        scope: Space-separated list of requested scopes (e.g. "openid profile email").
               When omitted the client's full default scope set is used. Note: the
               `audience` parameter within evaluate-scopes is only meaningful for
               token exchange; leave it empty for other grant types.
        realm: Target realm (uses default if not specified)

    Returns:
        AccessToken object containing all claims that would appear in the JWT, e.g.:
        - sub, jti, iss, aud, iat, exp
        - realm_access.roles, resource_access.<client>.roles
        - scope, preferred_username, email, name, given_name, family_name
        - Any custom claims added by protocol mappers
    """
    params: Dict[str, Any] = {"userId": user_id}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/generate-example-access-token",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def generate_example_id_token(
    client_id: str,
    user_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an example ID token for a user and client, simulating what
    Keycloak would issue for the given scope parameter value.

    The ID token contains identity claims about the authenticated user as
    defined by the OpenID Connect specification. Use this to verify that the
    correct profile information and custom claims appear for a given user.

    Args:
        client_id: UUID of the client (internal database UUID)
        user_id: UUID of the user to generate the token for
        scope: Space-separated list of requested scopes. The "openid" scope must
               be included for an ID token to be issued. When omitted the
               client's full default scope set is used.
        realm: Target realm (uses default if not specified)

    Returns:
        IDToken object containing the claims that would appear in the ID JWT, e.g.:
        - sub, iss, aud, iat, exp, auth_time, nonce (if applicable)
        - preferred_username, email, email_verified
        - name, given_name, family_name, middle_name, nickname, profile, picture
        - address, phone_number, birthdate, zoneinfo, locale, updated_at
        - Any custom claims added by protocol mappers
    """
    params: Dict[str, Any] = {"userId": user_id}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/generate-example-id-token",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def generate_example_userinfo(
    client_id: str,
    user_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an example UserInfo response for a user and client, simulating
    what Keycloak would return from the /userinfo endpoint for the given scope.

    The UserInfo endpoint returns claims about the authenticated end-user.
    Mappers configured with "Add to userinfo" will contribute claims here.

    Args:
        client_id: UUID of the client (internal database UUID)
        user_id: UUID of the user to generate the userinfo for
        scope: Space-separated list of requested scopes (e.g. "openid profile email").
               When omitted the client's full default scope set is used.
        realm: Target realm (uses default if not specified)

    Returns:
        UserInfo JSON object containing the claims that would be returned by the
        /userinfo endpoint, e.g.:
        - sub, preferred_username, email, email_verified
        - name, given_name, family_name
        - Any custom attributes mapped via protocol mappers
    """
    params: Dict[str, Any] = {"userId": user_id}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/generate-example-userinfo",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_client_evaluate_scopes_protocol_mappers(
    client_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all effective protocol mappers for a client given a scope parameter value.

    Returns the protocol mappers that would be active when the specified scopes
    are requested. Mappers may come from the client itself or from client scopes
    that are either default or match the requested scope strings.

    Use this to understand exactly which mappers contribute claims to tokens for
    a particular scope combination without having to inspect each scope manually.

    Args:
        client_id: UUID of the client (internal database UUID)
        scope: Space-separated list of requested scopes. When omitted the
               client's full default scope set is used.
        realm: Target realm (uses default if not specified)

    Returns:
        List of ClientScopeEvaluateResource$ProtocolMapperEvaluationRepresentation
        objects, each containing:
        - mapperId: Protocol mapper UUID
        - mapperName: Human-readable name
        - containerId: UUID of the client or client scope owning the mapper
        - containerName: Name of the owning container
        - containerType: "client" or "client-scope"
        - protocolMapper: Protocol mapper provider ID (e.g. "oidc-usermodel-property-mapper")
    """
    params: Dict[str, Any] = {}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/protocol-mappers",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_client_evaluate_scopes_granted_roles(
    client_id: str,
    role_container_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List the roles from a role container (realm or client) that are granted to
    the client given the specified scope parameter value.

    A role is "granted" when it is included in the effective scope mappings for
    the evaluated scopes — meaning it will appear in access token role claims
    (realm_access.roles or resource_access.<client>.roles) for users who hold
    that role.

    Args:
        client_id: UUID of the client being evaluated (internal database UUID)
        role_container_id: UUID of the role container to check:
            - Use the realm name (e.g. "myrealm") to check realm-level roles
            - Use a client UUID to check roles from a specific client
        scope: Space-separated list of requested scopes. When omitted the
               client's full default scope set is used.
        realm: Target realm (uses default if not specified)

    Returns:
        List of RoleRepresentation objects for roles that ARE granted, e.g.:
        - id: Role UUID
        - name: Role name
        - description: Role description
        - composite: Whether the role is composite
        - clientRole: True if it is a client role, False for realm roles
        - containerId: UUID or name of the owning container
    """
    params: Dict[str, Any] = {}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/scope-mappings/{role_container_id}/granted",
        params=params,
        realm=realm,
    )


@mcp.tool()
async def get_client_evaluate_scopes_not_granted_roles(
    client_id: str,
    role_container_id: str,
    scope: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List the roles from a role container (realm or client) that are NOT granted
    to the client given the specified scope parameter value.

    A role is "not granted" when it exists on the role container but is excluded
    from the effective scope mappings for the evaluated scopes — meaning it will
    NOT appear in access token role claims even if the user holds the role.
    Use this to identify scope mapping gaps or overly restrictive scope configurations.

    Args:
        client_id: UUID of the client being evaluated (internal database UUID)
        role_container_id: UUID of the role container to check:
            - Use the realm name (e.g. "myrealm") to check realm-level roles
            - Use a client UUID to check roles from a specific client
        scope: Space-separated list of requested scopes. When omitted the
               client's full default scope set is used.
        realm: Target realm (uses default if not specified)

    Returns:
        List of RoleRepresentation objects for roles that are NOT granted, e.g.:
        - id: Role UUID
        - name: Role name
        - description: Role description
        - composite: Whether the role is composite
        - clientRole: True if it is a client role, False for realm roles
        - containerId: UUID or name of the owning container
    """
    params: Dict[str, Any] = {}
    if scope is not None:
        params["scope"] = scope
    return await client._make_request(
        "GET",
        f"/clients/{client_id}/evaluate-scopes/scope-mappings/{role_container_id}/not-granted",
        params=params,
        realm=realm,
    )
