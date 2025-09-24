# Data Product Access Control Implementation Guide

## Overview
This document provides detailed implementation guidance for consuming data products from Microsoft Fabric Lakehouses with proper access control and permissions management.

## 1. Access Control Layers

### Layer 1: Azure Active Directory (Identity)
```python
# Example: Service Principal Authentication
import os
from azure.identity import ClientSecretCredential

# Set up service principal for application
os.environ['AZURE_CLIENT_ID'] = 'your-app-client-id'
os.environ['AZURE_CLIENT_SECRET'] = 'your-app-secret'
os.environ['AZURE_TENANT_ID'] = 'your-tenant-id'

# Application will use these credentials automatically
```

### Layer 2: Fabric Workspace Permissions
```python
# Permission checking example
def check_workspace_permissions(user_principal_name, workspace_id):
    """
    Check if user has appropriate workspace permissions
    """
    # This would integrate with Fabric REST API
    workspace_permissions = get_workspace_permissions(workspace_id)
    user_role = workspace_permissions.get(user_principal_name)
    
    return user_role in ['Admin', 'Member', 'Contributor', 'Viewer']
```

### Layer 3: Database-Level Security
```sql
-- Create role-based access structure
CREATE ROLE DataAnalyst_Role;
CREATE ROLE DataScientist_Role;
CREATE ROLE BusinessUser_Role;

-- Grant permissions to roles
GRANT SELECT ON SCHEMA::silver TO DataAnalyst_Role;
GRANT SELECT ON SCHEMA::gold TO BusinessUser_Role;
GRANT SELECT, INSERT, UPDATE ON SCHEMA::sandbox TO DataScientist_Role;

-- Assign users to roles
ALTER ROLE DataAnalyst_Role ADD MEMBER [user@company.com];
```

### Layer 4: Row-Level Security (RLS)
```sql
-- Create security predicate function
CREATE FUNCTION dbo.fn_department_security(@department_id INT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS fn_security_predicate_result
WHERE @department_id = USER_NAME() OR IS_MEMBER('db_owner') = 1;

-- Apply RLS policy
CREATE SECURITY POLICY DepartmentSecurity
ADD FILTER PREDICATE dbo.fn_department_security(department_id) ON dbo.sales_data,
ADD BLOCK PREDICATE dbo.fn_department_security(department_id) ON dbo.sales_data;

-- Enable the policy
ALTER SECURITY POLICY DepartmentSecurity WITH (STATE = ON);
```

### Layer 5: Column-Level Security (CLS)
```sql
-- Grant specific column access
GRANT SELECT ON dbo.customers(customer_id, company_name, contact_name) TO BusinessUser_Role;

-- Hide sensitive columns (SSN, credit_card, etc.)
-- These columns won't be accessible to BusinessUser_Role
```

## 2. Data Product Consumption Patterns

### Pattern A: Self-Service Analytics
```python
from knauf_darc_connector import FabricLakehouseConnector
import pandas as pd

class SelfServiceAnalytics:
    def __init__(self, user_context):
        self.connector = FabricLakehouseConnector(
            sql_endpoint=user_context['endpoint'],
            database=user_context['default_database']
        )
        self.user_role = user_context['role']
    
    def get_available_data_products(self):
        """List data products accessible to current user"""
        with self.connector:
            query = """
                SELECT 
                    schema_name,
                    table_name,
                    description,
                    last_updated,
                    data_classification
                FROM information_schema.tables t
                JOIN data_catalog.data_products dp ON t.table_name = dp.product_name
                WHERE has_perms_by_name(QUOTENAME(schema_name) + '.' + QUOTENAME(table_name), 
                                      'OBJECT', 'SELECT') = 1
            """
            return self.connector.execute_query(query)
    
    def consume_data_product(self, product_name, filters=None):
        """Consume a specific data product with optional filters"""
        with self.connector:
            base_query = f"SELECT * FROM {product_name}"
            if filters:
                base_query += f" WHERE {filters}"
            
            return self.connector.execute_query(base_query)

# Usage example
user_context = {
    'endpoint': 'your-endpoint.datawarehouse.fabric.microsoft.com',
    'default_database': 'gold',
    'role': 'data_analyst'
}

analytics = SelfServiceAnalytics(user_context)
available_products = analytics.get_available_data_products()
sales_data = analytics.consume_data_product('dbo.sales_summary', "region = 'EMEA'")
```

### Pattern B: Automated Data Pipeline
```python
import schedule
import time
from datetime import datetime, timedelta

class DataPipeline:
    def __init__(self, config):
        self.source_connector = FabricLakehouseConnector(
            config['source_endpoint'], 
            config['source_database']
        )
        self.target_connector = FabricLakehouseConnector(
            config['target_endpoint'], 
            config['target_database']
        )
    
    def extract_transform_load(self):
        """ETL process with proper error handling and logging"""
        try:
            with self.source_connector:
                # Extract latest data
                extract_query = """
                    SELECT * FROM bronze.raw_transactions 
                    WHERE created_date >= DATEADD(day, -1, GETDATE())
                    AND processing_status = 'pending'
                """
                raw_data = self.source_connector.execute_query(extract_query)
            
            # Transform data (business logic)
            transformed_data = self.transform_data(raw_data)
            
            # Load to target lakehouse
            with self.target_connector:
                # This would use bulk insert or merge operations
                self.bulk_insert_data('silver.processed_transactions', transformed_data)
                
            # Update processing status
            with self.source_connector:
                update_query = """
                    UPDATE bronze.raw_transactions 
                    SET processing_status = 'completed', 
                        processed_date = GETDATE()
                    WHERE created_date >= DATEADD(day, -1, GETDATE())
                    AND processing_status = 'pending'
                """
                self.source_connector.execute_query(update_query)
                
        except Exception as e:
            self.log_error(f"ETL pipeline failed: {str(e)}")
            raise
    
    def transform_data(self, raw_data):
        """Apply business transformations"""
        # Data cleaning, aggregation, enrichment
        transformed = raw_data.copy()
        transformed['processed_timestamp'] = datetime.now()
        transformed['data_quality_score'] = self.calculate_quality_score(raw_data)
        return transformed
    
    def schedule_pipeline(self):
        """Schedule automated execution"""
        schedule.every().day.at("02:00").do(self.extract_transform_load)
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

# Usage
pipeline_config = {
    'source_endpoint': 'bronze-endpoint.datawarehouse.fabric.microsoft.com',
    'source_database': 'bronze',
    'target_endpoint': 'silver-endpoint.datawarehouse.fabric.microsoft.com',
    'target_database': 'silver'
}

pipeline = DataPipeline(pipeline_config)
pipeline.schedule_pipeline()
```

### Pattern C: Machine Learning Data Access
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

class MLDataConsumer:
    def __init__(self, model_config):
        self.connector = FabricLakehouseConnector(
            model_config['endpoint'],
            model_config['database']
        )
        self.model_config = model_config
    
    def get_training_data(self, feature_set_version='latest'):
        """Get curated training data for ML models"""
        with self.connector:
            query = f"""
                SELECT * FROM ml_features.customer_churn_features 
                WHERE feature_set_version = '{feature_set_version}'
                AND data_quality_flag = 'approved'
                AND training_eligible = 1
            """
            return self.connector.execute_query(query)
    
    def get_inference_data(self, customer_ids=None):
        """Get data for model inference"""
        with self.connector:
            base_query = """
                SELECT customer_id, feature_1, feature_2, feature_3, feature_4
                FROM ml_features.customer_current_features
            """
            if customer_ids:
                customer_list = ','.join([f"'{id}'" for id in customer_ids])
                base_query += f" WHERE customer_id IN ({customer_list})"
            
            return self.connector.execute_query(base_query)
    
    def train_model(self):
        """Train ML model with lakehouse data"""
        # Get training data
        training_data = self.get_training_data()
        
        # Prepare features and target
        X = training_data.drop(['customer_id', 'churn_flag'], axis=1)
        y = training_data['churn_flag']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Train model
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        
        # Save model and metadata
        model_path = f"models/churn_model_{datetime.now().strftime('%Y%m%d_%H%M')}.joblib"
        joblib.dump(model, model_path)
        
        # Save model metadata to lakehouse
        self.save_model_metadata(model_path, X_test, y_test, model)
        
        return model
    
    def save_model_metadata(self, model_path, X_test, y_test, model):
        """Save model performance metadata"""
        accuracy = model.score(X_test, y_test)
        
        metadata = pd.DataFrame({
            'model_path': [model_path],
            'accuracy': [accuracy],
            'created_date': [datetime.now()],
            'feature_count': [X_test.shape[1]],
            'training_samples': [len(X_test) * 5]  # Assuming 80/20 split
        })
        
        # This would insert into model registry table
        with self.connector:
            # Bulk insert metadata
            pass

# Usage
ml_config = {
    'endpoint': 'ml-endpoint.datawarehouse.fabric.microsoft.com',
    'database': 'ml_platform'
}

ml_consumer = MLDataConsumer(ml_config)
model = ml_consumer.train_model()
```

## 3. Security Best Practices

### Authentication Best Practices
```python
class SecureConnector:
    def __init__(self, config):
        self.config = config
        self.connector = None
        self.token_expiry = None
    
    def get_connector(self):
        """Get connector with token refresh logic"""
        if self.connector is None or self._token_expired():
            self.connector = FabricLakehouseConnector(
                self.config['endpoint'],
                self.config['database']
            )
            self.token_expiry = datetime.now() + timedelta(hours=1)
        
        return self.connector
    
    def _token_expired(self):
        """Check if token needs refresh"""
        return datetime.now() >= self.token_expiry
    
    def execute_with_retry(self, query, max_retries=3):
        """Execute query with automatic retry on auth failure"""
        for attempt in range(max_retries):
            try:
                connector = self.get_connector()
                with connector:
                    return connector.execute_query(query)
            except AuthenticationError:
                self.connector = None  # Force token refresh
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
```

### Data Access Auditing
```python
import logging
from functools import wraps

def audit_data_access(func):
    """Decorator to audit data access operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        user_context = get_current_user_context()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful access
            audit_log = {
                'timestamp': start_time,
                'user_id': user_context['user_id'],
                'operation': func.__name__,
                'success': True,
                'rows_accessed': len(result) if hasattr(result, '__len__') else 'unknown',
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
            
            log_audit_event(audit_log)
            return result
            
        except Exception as e:
            # Log failed access attempt
            audit_log = {
                'timestamp': start_time,
                'user_id': user_context['user_id'],
                'operation': func.__name__,
                'success': False,
                'error': str(e),
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
            
            log_audit_event(audit_log)
            raise
    
    return wrapper

@audit_data_access
def get_customer_data(customer_id):
    """Audited function to get customer data"""
    connector = get_secure_connector()
    with connector:
        return connector.execute_query(f"SELECT * FROM customers WHERE id = '{customer_id}'")
```

## 4. Governance Integration

### Data Catalog Integration
```python
class DataCatalogIntegration:
    def __init__(self, catalog_config):
        self.catalog_api = DataCatalogAPI(catalog_config)
        self.connector = FabricLakehouseConnector(
            catalog_config['lakehouse_endpoint'],
            catalog_config['database']
        )
    
    def discover_data_products(self, user_context):
        """Discover available data products for user"""
        user_permissions = self.get_user_permissions(user_context['user_id'])
        available_products = []
        
        for product in self.catalog_api.list_all_products():
            if self.has_access(product, user_permissions):
                product_metadata = self.get_product_metadata(product)
                available_products.append(product_metadata)
        
        return available_products
    
    def get_product_metadata(self, product):
        """Get comprehensive metadata for data product"""
        with self.connector:
            metadata_query = f"""
                SELECT 
                    p.product_name,
                    p.description,
                    p.owner,
                    p.last_updated,
                    p.update_frequency,
                    p.data_classification,
                    p.retention_period,
                    s.row_count,
                    s.column_count,
                    s.size_mb
                FROM data_catalog.products p
                JOIN data_catalog.statistics s ON p.product_id = s.product_id
                WHERE p.product_name = '{product['name']}'
            """
            return self.connector.execute_query(metadata_query)
```

This architecture provides a comprehensive framework for secure, governed access to Fabric Lakehouse data products while maintaining flexibility for various consumption patterns and use cases.