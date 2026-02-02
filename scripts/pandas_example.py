#!/usr/bin/env python3
"""
Simple pandas connection example.
This is the refactored version of the original fabric_lakehouse_pandas.py
"""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from knauf_darc_connector.auth import get_azure_credential
from knauf_darc_connector.connectors import FabricLakehouseConnector


def main():
    """Main execution function."""
    # Database connection details
    sql_endpoint = "smacbln2btfurgctc35vgnkkju-p45cayxjodjedixrvld7zyrlla.datawarehouse.fabric.microsoft.com"
    database = "silver"
    
    try:
        # Alternative way: manually get credential and pass it
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential()  # Use your authentication mechanism of choice
        
        connector = FabricLakehouseConnector(sql_endpoint, database, credential)
        
        with connector:
            query = "SELECT TOP 100 * FROM dbo.orders"
            df = connector.execute_query(query)
            print(df)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())