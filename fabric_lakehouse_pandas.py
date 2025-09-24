import os
import struct
from itertools import chain, repeat

import pyodbc
import pandas as pd
from azure.identity import AzureCliCredential

# Set OpenSSL environment variables for macOS compatibility (only needed on macOS)
if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/openssl@3/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
    os.environ['OPENSSL_ROOT_DIR'] = '/opt/homebrew/opt/openssl@3'

credential = AzureCliCredential() # use your authentication mechanism of choice
sql_endpoint = "smacbln2btfurgctc35vgnkkju-p45cayxjodjedixrvld7zyrlla.datawarehouse.fabric.microsoft.com" # copy and paste the SQL endpoint from any of the Lakehouses or Warehouses in your Fabric Workspace
database = "silver" # copy and paste the name of the Lakehouse or Warehouse you want to connect to

connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_endpoint},1433;Database={database};Encrypt=Yes;TrustServerCertificate=No"

token_object = credential.get_token("https://database.windows.net//.default") # Retrieve an access token valid to connect to SQL databases
token_as_bytes = bytes(token_object.token, "UTF-8") # Convert the token to a UTF-8 byte string
encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0)))) # Encode the bytes to a Windows byte string
token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes # Package the token into a bytes object
attrs_before = {1256: token_bytes}  # Attribute pointing to SQL_COPT_SS_ACCESS_TOKEN to pass access token to the driver

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
    # print(f"Data from 'silver.dbo.orders' loaded into pandas DataFrame:")
    # print(f"Shape: {df.shape} (rows, columns)")
    # print(f"\nColumn names: {list(df.columns)}")
    # print(f"\nData types:\n{df.dtypes}")
    #
    # print(f"\nFirst 5 rows:")
    # print(df.head())
    #
    # print(f"\nBasic statistics:")
    # print(df.describe())
    
    # You can now perform pandas operations on the DataFrame
    # For example:
    # print(f"\nDataFrame info:")
    # df.info()
    
    connection.close()
    print("\nConnection closed successfully.")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    print("Make sure you have:")
    print("1. ODBC Driver 18 for SQL Server installed")
    print("2. OpenSSL properly configured")
    print("3. Valid Azure credentials")