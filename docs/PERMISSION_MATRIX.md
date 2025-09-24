# Permission Matrix & Access Patterns

## Quick Reference: Access Control Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PERMISSION MATRIX                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                     │
│  LAYER 1: AZURE AD IDENTITY                                                                        │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐            │
│  │     USERS       │   │     GROUPS      │   │    SERVICE      │   │    MANAGED      │            │
│  │                 │   │                 │   │   PRINCIPALS    │   │   IDENTITIES    │            │
│  │ ├─ Individual   │   │ ├─ Department   │   │                 │   │                 │            │
│  │   Employees     │   │   Based         │   │ ├─ Application  │   │ ├─ VM Identity  │            │
│  │ ├─ External     │   │ ├─ Role Based   │   │   Identity      │   │ ├─ Function     │            │
│  │   Users         │   │ └─ Project      │   │ └─ Automation   │   │   App Identity  │            │
│  │ └─ Contractors  │   │   Teams         │   │   Scripts       │   │ └─ AKS Identity │            │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘            │
│           │                       │                       │                       │                │
│           └───────────────────────┼───────────────────────┼───────────────────────┘                │
│                                   │                       │                                        │
│  LAYER 2: FABRIC WORKSPACE PERMISSIONS                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  ROLE        │  READ DATA  │  WRITE DATA │  MANAGE ITEMS │  ADMIN FUNCTIONS │  USE CASES   │  │
│  │──────────────┼─────────────┼─────────────┼───────────────┼──────────────────┼──────────────│  │
│  │  Admin       │      ✅      │      ✅      │       ✅       │        ✅         │ Full Control │  │
│  │  Member      │      ✅      │      ✅      │       ✅       │        ❌         │ Development  │  │
│  │  Contributor │      ✅      │      ✅      │       ❌       │        ❌         │ Data Eng.   │  │
│  │  Viewer      │      ✅      │      ❌      │       ❌       │        ❌         │ Read Only    │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                   │                                                                │
│  LAYER 3: DATABASE PERMISSIONS    │                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  DATABASE ROLE     │  SCHEMA ACCESS     │  TABLE ACCESS      │  TYPICAL USERS             │  │
│  │────────────────────┼────────────────────┼────────────────────┼────────────────────────────│  │
│  │  db_owner          │  All Schemas       │  Full Control      │  Database Administrators   │  │
│  │  db_datareader     │  All Schemas       │  SELECT Only       │  Report Users              │  │
│  │  db_datawriter     │  Allowed Schemas   │  INSERT/UPDATE     │  ETL Processes             │  │
│  │  DataAnalyst_Role  │  silver, gold      │  SELECT + Views    │  Business Analysts         │  │
│  │  DataScientist_Role│  All + sandbox     │  SELECT + Temp     │  Data Scientists           │  │
│  │  BusinessUser_Role │  gold Only         │  SELECT Curated    │  Business Users            │  │
│  │  MLPlatform_Role   │  ml_features       │  SELECT + Models   │  ML Applications           │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                   │                                                                │
│  LAYER 4: ROW-LEVEL SECURITY (RLS)│                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  SECURITY PREDICATE       │  FILTER LOGIC              │  APPLIED TO                        │  │
│  │───────────────────────────┼────────────────────────────┼────────────────────────────────────│  │
│  │  Department Filter        │  department_id = USER_ID   │  Sales, Customer, Order Data       │  │
│  │  Region Filter            │  region = USER_REGION()    │  Geographic Data Sets              │  │
│  │  Time-based Filter        │  date >= USER_START_DATE   │  Historical Data Access            │  │
│  │  Hierarchy Filter         │  reports_to_check()        │  Management Reporting Data         │  │
│  │  Project Filter           │  project_id IN (user_proj) │  Project-specific Data             │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                   │                                                                │
│  LAYER 5: COLUMN-LEVEL SECURITY   │                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  DATA CLASSIFICATION     │  COLUMNS HIDDEN            │  ACCESSIBLE TO                       │  │
│  │──────────────────────────┼────────────────────────────┼──────────────────────────────────────│  │
│  │  Highly Confidential     │  SSN, Credit Card, Salary  │  db_owner, HR_Role Only              │  │
│  │  Confidential            │  Phone, Email, Address     │  Manager_Role + Above                │  │
│  │  Internal                │  Employee ID, Department   │  Employee_Role + Above               │  │
│  │  Public                  │  Name, Title, Location     │  All Authenticated Users             │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Product Access Patterns

### Pattern 1: Self-Service Analytics
```
USER REQUEST → AUTHENTICATION → WORKSPACE CHECK → CATALOG BROWSE → PERMISSION FILTER → DATA ACCESS
     │                │               │               │                │                   │
     │                ├─ Azure AD     ├─ Fabric       ├─ Available     ├─ RLS/CLS         ├─ Query
     │                ├─ Token        │  Workspace    │  Products      │  Applied          │  Execution
     │                └─ Validation   └─ Role Check   └─ Metadata      └─ Audit Log       └─ Results
```

### Pattern 2: Automated ETL Pipeline
```
SCHEDULE → SERVICE PRINCIPAL → BULK DATA ACCESS → TRANSFORMATION → TARGET LOAD
    │             │                    │                 │              │
    ├─ Cron        ├─ App              ├─ Large          ├─ Business    ├─ Destination
    │  Job         │  Registration     │  Datasets       │  Logic       │  Lakehouse
    └─ Trigger     └─ Certificate      └─ Parallel       └─ Validation  └─ Confirmation
```

### Pattern 3: ML Model Training
```
MODEL REQUEST → FEATURE STORE → TRAINING DATA → MODEL TRAINING → MODEL REGISTRY
      │              │              │               │                │
      ├─ ML           ├─ Versioned   ├─ Quality      ├─ Automated     ├─ Model
      │  Pipeline     │  Features    │  Approved     │  Training      │  Metadata
      └─ Experiment   └─ Lineage     └─ Labeled      └─ Validation    └─ Deployment
```

## Security Implementation Examples

### 1. Department-based Row Level Security
```sql
-- Create security function
CREATE FUNCTION security.fn_department_access(@dept_id int)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN (
    SELECT 1 as result
    WHERE @dept_id = CAST(SESSION_CONTEXT(N'department_id') AS int)
       OR IS_MEMBER('db_owner') = 1
       OR IS_MEMBER('DataAdmin_Role') = 1
);

-- Apply to sales table
CREATE SECURITY POLICY security.DepartmentAccessPolicy
ADD FILTER PREDICATE security.fn_department_access(department_id) ON dbo.sales_data
WITH (STATE = ON);
```

### 2. Dynamic Column-Level Security
```sql
-- Grant base permissions
GRANT SELECT ON dbo.customers TO BusinessUser_Role;

-- Restrict sensitive columns
DENY SELECT ON dbo.customers(ssn, credit_card, salary) TO BusinessUser_Role;

-- Create view for business users
CREATE VIEW business.customer_summary AS
SELECT 
    customer_id,
    company_name,
    contact_name,
    city,
    country,
    CASE 
        WHEN IS_MEMBER('Manager_Role') = 1 THEN phone
        ELSE 'RESTRICTED'
    END as phone,
    CASE 
        WHEN IS_MEMBER('HR_Role') = 1 THEN email
        ELSE 'RESTRICTED'
    END as email
FROM dbo.customers;
```

### 3. Time-based Access Control
```sql
-- Create time-based security function
CREATE FUNCTION security.fn_time_access(@record_date datetime)
RETURNS TABLE
WITH SCHEMABINDING  
AS
RETURN (
    SELECT 1 as result
    WHERE @record_date >= CAST(SESSION_CONTEXT(N'data_access_start') AS datetime)
       OR IS_MEMBER('HistoricalDataAccess_Role') = 1
);

-- Apply to historical data
CREATE SECURITY POLICY security.TimeBasedAccessPolicy
ADD FILTER PREDICATE security.fn_time_access(created_date) ON dbo.transaction_history
WITH (STATE = ON);
```

## Monitoring & Compliance Dashboard

### Key Metrics to Track
1. **Access Patterns**: Who accesses what data products when
2. **Permission Violations**: Failed access attempts and reasons
3. **Data Usage**: Volume and frequency of data consumption
4. **Performance**: Query response times and system load
5. **Compliance**: Audit trail completeness and retention

### Alert Conditions
1. **Unusual Access Patterns**: Off-hours access by business users
2. **Permission Escalation**: Users attempting to access restricted data
3. **Bulk Data Extraction**: Large volume downloads outside normal patterns
4. **Failed Authentication**: Multiple failed login attempts
5. **Data Quality Issues**: Degraded data quality in consumed products

This comprehensive access control framework ensures secure, governed, and auditable consumption of data products from Fabric Lakehouses while enabling self-service analytics and automated data pipelines.