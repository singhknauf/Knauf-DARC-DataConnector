import os
import struct
from itertools import chain, repeat

import pyodbc
import pandas as pd
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential

# Set OpenSSL environment variables for macOS compatibility (only needed on macOS)
if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/openssl@3/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
    os.environ['OPENSSL_ROOT_DIR'] = '/opt/homebrew/opt/openssl@3'

# Try multiple authentication methods
def get_azure_credential():
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

# Database connection details
sql_endpoint = "smacbln2btfurgctc35vgnkkju-p45cayxjodjedixrvld7zyrlla.datawarehouse.fabric.microsoft.com"
database = "silver"

connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_endpoint},1433;Database={database};Encrypt=Yes;TrustServerCertificate=No"

try:
    # Get Azure credential
    credential = get_azure_credential()
    
    # Get access token
    token_object = credential.get_token("https://database.windows.net//.default")
    token_as_bytes = bytes(token_object.token, "UTF-8")
    encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
    token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
    attrs_before = {1256: token_bytes}
    
    # Connect to database
    connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
    
    print("Connection successful!")
    
    # Use pandas to read data directly from the database
    query = """
        SELECT TOP 100 * FROM dbo.orders
    """
    
    # Load data into pandas DataFrame
    df = pd.read_sql(query, connection)
    
    print(f"Data from 'silver.dbo.orders' loaded into pandas DataFrame:")
    print(f"Shape: {df.shape} (rows, columns)")
    print(f"\nColumn names: {list(df.columns)}")
    print(f"\nData types:\n{df.dtypes}")
    
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    print(f"\nBasic statistics:")
    print(df.describe())
    
    # You can now perform pandas operations on the DataFrame
    # For example:
    print(f"\nDataFrame info:")
    df.info()
    
    connection.close()
    print("\nConnection closed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check Azure authentication (see error message above)")
    print("2. Verify ODBC Driver 18 for SQL Server is installed")
    print("3. Ensure OpenSSL is properly configured")
    print("4. Verify access to the Fabric workspace")