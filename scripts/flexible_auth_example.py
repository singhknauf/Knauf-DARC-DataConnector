#!/usr/bin/env python3
"""
Example script showing flexible authentication with Fabric Lakehouse.
This is the refactored version of the original fabric_lakehouse_flexible_auth.py
"""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from knauf_darc_connector import FabricLakehouseConnector


def main():
    """Main execution function."""
    # Database connection details
    sql_endpoint = "smacbln2btfurgctc35vgnkkju-p45cayxjodjedixrvld7zyrlla.datawarehouse.fabric.microsoft.com"
    database = "silver"
    
    try:
        # Create connector instance
        connector = FabricLakehouseConnector(sql_endpoint, database)
        
        # Use context manager for automatic connection handling
        with connector:
            # Execute query
            query = "SELECT TOP 100 * FROM dbo.orders"
            df = connector.execute_query(query)
            
            print(f"Data from 'silver.dbo.orders' loaded into pandas DataFrame:")
            print(f"Shape: {df.shape} (rows, columns)")
            print(f"\nColumn names: {list(df.columns)}")
            print(f"\nData types:\n{df.dtypes}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nBasic statistics:")
            print(df.describe())
            
            # Alternative: use the convenience method
            # connector.get_table_info("orders")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())