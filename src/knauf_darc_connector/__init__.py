"""
Knauf DARC Data Connector

A Python package for connecting to Microsoft Fabric Lakehouse with flexible authentication methods.
"""

__version__ = "0.1.0"
__author__ = "Knauf DARC Team"
__email__ = "darc@knauf.com"

from .auth import get_azure_credential
from .connectors import FabricLakehouseConnector

__all__ = [
    "get_azure_credential",
    "FabricLakehouseConnector",
]