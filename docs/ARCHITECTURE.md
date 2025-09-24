# Knauf DARC Data Connector - Architecture Overview

## System Architecture: Lakehouse Data Product Consumption

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MICROSOFT FABRIC ECOSYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Lakehouse A   │    │   Lakehouse B   │    │   Lakehouse C   │                │
│  │   (Silver)      │    │   (Gold)        │    │   (Bronze)      │                │
│  │                 │    │                 │    │                 │                │
│  │ ├─ Tables       │    │ ├─ Tables       │    │ ├─ Raw Data     │                │
│  │ ├─ Views        │    │ ├─ Views        │    │ ├─ Files        │                │
│  │ └─ Functions    │    │ └─ Aggregates   │    │ └─ Streaming    │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                       │
│           └───────────────────────┼───────────────────────┘                       │
│                                   │                                               │
│  ┌─────────────────────────────────┼─────────────────────────────────────────────┐ │
│  │              FABRIC SECURITY & ACCESS CONTROL                              │ │
│  │                                 │                                           │ │
│  │  ┌─────────────────┐           │    ┌─────────────────┐                    │ │
│  │  │   Azure AD      │           │    │ Workspace-Level │                    │ │
│  │  │   Identity      │◄──────────┼────┤   Permissions   │                    │ │
│  │  │                 │           │    │                 │                    │ │
│  │  │ ├─ Users        │           │    │ ├─ Admin        │                    │ │
│  │  │ ├─ Groups       │           │    │ ├─ Member       │                    │ │
│  │  │ ├─ Service      │           │    │ ├─ Contributor  │                    │ │
│  │  │   Principals    │           │    │ └─ Viewer       │                    │ │
│  │  │ └─ Managed ID   │           │    └─────────────────┘                    │ │
│  │  └─────────────────┘           │                                           │ │
│  │                                │                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    FABRIC SQL ENDPOINT                             │   │ │
│  │  │                                                                     │   │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │   │ │
│  │  │  │    RLS      │  │    CLS      │  │  Database   │                │   │ │
│  │  │  │ Row-Level   │  │ Column-Level│  │   Level     │                │   │ │
│  │  │  │  Security   │  │  Security   │  │ Permissions │                │   │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘                │   │ │
│  │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                               │
└───────────────────────────────────┼───────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────────────┐
    │                    KNAUF DARC DATA CONNECTOR                          │
    │                               │                                       │
    │  ┌─────────────────────────────┼─────────────────────────────────────┐ │
    │  │              AUTHENTICATION LAYER                               │ │
    │  │                             │                                   │ │
    │  │  ┌─────────────┐  ┌─────────┼─────────┐  ┌─────────────────────┐ │ │
    │  │  │   Service   │  │  Azure  │   CLI   │  │  Default Azure      │ │ │
    │  │  │  Principal  │  │         │         │  │   Credential        │ │ │
    │  │  │             │  │         │         │  │                     │ │ │
    │  │  │ ├─Client ID │  │  az     │ login   │  │ ├─ Managed Identity  │ │ │
    │  │  │ ├─Secret    │  │         │         │  │ ├─ Environment Vars  │ │ │
    │  │  │ └─Tenant ID │  │         │         │  │ └─ VS Code/CLI      │ │ │
    │  │  └─────────────┘  └─────────┼─────────┘  └─────────────────────┘ │ │
    │  └─────────────────────────────┼─────────────────────────────────────┘ │
    │                                │                                       │
    │  ┌─────────────────────────────┼─────────────────────────────────────┐ │
    │  │              CONNECTION LAYER                                   │ │
    │  │                             │                                   │ │
    │  │          ┌─────────────────┼─────────────────┐                   │ │
    │  │          │   ODBC Driver   │   18 for SQL    │                   │ │
    │  │          │                 │    Server       │                   │ │
    │  │          └─────────────────┼─────────────────┘                   │ │
    │  │                             │                                   │ │
    │  │          ┌─────────────────┼─────────────────┐                   │ │
    │  │          │  Fabric         │   Lakehouse     │                   │ │
    │  │          │  Connector      │   Connector     │                   │ │
    │  │          │                 │                 │                   │ │
    │  │          │ ├─ Token Mgmt   │ ├─ SQL Endpoint │                   │ │
    │  │          │ ├─ Connection   │ ├─ Database      │                   │ │
    │  │          │ └─ Error Handle │ └─ Context Mgr  │                   │ │
    │  │          └─────────────────┼─────────────────┘                   │ │
    │  └─────────────────────────────┼─────────────────────────────────────┘ │
    └───────────────────────────────┼───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────────────┐
    │                    DATA CONSUMPTION LAYER                             │
    │                               │                                       │
    │  ┌─────────────────┐  ┌───────┼───────┐  ┌─────────────────────────┐ │
    │  │   Python Apps   │  │  Data │ Science│  │    Business Apps        │ │
    │  │                 │  │       │        │  │                         │ │
    │  │ ├─ ETL Scripts  │  │ ├─ Ju │yter   │  │ ├─ Dashboards           │ │
    │  │ ├─ Data         │  │ ├─ ML │Models │  │ ├─ Reports              │ │
    │  │   Processing    │  │ ├─ An │lytics │  │ ├─ Web Applications     │ │
    │  │ └─ Automation   │  │ └─ Pa │das    │  │ └─ APIs                 │ │
    │  └─────────────────┘  └───────┼───────┘  └─────────────────────────┘ │
    │           │                   │                       │               │
    │           └───────────────────┼───────────────────────┘               │
    │                               │                                       │
    │  ┌─────────────────────────────┼─────────────────────────────────────┐ │
    │  │                    PANDAS DATAFRAMES                            │ │
    │  │                             │                                   │ │
    │  │    df = connector.execute_query("SELECT * FROM dbo.orders")     │ │
    │  │                             │                                   │ │
    │  │  ┌─────────────┐  ┌─────────┼─────────┐  ┌─────────────────────┐ │ │
    │  │  │   Direct    │  │  Data   │ Analysis│  │    Integration      │ │ │
    │  │  │  Queries    │  │         │         │  │                     │ │ │
    │  │  │             │  │ ├─ EDA  │         │  │ ├─ External Systems  │ │ │
    │  │  │ ├─ Tables   │  │ ├─ Stat │ istics  │  │ ├─ APIs              │ │ │
    │  │  │ ├─ Views    │  │ ├─ Visu │lization │  │ ├─ File Exports      │ │ │
    │  │  │ └─ Functions│  │ └─ ML   │ Prep    │  │ └─ Data Pipelines    │ │ │
    │  │  └─────────────┘  └─────────┼─────────┘  └─────────────────────┘ │ │
    │  └─────────────────────────────┼─────────────────────────────────────┘ │
    └───────────────────────────────┼───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────────────┐
    │                      SECURITY & GOVERNANCE                            │
    │                               │                                       │
    │  ┌─────────────────┐  ┌───────┼───────┐  ┌─────────────────────────┐ │
    │  │   Data          │  │  Audit│ & Log │  │    Compliance           │ │
    │  │   Governance    │  │       │       │  │                         │ │
    │  │                 │  │ ├─ Acc │ess Log│  │ ├─ GDPR                 │ │
    │  │ ├─ Data Catalog │  │ ├─ Que │ry Log │  │ ├─ SOX                  │ │
    │  │ ├─ Lineage      │  │ ├─ Err │ or Log │  │ ├─ Industry Standards  │ │
    │  │ ├─ Quality      │  │ └─ Per │ f. Log │  │ └─ Data Retention      │ │
    │  │ └─ Metadata     │  └───────┼───────┘  └─────────────────────────┘ │
    │  └─────────────────┘          │                                     │
    └───────────────────────────────┼───────────────────────────────────────┘
```

## Access Control & Permission Matrix

### 1. Azure AD Identity Management
- **Users**: Individual employee accounts
- **Groups**: Department/role-based groups  
- **Service Principals**: Application identities
- **Managed Identities**: Azure resource identities

### 2. Fabric Workspace Permissions
| Role        | Read Data | Write Data | Manage Items | Admin Functions |
|-------------|-----------|------------|--------------|-----------------|
| **Admin**   | ✅        | ✅         | ✅           | ✅              |
| **Member**  | ✅        | ✅         | ✅           | ❌              |
| **Contributor** | ✅    | ✅         | ❌           | ❌              |
| **Viewer**  | ✅        | ❌         | ❌           | ❌              |

### 3. Database-Level Security
- **Database Permissions**: db_datareader, db_datawriter, db_owner
- **Schema Permissions**: SELECT, INSERT, UPDATE, DELETE on specific schemas
- **Object Permissions**: Granular table/view/function permissions

### 4. Row-Level Security (RLS)
```sql
-- Example: Users can only see their department's data
CREATE SECURITY POLICY DepartmentFilter  
ADD FILTER PREDICATE dbo.fn_securitypredicate(DepartmentID) ON dbo.Orders
```

### 5. Column-Level Security (CLS)
```sql
-- Example: Hide sensitive columns from certain users
GRANT SELECT ON dbo.Orders(OrderID, CustomerName, OrderDate) TO DataAnalyst_Role
-- Excludes sensitive columns like SSN, CreditCard, etc.
```

## Data Product Consumption Patterns

### Pattern 1: Direct Query Access
```python
from knauf_darc_connector import FabricLakehouseConnector

# Initialize connector with automatic authentication
connector = FabricLakehouseConnector(
    sql_endpoint="your-endpoint.datawarehouse.fabric.microsoft.com",
    database="silver"
)

# Consume data products
with connector:
    # Get curated data product
    sales_data = connector.execute_query("""
        SELECT * FROM dbo.vw_sales_dashboard_data 
        WHERE report_date >= '2024-01-01'
    """)
    
    # Access specific data product
    customer_insights = connector.execute_query("""
        EXEC dbo.sp_get_customer_insights @customer_segment = 'enterprise'
    """)
```

### Pattern 2: Data Science Workflow
```python
import pandas as pd
from knauf_darc_connector import FabricLakehouseConnector

connector = FabricLakehouseConnector(endpoint, database)

with connector:
    # Extract features for ML model
    features = connector.execute_query("""
        SELECT customer_id, tenure, avg_order_value, churn_risk_score
        FROM gold.customer_features 
        WHERE model_version = 'v2.1'
    """)
    
    # Perform analysis
    correlation = features.corr()
    model_ready_data = features.dropna()
```

### Pattern 3: Business Intelligence Integration
```python
# Automated report generation
def generate_monthly_report():
    connector = FabricLakehouseConnector(endpoint, "gold")
    
    with connector:
        # Get KPI data
        kpis = connector.execute_query("""
            SELECT * FROM dbo.monthly_kpis 
            WHERE report_month = DATEADD(month, -1, GETDATE())
        """)
        
        # Export for BI tools
        kpis.to_csv('monthly_kpis.csv')
        return kpis
```

## Security Implementation

### Authentication Flow
1. **Application Start**: Connector attempts authentication methods in priority order
2. **Token Acquisition**: Secure token obtained from Azure AD
3. **Connection Establishment**: ODBC connection with token-based auth
4. **Query Execution**: All queries executed with user context
5. **Audit Logging**: All access logged for compliance

### Permission Validation
1. **Workspace Access**: User must have appropriate workspace role
2. **Database Permission**: User must have database-level access
3. **Object Permission**: User must have permissions on specific tables/views
4. **Row-Level Filter**: RLS policies applied automatically
5. **Column-Level Filter**: CLS restrictions enforced

### Data Governance Integration
- **Data Catalog**: Automatic discovery of available data products
- **Lineage Tracking**: Track data flow from source to consumption
- **Quality Monitoring**: Automated data quality checks
- **Compliance Reporting**: Audit trails for regulatory requirements

This architecture ensures secure, governed, and scalable access to Fabric Lakehouse data products while maintaining flexibility for various consumption patterns.