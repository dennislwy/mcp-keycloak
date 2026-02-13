"""Basic import tests that don't require Keycloak connection"""

import importlib
import pkgutil
from pathlib import Path


def test_can_import_main():
    """Test that we can import the main module"""
    from src.main import OriginValidationMiddleware, main

    assert main is not None
    assert OriginValidationMiddleware is not None


def test_can_import_tools():
    """Test that we can import all tool modules"""
    import src.tools

    tools_path = Path(src.tools.__file__).parent

    # Discover all Python modules in src.tools
    for finder, name, ispkg in pkgutil.iter_modules([str(tools_path)]):
        if not name.startswith("_"):  # Skip __init__ and private modules
            module = importlib.import_module(f"src.tools.{name}")
            assert module is not None, f"Failed to import src.tools.{name}"


def test_can_import_keycloak_client():
    """Test that we can import the Keycloak client"""
    from src.tools.keycloak_client import KeycloakClient

    assert KeycloakClient is not None


def test_can_import_config():
    """Test that we can import the config module"""
    from src.common.config import KEYCLOAK_CFG

    assert KEYCLOAK_CFG is not None
    assert isinstance(KEYCLOAK_CFG, dict)


def test_can_import_server():
    """Test that we can import the server module"""
    from src.common.server import mcp

    assert mcp is not None
