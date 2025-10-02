import os
import struct
from itertools import chain, repeat

import pyodbc
import pandas as pd

# Set OpenSSL environment variables for macOS compatibility (only needed on macOS)
if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/openssl@3/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
    os.environ['OPENSSL_ROOT_DIR'] = '/opt/homebrew/opt/openssl@3'

# ============================================
# METHOD 1: Use Azure CLI to get token
# ============================================
def get_token_from_cli():
    """Get token using Azure CLI"""
    import subprocess
    import json
    
    try:
        result = subprocess.run(
            ['az', 'account', 'get-access-token', '--resource=https://database.windows.net/'],
            capture_output=True,
            text=True,
            check=True
        )
        token_data = json.loads(result.stdout)
        return token_data['accessToken']
    except Exception as e:
        print(f"Error getting token from Azure CLI: {e}")
        print("Make sure you're logged in: run 'az login' first")
        return None


# ============================================
# METHOD 2: Paste your token directly
# ============================================
def get_token_manual():
    """
    Replace 'YOUR_TOKEN_HERE' with your actual access token.
    You can get this token by:
    1. Running: az account get-access-token --resource=https://database.windows.net/
    2. Or using the browser DevTools method from the guide
    """
    token = "YOUR_TOKEN_HERE"
    
    if token == "YOUR_TOKEN_HERE":
        print("ERROR: Please replace 'YOUR_TOKEN_HERE' with your actual token")
        return None
    
    return token


# ============================================
# METHOD 3: Use MSAL for interactive login
# ============================================
def get_token_from_msal():
    """Get token using MSAL interactive login"""
    try:
        from msal import PublicClientApplication
        
        # Public client ID for Power BI/Fabric
        CLIENT_ID = "ea0616ba-638b-4df5-95b9-636659ae5121"
        AUTHORITY = "https://login.microsoftonline.com/organizations"
        SCOPE = ["https://database.windows.net//.default"]
        
        app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        
        # Try to get token silently first
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPE, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]
        
        # If silent fails, do interactive login
        result = app.acquire_token_interactive(scopes=SCOPE)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            print(f"Error: {result.get('error')}")
            print(f"Description: {result.get('error_description')}")
            return None
            
    except ImportError:
        print("MSAL not installed. Install it with: pip install msal")
        return None
    except Exception as e:
        print(f"Error getting token from MSAL: {e}")
        return None


# ============================================
# Main Connection Code
# ============================================

sql_endpoint = "smacbln2btfurgctc35vgnkkju-p45cayxjodjedixrvld7zyrlla.datawarehouse.fabric.microsoft.com"
database = "silver"

connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_endpoint},1433;Database={database};Encrypt=Yes;TrustServerCertificate=No"

# ============================================
# CHOOSE YOUR TOKEN METHOD HERE:
# ============================================
# Uncomment ONE of these methods:

# Option 1: Get token from Azure CLI (recommended if you have Azure CLI)
token = get_token_from_cli()

# Option 2: Paste your token manually
# token = get_token_manual()

# Option 3: Use MSAL for interactive login (requires: pip install msal)
# token = get_token_from_msal()

# ============================================

if not token:
    print("Failed to obtain token. Exiting.")
    exit(1)

print("Token obtained successfully!")
print(f"Token preview: {token[:50]}..." if len(token) > 50 else f"Token: {token}")

# Convert token to the format required by pyodbc
token_as_bytes = bytes(token, "UTF-8")
encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
attrs_before = {1256: token_bytes}  # SQL_COPT_SS_ACCESS_TOKEN

try:
    connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
    
    print("Connection successful!")
    
    # Use pandas to read data directly from the database
    query = """
        SELECT TOP 100 * FROM dbo.orders
    """
    
    # Load data into pandas DataFrame
    df = pd.read_sql(query, connection)
    print(df)
    
    # Uncomment for more details:
    # print(f"\nData from 'silver.dbo.orders' loaded into pandas DataFrame:")
    # print(f"Shape: {df.shape} (rows, columns)")
    # print(f"\nColumn names: {list(df.columns)}")
    # print(f"\nData types:\n{df.dtypes}")
    # print(f"\nFirst 5 rows:")
    # print(df.head())
    # print(f"\nBasic statistics:")
    # print(df.describe())
    
    connection.close()
    print("\nConnection closed successfully.")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    print("\nTroubleshooting checklist:")
    print("1. ODBC Driver 18 for SQL Server is installed")
    print("2. OpenSSL is properly configured (macOS)")
    print("3. Token is valid and not expired (tokens expire after ~1 hour)")
    print("4. You have access to the Fabric workspace and lakehouse")
    print("5. The SQL endpoint URL is correct")
    print("\nTo get a new token, run one of these commands:")
    print("   az account get-access-token --resource=https://database.windows.net/")
    print("   az login  (if not logged in)")