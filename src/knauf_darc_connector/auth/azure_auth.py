"""
Azure authentication utilities for Fabric Lakehouse connections.
"""

import os
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential


def setup_macos_openssl():
    """
    Set OpenSSL environment variables for macOS compatibility.
    Only needed on macOS systems.
    """
    if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
        os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/openssl@3/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
        os.environ['OPENSSL_ROOT_DIR'] = '/opt/homebrew/opt/openssl@3'


def get_azure_credential():
    """
    Try multiple authentication methods to get Azure credentials.
    
    Returns:
        Azure credential object that can be used to get access tokens.
        
    Raises:
        Exception: If no valid authentication method is found.
    """
    # Ensure macOS OpenSSL compatibility
    setup_macos_openssl()
    
    # Method 1: Try Service Principal from environment variables
    client_id = os.environ.get('AZURE_CLIENT_ID')
    client_secret = os.environ.get('AZURE_CLIENT_SECRET')
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    
    if client_id and client_secret and tenant_id:
        print("Using Service Principal authentication from environment variables")
        return ClientSecretCredential(tenant_id, client_id, client_secret)
    
    # Method 2: Try DefaultAzureCredential (works with multiple auth methods)
    try:
        print("Trying DefaultAzureCredential...")
        credential = DefaultAzureCredential()
        # Test the credential
        credential.get_token("https://database.windows.net//.default")
        print("Using DefaultAzureCredential")
        return credential
    except Exception as e:
        print(f"DefaultAzureCredential failed: {e}")
    
    # Method 3: Try Azure CLI (if available)
    try:
        print("Trying Azure CLI authentication...")
        credential = AzureCliCredential()
        # Test the credential
        credential.get_token("https://database.windows.net//.default")
        print("Using Azure CLI authentication")
        return credential
    except Exception as e:
        print(f"Azure CLI authentication failed: {e}")
    
    # If all methods fail, provide guidance
    raise Exception("""
    No valid Azure authentication method found. Please use one of these options:
    
    1. Set environment variables for Service Principal:
       export AZURE_CLIENT_ID="your-client-id"
       export AZURE_CLIENT_SECRET="your-client-secret"
       export AZURE_TENANT_ID="your-tenant-id"
    
    2. Install and login with Azure CLI:
       - Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
       - Login: az login
    
    3. Use Managed Identity (if running on Azure)
    """)