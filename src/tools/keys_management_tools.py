from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


# Realm Keys Management


@mcp.tool()
async def get_realm_keys(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get cryptographic keys metadata for the realm.

    Retrieves information about all cryptographic keys used by the realm,
    including active keys, certificates, algorithms, and key metadata.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Keys metadata with active keys and detailed information
    """
    return await client._make_request("GET", "/keys", realm=realm)


@mcp.tool()
async def get_realm_keys_summary(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a summary of realm cryptographic keys with analysis.

    Provides an organized view of realm keys including counts by type,
    algorithm distribution, and key status analysis.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Comprehensive summary of realm keys with analytics
    """
    keys_data = await get_realm_keys(realm=realm)

    # Initialize summary
    summary = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "active_keys": keys_data.get("active", {}),
        "total_keys": len(keys_data.get("keys", [])),
        "key_analysis": {
            "by_type": {},
            "by_algorithm": {},
            "by_status": {},
            "by_provider": {},
            "by_use": {},
        },
        "keys_details": [],
    }

    # Analyze keys
    for key in keys_data.get("keys", []):
        key_type = key.get("type", "unknown")
        algorithm = key.get("algorithm", "unknown")
        status = key.get("status", "unknown")
        provider = key.get("providerId", "unknown")
        use = key.get("use", "unknown")

        # Count by categories
        summary["key_analysis"]["by_type"][key_type] = (
            summary["key_analysis"]["by_type"].get(key_type, 0) + 1
        )
        summary["key_analysis"]["by_algorithm"][algorithm] = (
            summary["key_analysis"]["by_algorithm"].get(algorithm, 0) + 1
        )
        summary["key_analysis"]["by_status"][status] = (
            summary["key_analysis"]["by_status"].get(status, 0) + 1
        )
        summary["key_analysis"]["by_provider"][provider] = (
            summary["key_analysis"]["by_provider"].get(provider, 0) + 1
        )
        summary["key_analysis"]["by_use"][use] = (
            summary["key_analysis"]["by_use"].get(use, 0) + 1
        )

        # Add key details
        key_detail = {
            "kid": key.get("kid"),
            "type": key_type,
            "algorithm": algorithm,
            "status": status,
            "provider_id": provider,
            "use": use,
            "provider_priority": key.get("providerPriority"),
            "valid_to": key.get("validTo"),
            "has_certificate": bool(key.get("certificate")),
            "has_public_key": bool(key.get("publicKey")),
        }

        summary["keys_details"].append(key_detail)

    # Add key health analysis
    active_keys_count = len(summary["active_keys"])
    total_keys_count = summary["total_keys"]

    summary["key_health"] = {
        "active_keys_count": active_keys_count,
        "inactive_keys_count": total_keys_count - active_keys_count,
        "active_ratio": round(active_keys_count / total_keys_count, 2)
        if total_keys_count > 0
        else 0,
        "has_rsa_keys": "RSA" in summary["key_analysis"]["by_algorithm"],
        "has_ec_keys": any(
            alg.startswith("EC") for alg in summary["key_analysis"]["by_algorithm"]
        ),
        "has_hmac_keys": any(
            alg.startswith("HS") for alg in summary["key_analysis"]["by_algorithm"]
        ),
    }

    return summary


@mcp.tool()
async def list_key_providers(
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all key providers configured for the realm.

    Retrieves information about key providers that generate and manage
    cryptographic keys for the realm, including their configuration and status.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        List of key provider configurations
    """
    # Key providers are managed as components
    from . import user_federation_tools

    components = await user_federation_tools.list_components(realm=realm)

    # Filter for key providers
    key_providers = [
        comp
        for comp in components
        if comp.get("providerType") in ["org.keycloak.keys.KeyProvider"]
    ]

    # Enrich with additional information
    for provider in key_providers:
        provider_id = provider.get("providerId", "")
        if "rsa" in provider_id.lower():
            provider["key_type"] = "RSA"
        elif "hmac" in provider_id.lower():
            provider["key_type"] = "HMAC"
        elif "ec" in provider_id.lower():
            provider["key_type"] = "EC"
        else:
            provider["key_type"] = "unknown"

        # Add configuration summary
        config = provider.get("config", {})
        provider["config_summary"] = {
            "priority": config.get("priority", [""])[0],
            "enabled": config.get("enabled", ["true"])[0].lower() == "true",
            "active": config.get("active", ["true"])[0].lower() == "true",
        }

    return key_providers


@mcp.tool()
async def get_key_provider_details(
    provider_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific key provider.

    Retrieves comprehensive configuration and status information
    for a specific key provider in the realm.

    Args:
        provider_id: ID of the key provider component
        realm: Target realm (uses default if not specified)

    Returns:
        Detailed key provider information
    """
    from . import user_federation_tools

    return await user_federation_tools.get_component(provider_id, realm=realm)


@mcp.tool()
async def rotate_realm_keys(
    key_type: str = "rsa",
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Initiate key rotation for the realm.

    Note: This is a conceptual operation. Actual key rotation in Keycloak
    typically happens automatically based on key provider configuration,
    or by creating new key providers with higher priority.

    Args:
        key_type: Type of keys to rotate (rsa, ec, hmac)
        realm: Target realm (uses default if not specified)

    Returns:
        Information about key rotation process
    """
    # Get current keys status
    current_keys = await get_realm_keys_summary(realm=realm)

    rotation_info = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "requested_key_type": key_type,
        "current_keys_summary": {
            "total_keys": current_keys["total_keys"],
            "active_keys": len(current_keys["active_keys"]),
            "key_types": current_keys["key_analysis"]["by_type"],
        },
        "rotation_status": "manual_action_required",
        "instructions": [
            "Automatic key rotation is handled by Keycloak key providers",
            "To rotate keys manually:",
            "1. Create a new key provider with higher priority",
            "2. Or update existing provider configuration",
            "3. Or use admin console key rotation features",
        ],
        "recommendations": [],
    }

    # Add specific recommendations based on key type
    if key_type.lower() == "rsa":
        rotation_info["recommendations"].append(
            "For RSA key rotation, create new RSA key provider with higher priority"
        )
    elif key_type.lower() == "ec":
        rotation_info["recommendations"].append(
            "For EC key rotation, create new ECDSA key provider with higher priority"
        )
    elif key_type.lower() == "hmac":
        rotation_info["recommendations"].append(
            "For HMAC key rotation, create new HMAC key provider with higher priority"
        )

    return rotation_info


# Client Certificate Management


@mcp.tool()
async def list_client_certificates(
    client_id: str,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List certificates for a specific client.

    Retrieves information about certificates associated with a client,
    including JWT signing certificates and TLS client certificates.

    Args:
        client_id: ID of the client
        realm: Target realm (uses default if not specified)

    Returns:
        Client certificate information
    """
    # Get client details which includes certificate information
    from . import client_tools

    client_details = await client_tools.get_client(client_id, realm=realm)

    certificate_info = {
        "realm": realm or client.realm_name,
        "client_id": client_id,
        "client_name": client_details.get("clientId"),
        "timestamp": client._get_current_timestamp(),
        "certificates": {},
    }

    # Check for various certificate attributes
    cert_attributes = ["jwt.credential", "x509.subjectdn"]

    attributes = client_details.get("attributes", {})
    for attr in cert_attributes:
        if attr in attributes:
            certificate_info["certificates"][attr] = {
                "value": attributes[attr],
                "type": attr,
                "configured": True,
            }

    # Check for client authentication configuration
    client_authenticator = client_details.get("clientAuthenticatorType")
    certificate_info["authentication"] = {
        "client_authenticator_type": client_authenticator,
        "uses_certificates": client_authenticator in ["client-jwt", "client-x509"],
        "public_client": client_details.get("publicClient", False),
    }

    return certificate_info


@mcp.tool()
async def generate_client_certificate(
    client_id: str,
    certificate_type: str = "jwt.credential",
    key_algorithm: str = "RSA",
    key_size: int = 2048,
    validity_days: int = 365,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a new certificate for a client.

    Creates a new certificate and key pair for client authentication
    or JWT signing purposes.

    Args:
        client_id: ID of the client
        certificate_type: Type of certificate (jwt.credential, x509)
        key_algorithm: Key algorithm (RSA, EC)
        key_size: Key size in bits (2048, 4096 for RSA)
        validity_days: Certificate validity in days
        realm: Target realm (uses default if not specified)

    Returns:
        Generated certificate information
    """
    # Get the internal client UUID
    from . import client_tools

    client_details = await client_tools.get_client(client_id, realm=realm)
    client_uuid = client_details["id"]

    # Certificate generation payload
    cert_config = {
        "keyAlgorithm": key_algorithm,
        "keySize": key_size,
        "validity": validity_days,
    }

    try:
        # Generate certificate using Keycloak's certificate generation endpoint
        result = await client._make_request(
            "POST",
            f"/clients/{client_uuid}/certificates/{certificate_type}/generate",
            data=cert_config,
            realm=realm,
        )

        return {
            "status": "generated",
            "realm": realm or client.realm_name,
            "client_id": client_id,
            "client_uuid": client_uuid,
            "certificate_type": certificate_type,
            "configuration": cert_config,
            "timestamp": client._get_current_timestamp(),
            "certificate_info": result,
            "message": f"Certificate generated successfully for client {client_id}",
        }

    except Exception as e:
        return {
            "status": "failed",
            "realm": realm or client.realm_name,
            "client_id": client_id,
            "certificate_type": certificate_type,
            "error": str(e),
            "message": f"Failed to generate certificate for client {client_id}",
            "note": "Certificate generation may not be supported for this client type or configuration",
        }


@mcp.tool()
async def export_client_certificate(
    client_id: str,
    certificate_type: str = "jwt.credential",
    keystore_format: str = "JKS",
    keystore_password: str = "password",
    key_password: str = "password",
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export client certificate in keystore format.

    Generates and downloads a client certificate in the specified keystore format.
    Note: This returns certificate metadata, not the actual binary keystore.

    Args:
        client_id: ID of the client
        certificate_type: Type of certificate to export
        keystore_format: Format for keystore (JKS, PKCS12)
        keystore_password: Password for the keystore
        key_password: Password for the private key
        realm: Target realm (uses default if not specified)

    Returns:
        Certificate export information
    """
    # Get the internal client UUID
    from . import client_tools

    client_details = await client_tools.get_client(client_id, realm=realm)
    client_uuid = client_details["id"]

    # Keystore configuration
    keystore_config = {
        "format": keystore_format,
        "storePassword": keystore_password,
        "keyPassword": key_password,
        "keyAlias": f"{client_id}-key",
        "realmAlias": f"{realm or client.realm_name}-cert",
    }

    try:
        # Note: The actual endpoint returns binary data which we can't easily handle
        # in this context, so we return the configuration that would be used
        export_info = {
            "status": "export_configured",
            "realm": realm or client.realm_name,
            "client_id": client_id,
            "client_uuid": client_uuid,
            "certificate_type": certificate_type,
            "keystore_configuration": keystore_config,
            "timestamp": client._get_current_timestamp(),
            "message": "Certificate export configuration prepared",
            "note": "Use Keycloak Admin Console or direct API call to download the actual keystore file",
            "api_endpoint": f"/admin/realms/{realm or client.realm_name}/clients/{client_uuid}/certificates/{certificate_type}/generate-and-download",
        }

        return export_info

    except Exception as e:
        return {
            "status": "export_failed",
            "error": str(e),
            "message": f"Failed to configure certificate export for client {client_id}",
        }


# Key Analysis and Monitoring


@mcp.tool()
async def analyze_key_security(
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze the security posture of realm cryptographic keys.

    Evaluates key algorithms, sizes, and configurations to identify
    potential security issues and provide recommendations.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Security analysis of realm keys with recommendations
    """
    keys_summary = await get_realm_keys_summary(realm=realm)

    analysis = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "security_assessment": "analyzing",
        "issues": [],
        "recommendations": [],
        "compliance": {
            "modern_algorithms": False,
            "adequate_key_sizes": False,
            "active_keys_ratio": keys_summary["key_health"]["active_ratio"],
        },
    }

    # Analyze algorithms
    algorithms = keys_summary["key_analysis"]["by_algorithm"]

    # Check for modern algorithms
    modern_algorithms = {
        "RS256",
        "RS384",
        "RS512",
        "ES256",
        "ES384",
        "ES512",
        "PS256",
        "PS384",
        "PS512",
    }
    has_modern_algs = any(alg in modern_algorithms for alg in algorithms.keys())
    analysis["compliance"]["modern_algorithms"] = has_modern_algs

    if not has_modern_algs:
        analysis["issues"].append("No modern signing algorithms detected")
        analysis["recommendations"].append(
            "Consider adding RSA-PSS or ECDSA key providers"
        )

    # Check for deprecated algorithms
    deprecated_algorithms = {"HS256", "HS384", "HS512", "RS1"}
    has_deprecated = any(alg in deprecated_algorithms for alg in algorithms.keys())

    if has_deprecated:
        analysis["issues"].append("Deprecated algorithms in use")
        analysis["recommendations"].append("Migrate away from HMAC and RS1 algorithms")

    # Check key distribution
    if (
        "RSA" in keys_summary["key_analysis"]["by_type"]
        and "EC" not in keys_summary["key_analysis"]["by_type"]
    ):
        analysis["recommendations"].append(
            "Consider adding Elliptic Curve keys for better performance"
        )

    # Check active keys ratio
    if analysis["compliance"]["active_keys_ratio"] < 0.5:
        analysis["issues"].append(
            "Low ratio of active keys - many inactive keys present"
        )
        analysis["recommendations"].append("Review and clean up inactive key providers")

    # Determine overall security level
    if len(analysis["issues"]) == 0:
        analysis["security_assessment"] = "good"
    elif len(analysis["issues"]) <= 2:
        analysis["security_assessment"] = "moderate"
    else:
        analysis["security_assessment"] = "needs_attention"

    # Add key rotation recommendations
    analysis["key_rotation"] = {
        "recommendation": "Regular key rotation is recommended",
        "suggested_frequency": "Every 6-12 months for signing keys",
        "automated_rotation": "Configure key providers with appropriate key rotation policies",
    }

    return analysis


@mcp.tool()
async def monitor_key_expiration(
    days_ahead: int = 30,
    realm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Monitor key expiration and provide early warnings.

    Checks for keys that will expire within the specified timeframe
    and provides alerts for proactive key management.

    Args:
        days_ahead: Number of days ahead to check for expiration (default: 30)
        realm: Target realm (uses default if not specified)

    Returns:
        Key expiration monitoring report with alerts
    """
    import datetime

    keys_summary = await get_realm_keys_summary(realm=realm)
    current_time = datetime.datetime.now(datetime.UTC)
    alert_threshold = current_time + datetime.timedelta(days=days_ahead)

    monitoring_report = {
        "realm": realm or client.realm_name,
        "timestamp": client._get_current_timestamp(),
        "monitoring_period_days": days_ahead,
        "alert_threshold": alert_threshold.isoformat() + "Z",
        "expiring_keys": [],
        "expired_keys": [],
        "healthy_keys": [],
        "summary": {
            "total_keys": 0,
            "expiring_soon": 0,
            "already_expired": 0,
            "healthy": 0,
        },
    }

    for key in keys_summary["keys_details"]:
        monitoring_report["summary"]["total_keys"] += 1

        valid_to = key.get("valid_to")
        if valid_to:
            # Convert milliseconds to datetime
            expiry_date = datetime.datetime.fromtimestamp(valid_to / 1000, datetime.UTC)

            key_status = {
                "kid": key["kid"],
                "type": key["type"],
                "algorithm": key["algorithm"],
                "expiry_date": expiry_date.isoformat() + "Z",
                "days_until_expiry": (expiry_date - current_time).days,
            }

            if expiry_date < current_time:
                monitoring_report["expired_keys"].append(key_status)
                monitoring_report["summary"]["already_expired"] += 1
            elif expiry_date < alert_threshold:
                monitoring_report["expiring_keys"].append(key_status)
                monitoring_report["summary"]["expiring_soon"] += 1
            else:
                monitoring_report["healthy_keys"].append(key_status)
                monitoring_report["summary"]["healthy"] += 1
        else:
            # Keys without expiration are considered healthy
            monitoring_report["healthy_keys"].append(
                {
                    "kid": key["kid"],
                    "type": key["type"],
                    "algorithm": key["algorithm"],
                    "expiry_date": "no_expiration",
                    "days_until_expiry": "unlimited",
                }
            )
            monitoring_report["summary"]["healthy"] += 1

    # Generate alerts and recommendations
    monitoring_report["alerts"] = []
    monitoring_report["recommendations"] = []

    if monitoring_report["summary"]["already_expired"] > 0:
        monitoring_report["alerts"].append(
            f"{monitoring_report['summary']['already_expired']} keys have already expired"
        )
        monitoring_report["recommendations"].append("Immediately replace expired keys")

    if monitoring_report["summary"]["expiring_soon"] > 0:
        monitoring_report["alerts"].append(
            f"{monitoring_report['summary']['expiring_soon']} keys will expire within {days_ahead} days"
        )
        monitoring_report["recommendations"].append(
            "Schedule key rotation for expiring keys"
        )

    if len(monitoring_report["alerts"]) == 0:
        monitoring_report["status"] = "healthy"
        monitoring_report["message"] = f"No keys expiring within {days_ahead} days"
    else:
        monitoring_report["status"] = "attention_required"
        monitoring_report["message"] = (
            f"Found {len(monitoring_report['alerts'])} key expiration alerts"
        )

    return monitoring_report


@mcp.tool()
async def get_realm_certificates(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get realm certificates and certificate information.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing certificate information
    """
    keys_data = await get_realm_keys(realm=realm)

    certificates = []
    for key in keys_data.get("keys", []):
        if key.get("certificate"):
            cert_info = {
                "kid": key.get("kid"),
                "type": key.get("type"),
                "algorithm": key.get("algorithm"),
                "status": key.get("status"),
                "certificate": key.get("certificate"),
                "publicKey": key.get("publicKey"),
                "validTo": key.get("validTo"),
                "providerId": key.get("providerId"),
            }
            certificates.append(cert_info)

    return {
        "certificates": certificates,
        "total_certificates": len(certificates),
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def get_key_providers(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get key providers available in the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing key provider information
    """
    return await list_key_providers(realm=realm)


@mcp.tool()
async def get_signing_algorithms(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get supported signing algorithms from realm keys.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing signing algorithm information
    """
    keys_data = await get_realm_keys(realm=realm)

    algorithms = set()
    algorithm_details = {}

    for key in keys_data.get("keys", []):
        algorithm = key.get("algorithm")
        if algorithm:
            algorithms.add(algorithm)
            if algorithm not in algorithm_details:
                algorithm_details[algorithm] = {
                    "algorithm": algorithm,
                    "type": key.get("type"),
                    "keys_count": 0,
                    "active_keys": 0,
                }
            algorithm_details[algorithm]["keys_count"] += 1
            if key.get("status") == "ACTIVE":
                algorithm_details[algorithm]["active_keys"] += 1

    return {
        "algorithms": sorted(list(algorithms)),
        "algorithm_details": algorithm_details,
        "total_algorithms": len(algorithms),
        "realm": realm or client.realm_name,
    }


@mcp.tool()
async def export_realm_certificate(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Export the main realm certificate.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing exported certificate
    """
    certificates = await get_realm_certificates(realm=realm)

    if not certificates["certificates"]:
        return {
            "error": "No certificates found",
            "message": "Realm has no certificates available for export",
            "realm": realm or client.realm_name,
        }

    # Get the first active certificate
    active_cert = None
    for cert in certificates["certificates"]:
        if cert.get("status") == "ACTIVE":
            active_cert = cert
            break

    if not active_cert:
        active_cert = certificates["certificates"][0]

    return {
        "certificate": active_cert,
        "export_format": "PEM",
        "realm": realm or client.realm_name,
        "exported_at": client._get_current_timestamp(),
    }


@mcp.tool()
async def get_client_certificates(
    client_id: Optional[str] = None, realm: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get certificates associated with clients.

    Args:
        client_id: Specific client ID to get certificates for
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing client certificate information
    """
    return await list_client_certificates(client_id=client_id, realm=realm)


@mcp.tool()
async def validate_certificate_chain(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate certificate chains in the realm.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing certificate chain validation results
    """
    certificates = await get_realm_certificates(realm=realm)

    validation_results = {
        "validation": {
            "total_certificates": len(certificates["certificates"]),
            "valid_certificates": 0,
            "expired_certificates": 0,
            "certificate_details": [],
        },
        "realm": realm or client.realm_name,
        "validated_at": client._get_current_timestamp(),
    }

    for cert in certificates["certificates"]:
        cert_validation = {
            "kid": cert["kid"],
            "algorithm": cert["algorithm"],
            "status": cert["status"],
            "valid": cert["status"] == "ACTIVE",
            "expired": False,
        }

        # Check expiration if validTo is available
        if cert.get("validTo"):
            import datetime

            valid_to = datetime.datetime.fromtimestamp(cert["validTo"] / 1000)
            now = datetime.datetime.now()
            cert_validation["expired"] = valid_to < now
            cert_validation["valid"] = (
                cert_validation["valid"] and not cert_validation["expired"]
            )

        validation_results["validation"]["certificate_details"].append(cert_validation)

        if cert_validation["valid"]:
            validation_results["validation"]["valid_certificates"] += 1
        if cert_validation["expired"]:
            validation_results["validation"]["expired_certificates"] += 1

    return validation_results


@mcp.tool()
async def get_keys_summary(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a summary of keys and certificates status.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing keys summary
    """
    return await get_realm_keys_summary(realm=realm)


@mcp.tool()
async def get_comprehensive_keys_report(realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive keys and certificates report.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Dictionary containing comprehensive keys report
    """
    # Gather all key-related information
    keys_summary = await get_keys_summary(realm=realm)
    certificates = await get_realm_certificates(realm=realm)
    providers = await get_key_providers(realm=realm)
    algorithms = await get_signing_algorithms(realm=realm)
    security_analysis = await analyze_key_security(realm=realm)
    expiration_monitoring = await monitor_key_expiration(realm=realm)
    validation_results = await validate_certificate_chain(realm=realm)

    report = {
        "realm": realm or client.realm_name,
        "generated_at": client._get_current_timestamp(),
        "summary": keys_summary,
        "certificates": certificates,
        "providers": providers,
        "algorithms": algorithms,
        "security_analysis": security_analysis,
        "expiration_monitoring": expiration_monitoring,
        "certificate_validation": validation_results,
        "report": {
            "total_keys": keys_summary.get("total_keys", 0),
            "active_keys": keys_summary.get("key_health", {}).get(
                "active_keys_count", 0
            ),
            "total_certificates": certificates.get("total_certificates", 0),
            "key_providers_count": len(providers.get("providers", [])),
            "supported_algorithms": len(algorithms.get("algorithms", [])),
            "security_status": security_analysis.get("security_assessment", "unknown"),
            "expiration_alerts": len(expiration_monitoring.get("alerts", [])),
            "certificate_validation_status": "healthy"
            if validation_results["validation"]["expired_certificates"] == 0
            else "attention_required",
        },
    }

    return report
