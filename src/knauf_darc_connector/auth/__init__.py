"""
Authentication module for Azure connections.
"""

from .azure_auth import get_azure_credential

__all__ = ["get_azure_credential"]