"""
Microsoft Fabric Lakehouse connector with flexible authentication.
"""

import os
import struct
from itertools import chain, repeat
from typing import Optional, Dict, Any

import pyodbc
import pandas as pd

from ..auth import get_azure_credential


class FabricLakehouseConnector:
    """
    A connector class for Microsoft Fabric Lakehouse with flexible authentication methods.
    """
    
    def __init__(
        self, 
        sql_endpoint: str, 
        database: str, 
        credential: Optional[Any] = None
    ):
        """
        Initialize the Fabric Lakehouse connector.
        
        Args:
            sql_endpoint: The SQL endpoint for the Fabric Lakehouse
            database: The database name to connect to
            credential: Optional Azure credential object. If None, will use get_azure_credential()
        """
        self.sql_endpoint = sql_endpoint
        self.database = database
        self.credential = credential or get_azure_credential()
        self.connection = None
        
        self.connection_string = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={sql_endpoint},1433;"
            f"Database={database};"
            f"Encrypt=Yes;"
            f"TrustServerCertificate=No"
        )
    
    def _get_connection_attrs(self) -> Dict[int, bytes]:
        """
        Get connection attributes with access token for authentication.
        
        Returns:
            Dictionary with connection attributes for pyodbc.
        """
        token_object = self.credential.get_token("https://database.windows.net//.default")
        token_as_bytes = bytes(token_object.token, "UTF-8")
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        return {1256: token_bytes}  # SQL_COPT_SS_ACCESS_TOKEN
    
    def connect(self) -> None:
        """
        Establish connection to the Fabric Lakehouse.
        
        Raises:
            Exception: If connection fails.
        """
        try:
            attrs_before = self._get_connection_attrs()
            self.connection = pyodbc.connect(self.connection_string, attrs_before=attrs_before)
            print(f"Successfully connected to {self.database} database on {self.sql_endpoint}")
        except Exception as e:
            print(f"Connection failed: {e}")
            print("\nTroubleshooting steps:")
            print("1. Check Azure authentication")
            print("2. Verify ODBC Driver 18 for SQL Server is installed")
            print("3. Ensure OpenSSL is properly configured")
            print("4. Verify access to the Fabric workspace")
            raise
    
    def disconnect(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Connection closed successfully.")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a pandas DataFrame.
        
        Args:
            query: SQL query string to execute
            
        Returns:
            pandas DataFrame with query results
            
        Raises:
            Exception: If connection is not established or query fails
        """
        if not self.connection:
            raise Exception("Not connected to database. Call connect() first.")
        
        try:
            df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            print(f"Query execution failed: {e}")
            raise
    
    def get_table_info(self, table_name: str, schema: str = "dbo") -> None:
        """
        Display information about a table including columns, data types, and basic statistics.
        
        Args:
            table_name: Name of the table to analyze
            schema: Schema name (default: "dbo")
        """
        full_table_name = f"{schema}.{table_name}"
        query = f"SELECT TOP 100 * FROM {full_table_name}"
        
        try:
            df = self.execute_query(query)
            
            print(f"Table information for '{full_table_name}':")
            print(f"Shape: {df.shape} (rows, columns)")
            print(f"\nColumn names: {list(df.columns)}")
            print(f"\nData types:\n{df.dtypes}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nBasic statistics:")
            print(df.describe())
            print(f"\nDataFrame info:")
            df.info()
            
        except Exception as e:
            print(f"Failed to get table info for {full_table_name}: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()