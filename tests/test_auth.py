"""
Tests for authentication module.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from knauf_darc_connector.auth import get_azure_credential, setup_macos_openssl


class TestAuthentication:
    """Test cases for authentication functions."""
    
    def test_setup_macos_openssl(self):
        """Test macOS OpenSSL environment setup."""
        with patch('os.name', 'posix'), \
             patch('os.uname') as mock_uname, \
             patch.dict(os.environ, {}, clear=True):
            
            mock_uname.return_value = MagicMock()
            mock_uname.return_value.sysname = 'Darwin'
            
            setup_macos_openssl()
            
            assert 'DYLD_LIBRARY_PATH' in os.environ
            assert 'OPENSSL_ROOT_DIR' in os.environ
            assert '/opt/homebrew/opt/openssl@3/lib' in os.environ['DYLD_LIBRARY_PATH']
            assert os.environ['OPENSSL_ROOT_DIR'] == '/opt/homebrew/opt/openssl@3'
    
    def test_get_azure_credential_service_principal(self):
        """Test Service Principal authentication."""
        with patch.dict(os.environ, {
            'AZURE_CLIENT_ID': 'test-client-id',
            'AZURE_CLIENT_SECRET': 'test-client-secret',
            'AZURE_TENANT_ID': 'test-tenant-id'
        }), \
        patch('knauf_darc_connector.auth.azure_auth.ClientSecretCredential') as mock_cred:
            
            credential = get_azure_credential()
            
            mock_cred.assert_called_once_with('test-tenant-id', 'test-client-id', 'test-client-secret')
            assert credential == mock_cred.return_value
    
    def test_get_azure_credential_default(self):
        """Test DefaultAzureCredential authentication."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('knauf_darc_connector.auth.azure_auth.DefaultAzureCredential') as mock_default_cred, \
             patch('knauf_darc_connector.auth.azure_auth.AzureCliCredential'):
            
            # Mock successful token retrieval
            mock_credential = MagicMock()
            mock_default_cred.return_value = mock_credential
            
            credential = get_azure_credential()
            
            assert credential == mock_credential
            mock_credential.get_token.assert_called_with("https://database.windows.net//.default")
    
    def test_get_azure_credential_failure(self):
        """Test authentication failure."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('knauf_darc_connector.auth.azure_auth.DefaultAzureCredential') as mock_default, \
             patch('knauf_darc_connector.auth.azure_auth.AzureCliCredential') as mock_cli:
            
            # Mock all authentication methods to fail
            mock_default.return_value.get_token.side_effect = Exception("Default failed")
            mock_cli.return_value.get_token.side_effect = Exception("CLI failed")
            
            with pytest.raises(Exception) as exc_info:
                get_azure_credential()
            
            assert "No valid Azure authentication method found" in str(exc_info.value)