from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Organization CRUD Operations


@mcp.tool()
async def create_organization(
    name: str,
    enabled: bool = True,
    description: Optional[str] = None,
    alias: Optional[str] = None,
    redirect_url: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new organization in the specified realm.

    Creates a new organization with the specified name and configuration.
    Organizations provide multi-tenancy capabilities and can have associated
    domains, members, and identity providers.

    Args:
        name: Name of the organization (required)
        enabled: Whether the organization is enabled (default: True)
        description: Optional description of the organization
        alias: Optional alias for the organization
        redirect_url: Optional redirect URL for the organization
        attributes: Optional additional attributes for the organization
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with organization creation result
    """
    organization_data = {
        "name": name,
        "enabled": enabled,
    }

    if description is not None:
        organization_data["description"] = description
    if alias is not None:
        organization_data["alias"] = alias
    if redirect_url is not None:
        organization_data["redirectUrl"] = redirect_url
    if attributes is not None:
        organization_data["attributes"] = attributes

    result = await client._make_request(
        "POST", "/organizations", data=organization_data, realm=realm
    )

    return {
        "status": "created",
        "name": name,
        "enabled": enabled,
        "message": f"Organization '{name}' created successfully",
        "result": result,
    }


@mcp.tool()
async def list_organizations(
    search: Optional[str] = None,
    exact: bool = False,
    first: int = 0,
    max: int = 20,
    brief_representation: bool = True,
    q: Optional[str] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List organizations in the realm with optional filtering and pagination.

    Retrieves a paginated list of organizations with support for search
    by name, domain, and custom attributes.

    Args:
        search: Search by organization name or domain
        exact: Whether the search must match exactly (default: False)
        first: Pagination offset (default: 0)
        max: Maximum number of results (default: 20)
        brief_representation: Return only basic fields if True (default: True)
        q: Search for custom attributes in format 'key1:value1 key2:value2'
        realm: Target realm (uses default if not specified)

    Returns:
        List of organization objects
    """
    params = {
        "first": first,
        "max": max,
        "briefRepresentation": brief_representation,
        "exact": exact,
    }

    if search is not None:
        params["search"] = search
    if q is not None:
        params["q"] = q

    return await client._make_request(
        "GET", "/organizations", params=params, realm=realm
    )


@mcp.tool()
async def get_organization(
    organization_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific organization.

    Retrieves complete organization information including domains,
    members, identity providers, and attributes.

    Args:
        organization_id: ID of the organization to retrieve
        realm: Target realm (uses default if not specified)

    Returns:
        Organization object with complete details
    """
    return await client._make_request(
        "GET", f"/organizations/{organization_id}", realm=realm
    )


@mcp.tool()
async def update_organization(
    organization_id: str,
    name: Optional[str] = None,
    enabled: Optional[bool] = None,
    description: Optional[str] = None,
    alias: Optional[str] = None,
    redirect_url: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing organization's configuration.

    Updates the specified organization with new configuration values.
    Only provided fields will be updated.

    Args:
        organization_id: ID of the organization to update
        name: New organization name
        enabled: Whether the organization should be enabled
        description: New description
        alias: New alias
        redirect_url: New redirect URL
        attributes: New attributes (replaces existing attributes)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with update result
    """
    # Get current organization data first
    current_org = await get_organization(organization_id, realm=realm)

    # Build update data with only provided values
    update_data = {}

    if name is not None:
        update_data["name"] = name
    if enabled is not None:
        update_data["enabled"] = enabled
    if description is not None:
        update_data["description"] = description
    if alias is not None:
        update_data["alias"] = alias
    if redirect_url is not None:
        update_data["redirectUrl"] = redirect_url
    if attributes is not None:
        update_data["attributes"] = attributes

    # Include required fields from current organization
    update_data["id"] = current_org["id"]

    if not update_data:
        raise ValueError("At least one field must be provided for update")

    await client._make_request(
        "PUT", f"/organizations/{organization_id}", data=update_data, realm=realm
    )

    return {
        "status": "updated",
        "organization_id": organization_id,
        "message": f"Organization {organization_id} updated successfully",
        "updated_fields": list(k for k in update_data.keys() if k != "id"),
    }


@mcp.tool()
async def delete_organization(
    organization_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Delete an organization from the realm.

    Permanently removes the organization and all its associations.
    This action cannot be undone.

    Args:
        organization_id: ID of the organization to delete
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with deletion result
    """
    await client._make_request(
        "DELETE", f"/organizations/{organization_id}", realm=realm
    )

    return {
        "status": "deleted",
        "organization_id": organization_id,
        "message": f"Organization {organization_id} deleted successfully",
    }


# Organization Members Management


@mcp.tool()
async def list_organization_members(
    organization_id: str,
    first: int = 0,
    max: int = 20,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all members of an organization.

    Retrieves a paginated list of users who are members of the organization.

    Args:
        organization_id: ID of the organization
        first: Pagination offset (default: 0)
        max: Maximum number of results (default: 20)
        realm: Target realm (uses default if not specified)

    Returns:
        List of member/user objects
    """
    params = {
        "first": first,
        "max": max,
    }

    return await client._make_request(
        "GET", f"/organizations/{organization_id}/members", params=params, realm=realm
    )


@mcp.tool()
async def add_organization_member(
    organization_id: str,
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Add an existing user as a member to the organization.

    Associates an existing user with the organization. The user must
    already exist in the realm.

    Args:
        organization_id: ID of the organization
        user_id: ID of the user to add as a member
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with member addition result
    """
    await client._make_request(
        "POST",
        f"/organizations/{organization_id}/members",
        data={"id": user_id},
        realm=realm,
    )

    return {
        "status": "member_added",
        "organization_id": organization_id,
        "user_id": user_id,
        "message": f"User {user_id} added as member to organization {organization_id}",
    }


@mcp.tool()
async def remove_organization_member(
    organization_id: str,
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove a user's membership from the organization.

    Breaks the association between the user and organization. The user
    itself may be deleted if membership is managed, otherwise only the
    association is removed.

    Args:
        organization_id: ID of the organization
        user_id: ID of the user to remove from membership
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with member removal result
    """
    await client._make_request(
        "DELETE", f"/organizations/{organization_id}/members/{user_id}", realm=realm
    )

    return {
        "status": "member_removed",
        "organization_id": organization_id,
        "user_id": user_id,
        "message": f"User {user_id} removed from organization {organization_id}",
    }


@mcp.tool()
async def get_organization_member(
    organization_id: str,
    user_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific organization member.

    Retrieves user information for a specific member of the organization.

    Args:
        organization_id: ID of the organization
        user_id: ID of the member to retrieve
        realm: Target realm (uses default if not specified)

    Returns:
        Member/user object with details
    """
    return await client._make_request(
        "GET", f"/organizations/{organization_id}/members/{user_id}", realm=realm
    )


# Organization Domains Management


@mcp.tool()
async def list_organization_domains(
    organization_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all domains associated with an organization.

    Retrieves all domains configured for the organization, including
    their verification status.

    Args:
        organization_id: ID of the organization
        realm: Target realm (uses default if not specified)

    Returns:
        List of organization domain objects
    """
    return await client._make_request(
        "GET", f"/organizations/{organization_id}/domains", realm=realm
    )


@mcp.tool()
async def add_organization_domain(
    organization_id: str,
    domain_name: str,
    verified: bool = False,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Add a domain to an organization.

    Associates a domain with the organization. The domain can be marked
    as verified or unverified.

    Args:
        organization_id: ID of the organization
        domain_name: Domain name to add (e.g., 'example.com')
        verified: Whether the domain is verified (default: False)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with domain addition result
    """
    domain_data = {
        "name": domain_name,
        "verified": verified,
    }

    await client._make_request(
        "POST",
        f"/organizations/{organization_id}/domains",
        data=domain_data,
        realm=realm,
    )

    return {
        "status": "domain_added",
        "organization_id": organization_id,
        "domain_name": domain_name,
        "verified": verified,
        "message": f"Domain '{domain_name}' added to organization {organization_id}",
    }


@mcp.tool()
async def remove_organization_domain(
    organization_id: str,
    domain_name: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Remove a domain from an organization.

    Removes the association between a domain and the organization.

    Args:
        organization_id: ID of the organization
        domain_name: Domain name to remove
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with domain removal result
    """
    await client._make_request(
        "DELETE", f"/organizations/{organization_id}/domains/{domain_name}", realm=realm
    )

    return {
        "status": "domain_removed",
        "organization_id": organization_id,
        "domain_name": domain_name,
        "message": f"Domain '{domain_name}' removed from organization {organization_id}",
    }


@mcp.tool()
async def verify_organization_domain(
    organization_id: str,
    domain_name: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Verify a domain for an organization.

    Marks a domain as verified for the organization. This is typically
    done after DNS verification or other domain ownership verification.

    Args:
        organization_id: ID of the organization
        domain_name: Domain name to verify
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with domain verification result
    """
    # Get current domain info
    domains = await list_organization_domains(organization_id, realm=realm)
    target_domain = None
    for domain in domains:
        if domain.get("name") == domain_name:
            target_domain = domain
            break

    if not target_domain:
        raise ValueError(f"Domain '{domain_name}' not found in organization")

    # Update domain to verified status
    domain_data = {
        "name": domain_name,
        "verified": True,
    }

    await client._make_request(
        "PUT",
        f"/organizations/{organization_id}/domains/{domain_name}",
        data=domain_data,
        realm=realm,
    )

    return {
        "status": "domain_verified",
        "organization_id": organization_id,
        "domain_name": domain_name,
        "message": f"Domain '{domain_name}' verified for organization {organization_id}",
    }


# Organization Identity Providers Management


@mcp.tool()
async def list_organization_identity_providers(
    organization_id: str,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all identity providers associated with an organization.

    Retrieves all identity providers configured for the organization.

    Args:
        organization_id: ID of the organization
        realm: Target realm (uses default if not specified)

    Returns:
        List of identity provider objects
    """
    return await client._make_request(
        "GET", f"/organizations/{organization_id}/identity-providers", realm=realm
    )


@mcp.tool()
async def get_organization_identity_provider(
    organization_id: str,
    provider_alias: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific identity provider associated with an organization.

    Retrieves detailed information about an identity provider that is
    associated with the organization.

    Args:
        organization_id: ID of the organization
        provider_alias: Alias of the identity provider
        realm: Target realm (uses default if not specified)

    Returns:
        Identity provider object with details
    """
    return await client._make_request(
        "GET",
        f"/organizations/{organization_id}/identity-providers/{provider_alias}",
        realm=realm,
    )


@mcp.tool()
async def link_organization_identity_provider(
    organization_id: str,
    provider_alias: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Link an existing identity provider to an organization.

    Associates an existing identity provider with the organization.
    The identity provider must already exist in the realm.

    Args:
        organization_id: ID of the organization
        provider_alias: Alias of the identity provider to link
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with linking result
    """
    await client._make_request(
        "POST",
        f"/organizations/{organization_id}/identity-providers",
        data={"alias": provider_alias},
        realm=realm,
    )

    return {
        "status": "provider_linked",
        "organization_id": organization_id,
        "provider_alias": provider_alias,
        "message": f"Identity provider '{provider_alias}' linked to organization {organization_id}",
    }


@mcp.tool()
async def unlink_organization_identity_provider(
    organization_id: str,
    provider_alias: str,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Unlink an identity provider from an organization.

    Removes the association between an identity provider and the organization.
    The identity provider itself is not deleted.

    Args:
        organization_id: ID of the organization
        provider_alias: Alias of the identity provider to unlink
        realm: Target realm (uses default if not specified)

    Returns:
        Status message with unlinking result
    """
    await client._make_request(
        "DELETE",
        f"/organizations/{organization_id}/identity-providers/{provider_alias}",
        realm=realm,
    )

    return {
        "status": "provider_unlinked",
        "organization_id": organization_id,
        "provider_alias": provider_alias,
        "message": f"Identity provider '{provider_alias}' unlinked from organization {organization_id}",
    }


# Convenience and Monitoring Functions


@mcp.tool()
async def get_organization_summary(
    organization_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive summary information about an organization.

    Provides a complete overview including organization details, member count,
    domain count, and associated identity providers.

    Args:
        organization_id: ID of the organization
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive organization summary
    """
    # Get organization details
    org_details = await get_organization(organization_id, realm=realm)

    # Get members count
    try:
        members = await list_organization_members(organization_id, max=1, realm=realm)
        members_count = len(members) if members else 0
    except Exception:
        members_count = 0

    # Get domains
    try:
        domains = await list_organization_domains(organization_id, realm=realm)
        domains_count = len(domains) if domains else 0
        verified_domains = (
            [d for d in domains if d.get("verified", False)] if domains else []
        )
        verified_domains_count = len(verified_domains)
    except Exception:
        domains_count = 0
        verified_domains_count = 0
        domains = []

    # Get identity providers
    try:
        identity_providers = await list_organization_identity_providers(
            organization_id, realm=realm
        )
        identity_providers_count = len(identity_providers) if identity_providers else 0
    except Exception:
        identity_providers_count = 0
        identity_providers = []

    return {
        "organization_id": organization_id,
        "name": org_details.get("name"),
        "enabled": org_details.get("enabled"),
        "description": org_details.get("description"),
        "alias": org_details.get("alias"),
        "summary": {
            "members_count": members_count,
            "domains_count": domains_count,
            "verified_domains_count": verified_domains_count,
            "identity_providers_count": identity_providers_count,
        },
        "domains": domains,
        "identity_providers": [
            {"alias": idp.get("alias"), "providerId": idp.get("providerId")}
            for idp in identity_providers
        ],
        "attributes": org_details.get("attributes", {}),
    }


@mcp.tool()
async def search_organizations(
    query: str,
    search_type: str = "name",
    exact: bool = False,
    max: int = 10,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search for organizations using various criteria.

    Provides flexible search capabilities for finding organizations by
    name, domain, or custom attributes.

    Args:
        query: Search query string
        search_type: Type of search - 'name', 'domain', or 'attributes'
        exact: Whether to use exact matching (default: False)
        max: Maximum number of results (default: 10)
        realm: Target realm (uses default if not specified)

    Returns:
        List of matching organization objects
    """
    if search_type == "attributes":
        # For attribute search, use the 'q' parameter
        return await list_organizations(q=query, exact=exact, max=max, realm=realm)
    else:
        # For name and domain search, use the 'search' parameter
        return await list_organizations(search=query, exact=exact, max=max, realm=realm)
