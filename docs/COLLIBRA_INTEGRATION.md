# Collibra Data Product Access Request Process

## Overview
This document outlines the streamlined process for users to request data product access through Collibra, with automated provisioning to Microsoft Fabric Lakehouses.

## High-Level Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COLLIBRA → FABRIC ACCESS PROCESS                     │
└─────────────────────────────────────────────────────────────────────────────────┘

   USER                COLLIBRA              APPROVAL           PROVISIONING         FABRIC
    │                     │                     │                    │               │
    │  1. Browse Data     │                     │                    │               │
    │  ───────────────►   │                     │                    │               │
    │                     │                     │                    │               │
    │  2. Request Access  │                     │                    │               │
    │  ───────────────►   │                     │                    │               │
    │                     │  3. Route Request   │                    │               │
    │                     │  ─────────────────► │                    │               │
    │                     │                     │  4. Multi-Stage    │               │
    │                     │                     │     Approval       │               │
    │                     │                     │     (Owner/Manager/│               │
    │                     │                     │      Compliance)   │               │
    │                     │  5. Approval Result │                    │               │
    │                     │  ◄───────────────── │                    │               │
    │                     │                     │                    │               │
    │                     │  6. Trigger Provisioning                 │               │
    │                     │  ─────────────────────────────────────►  │               │
    │                     │                     │                    │  7. Create    │
    │                     │                     │                    │     Groups &  │
    │                     │                     │                    │     Permissions│
    │                     │                     │                    │  ───────────► │
    │                     │                     │                    │               │
    │  8. Access Granted  │                     │                    │               │
    │  ◄─────────────────  │                     │                    │               │
    │                     │                     │                    │               │
    │  9. Connect & Query │                     │                    │               │
    │  ─────────────────────────────────────────────────────────────────────────►   │
    │                     │                     │                    │               │
    │ 10. Usage Monitoring│                     │                    │               │
    │  ◄─────────────────  │                     │                    │               │

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PROCESS COMPONENTS                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│  COLLIBRA CATALOG    │  APPROVAL WORKFLOW  │  AUTO PROVISIONING │  FABRIC ACCESS │
│  ├─ Data Discovery   │  ├─ Data Owner      │  ├─ Azure AD Groups │  ├─ Workspace  │
│  ├─ Request Form     │  ├─ Manager Review  │  ├─ Role Assignment │  ├─ Database    │
│  ├─ Business Context │  ├─ Compliance      │  ├─ Permission Sync │  ├─ Table/View │
│  └─ Asset Metadata   │  └─ Auto-Approval   │  └─ Notification    │  └─ Row/Column │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                                                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┐
│                                          MICROSOFT FABRIC ECOSYSTEM                                        │                    │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┤
│                                                                                                             │                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │                    │
│  │   Lakehouse A   │    │   Lakehouse B   │    │   Lakehouse C   │    │   Lakehouse D   │                  │                    │
│  │   (Bronze)      │    │   (Silver)      │    │   (Gold)        │    │   (Sandbox)     │                  │                    │
│  │   Raw Data      │    │   Curated       │    │   Business      │    │   Experimental  │                  │                    │
│  │                 │    │   Data          │    │   Products      │    │   Data          │                  │                    │
│  │ ├─ Streaming    │    │                 │    │                 │    │                 │                  │                    │
│  │ ├─ Files        │    │ ├─ Tables       │    │ ├─ Dashboards   │    │ ├─ ML Models    │                  │                    │
│  │ └─ Raw APIs     │    │ ├─ Views        │    │ ├─ Reports      │    │ ├─ Experiments  │                  │                    │
│  └─────────────────┘    │ └─ Procedures   │    │ └─ KPIs         │    │ └─ Temp Data    │                  │                    │
│           │              └─────────────────┘    └─────────────────┘    └─────────────────┘                  │                    │
│           │                       │                       │                       │                         │                    │
│           └───────────────────────┼───────────────────────┼───────────────────────┘                         │                    │
│                                   │                       │                                                 │                    │
│  ┌─────────────────────────────────┼───────────────────────┼─────────────────────────────────────────────────┼──────────────────┐ │
│  │                          FABRIC WORKSPACE MANAGEMENT                                                   │                  │ │
│  │                                 │                       │                                             │                  │ │
│  │  ┌─────────────────┐           │    ┌─────────────────┐  │   ┌─────────────────┐    ┌─────────────────┼──────────────────┐ │ │
│  │  │   WORKSPACE     │           │    │   ROLE-BASED    │  │   │   DYNAMIC       │    │   PERMISSION    │                  │ │ │
│  │  │   PROVISIONING  │◄──────────┼────┤   ACCESS        │◄─┼───┤   GROUPS        │    │   AUDIT         │                  │ │ │
│  │  │                 │           │    │   CONTROL       │  │   │                 │    │                 │                  │ │ │
│  │  │ ├─ Auto         │           │    │                 │  │   │ ├─ Department   │    │ ├─ Access Log   │                  │ │ │
│  │  │   Workspace     │           │    │ ├─ Data         │  │   │   Based Groups  │    │ ├─ Permission   │                  │ │ │
│  │  │   Creation      │           │    │   Analyst       │  │   │ ├─ Project      │    │   Changes       │                  │ │ │
│  │  │ ├─ User         │           │    │ ├─ Data         │  │   │   Based Groups  │    │ └─ Compliance   │                  │ │ │
│  │  │   Assignment    │           │    │   Scientist     │  │   │ └─ Temporary    │    │   Reports       │                  │ │ │
│  │  │ └─ Permission   │           │    │ ├─ Business     │  │   │   Access Groups │    │                 │                  │ │ │
│  │  │   Mapping       │           │    │   User          │  │   │                 │    │                 │                  │ │ │
│  │  └─────────────────┘           │    │ └─ ML Engineer  │  │   └─────────────────┘    └─────────────────┼──────────────────┘ │ │
│  │                                │    └─────────────────┘  │                                           │                  │ │
│  │                                │                         │                                           │                  │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────┐ │ │
│  │  │                                    SQL ENDPOINT SECURITY                                         │                  │ │ │
│  │  │                                                                                                   │                  │ │ │
│  │  │    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │                  │ │ │
│  │  │    │   DATABASE      │    │   ROW-LEVEL     │    │   COLUMN-LEVEL  │    │   DYNAMIC       │      │                  │ │ │
│  │  │    │   ROLES         │    │   SECURITY      │    │   SECURITY      │    │   DATA MASKING  │      │                  │ │ │
│  │  │    │                 │    │                 │    │                 │    │                 │      │                  │ │ │
│  │  │    │ ├─ Reader       │    │ ├─ Department   │    │ ├─ PII          │    │ ├─ Sensitive    │      │                  │ │ │
│  │  │    │ ├─ Writer       │    │   Filter        │    │   Protection    │    │   Data Masking  │      │                  │ │ │
│  │  │    │ ├─ Contributor  │    │ ├─ Geography    │    │ ├─ Financial     │    │ ├─ Context      │      │                  │ │ │
│  │  │    │ └─ Admin        │    │   Filter        │    │   Data          │    │   Based         │      │                  │ │ │
│  │  │    └─────────────────┘    │ └─ Time Filter  │    │ └─ HR Data      │    │ └─ Role Based   │      │                  │ │ │
│  │  │                           └─────────────────┘    └─────────────────┘    └─────────────────┘      │                  │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┘
                                                                                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┐
│                                      KNAUF DARC DATA CONNECTOR                                             │                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
│                                                                                                             │                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┐ │
│  │                                    ENHANCED AUTHENTICATION                                             │                      │ │
│  │                                                                                                         │                      │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │                      │ │
│  │  │   COLLIBRA      │    │   AZURE AD      │    │   FABRIC        │    │   PERMISSION    │              │                      │ │
│  │  │   INTEGRATION   │    │   ENHANCED      │    │   WORKSPACE     │    │   VALIDATION    │              │                      │ │
│  │  │                 │    │                 │    │   VALIDATION    │    │                 │              │                      │ │
│  │  │ ├─ Asset        │    │ ├─ User Context │    │                 │    │ ├─ Real-time    │              │                      │ │
│  │  │   Validation    │    │ ├─ Group        │    │ ├─ Workspace    │    │   Permission    │              │                      │ │
│  │  │ ├─ Access       │    │   Membership    │    │   Membership    │    │   Check         │              │                      │ │
│  │  │   Verification  │    │ └─ Dynamic      │    │ └─ Role         │    │ └─ Access       │              │                      │ │
│  │  │ └─ Usage        │    │   Token         │    │   Validation    │    │   Logging       │              │                      │ │
│  │  │   Tracking      │    │   Refresh       │    │                 │    │                 │              │                      │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │                      │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┘ │
│                                                                                                             │                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┐ │
│  │                                    DATA CONSUMPTION WITH GOVERNANCE                                    │                      │ │
│  │                                                                                                         │                      │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │                      │ │
│  │  │   GOVERNED      │    │   USAGE         │    │   AUDIT &       │    │   FEEDBACK      │              │                      │ │
│  │  │   DATA ACCESS   │    │   MONITORING    │    │   COMPLIANCE    │    │   LOOP          │              │                      │ │
│  │  │                 │    │                 │    │                 │    │                 │              │                      │ │
│  │  │ ├─ Approved     │    │ ├─ Query        │    │ ├─ Access       │    │ ├─ Usage        │              │                      │ │
│  │  │   Assets Only   │    │   Tracking      │    │   Audit         │    │   Analytics     │              │                      │ │
│  │  │ ├─ Permission   │    │ ├─ Performance  │    │ ├─ Compliance   │    │ ├─ Permission   │              │                      │ │
│  │  │   Enforcement   │    │   Monitoring    │    │   Reporting     │    │   Optimization  │              │                      │ │
│  │  │ └─ Data         │    │ └─ Usage        │    │ └─ Violation    │    │ └─ Access       │              │                      │ │
│  │  │   Lineage       │    │   Patterns      │    │   Detection     │    │   Reviews       │              │                      │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │                      │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────┘
                                                                                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────┐
│                                        END USER APPLICATIONS                                               │                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────┤
│                                                                                                             │                        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │                        │
│  │   PYTHON        │    │   BUSINESS      │    │   ML PLATFORMS  │    │   DATA          │                  │                        │
│  │   APPLICATIONS  │    │   INTELLIGENCE  │    │                 │    │   SCIENCE       │                  │                        │
│  │                 │    │                 │    │                 │    │   WORKBENCH     │                  │                        │
│  │ ├─ Jupyter      │    │ ├─ Power BI     │    │ ├─ Azure ML     │    │                 │                  │                        │
│  │   Notebooks     │    │ ├─ Tableau      │    │ ├─ Databricks   │    │ ├─ Data Mining  │                  │                        │
│  │ ├─ ETL Scripts  │    │ ├─ Qlik         │    │ ├─ MLflow       │    │ ├─ Statistical  │                  │                        │
│  │ └─ Analytics    │    │ └─ Custom       │    │ └─ Kubeflow     │    │   Analysis      │                  │                        │
│  │   Apps          │    │   Dashboards    │    │                 │    │ └─ Visualization│                  │                        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘                  │                        │
│           │                       │                       │                       │                         │                        │
│           └───────────────────────┼───────────────────────┼───────────────────────┘                         │                        │
│                                   │                       │                                                 │                        │
│  ┌─────────────────────────────────┼───────────────────────┼─────────────────────────────────────────────────┼────────────────────────┐ │
│  │                          UNIFIED DATA ACCESS LAYER                                                     │                        │ │
│  │                                 │                       │                                             │                        │ │
│  │    df = connector.execute_query_with_governance("SELECT * FROM gold.customer_insights")              │                        │ │
│  │                                 │                       │                                             │                        │ │
│  │  ┌─────────────────┐           │    ┌─────────────────┐  │   ┌─────────────────┐    ┌─────────────────┼────────────────────────┐ │ │
│  │  │   COLLIBRA      │           │    │   FABRIC        │  │   │   GOVERNANCE    │    │   USAGE         │                        │ │ │
│  │  │   GOVERNED      │◄──────────┼────┤   LAKEHOUSE     │◄─┼───┤   VALIDATION    │    │   TRACKING      │                        │ │ │
│  │  │   ACCESS        │           │    │   DATA          │  │   │                 │    │                 │                        │ │ │
│  │  │                 │           │    │                 │  │   │ ├─ Asset        │    │ ├─ Query        │                        │ │ │
│  │  │ ├─ Asset        │           │    │ ├─ Tables       │  │   │   Authorization │    │   Logging       │                        │ │ │
│  │  │   Authorization │           │    │ ├─ Views        │  │   │ ├─ Permission   │    │ ├─ Performance  │                        │ │ │
│  │  │ ├─ Data         │           │    │ ├─ Procedures   │  │   │   Verification  │    │   Metrics       │                        │ │ │
│  │  │   Lineage       │           │    │ └─ Functions    │  │   │ └─ Usage        │    │ └─ Audit        │                        │ │ │
│  │  │ └─ Quality      │           │    │                 │  │   │   Compliance    │    │   Trails        │                        │ │ │
│  │  │   Validation    │           │    │                 │  │   │                 │    │                 │                        │ │ │
│  │  └─────────────────┘           │    └─────────────────┘  │   └─────────────────┘    └─────────────────┼────────────────────────┘ │ │
│  └─────────────────────────────────┼───────────────────────┼─────────────────────────────────────────────────┼──────────────────────────┘ │
└─────────────────────────────────────┼───────────────────────┼─────────────────────────────────────────────────┼────────────────────────────┘
                                      │                       │                                             │
                                      └───────────────────────┘                                             │
                                                                                                            │
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┐
│                                    GOVERNANCE & COMPLIANCE FEEDBACK LOOP                                  │                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┤
│                                                                                                             │                            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │                            │
│  │   USAGE         │    │   ACCESS        │    │   COMPLIANCE    │    │   OPTIMIZATION  │                  │                            │
│  │   ANALYTICS     │    │   REVIEWS       │    │   MONITORING    │    │   RECOMMENDATIONS│                 │                            │
│  │                 │    │                 │    │                 │    │                 │                  │                            │
│  │ ├─ Popular      │    │ ├─ Periodic     │    │ ├─ Policy       │    │ ├─ Permission   │                  │                            │
│  │   Datasets      │    │   Reviews       │    │   Violations    │    │   Optimization  │                  │                            │
│  │ ├─ Access       │    │ ├─ Role         │    │ ├─ Audit        │    │ ├─ Access       │                  │                            │
│  │   Patterns      │    │   Adjustments   │    │   Findings      │    │   Streamlining  │                  │                            │
│  │ └─ Performance  │    │ └─ Permission   │    │ └─ Remediation  │    │ └─ Policy       │                  │                            │
│  │   Insights      │    │   Cleanup       │    │   Actions       │    │   Updates       │                  │                            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘                  │                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────┘
```

## Step-by-Step Process

### 1. Data Discovery in Collibra
- User browses Collibra data catalog
- Searches data products using business terms
- Reviews metadata, lineage, and quality scores
- Identifies required access level

### 2. Access Request Submission
**Request Form includes:**
- Data product/table selection
- Access level (Read/Write/Admin)
- Business justification and use case
- Duration needed
- Compliance requirements

### 3. Automated Routing & Approval
**Approval Routing Based on Data Classification:**
- **Public Data**: Auto-approved
- **Internal Data**: Data Owner approval
- **Confidential Data**: Data Owner + Manager approval
- **Restricted Data**: Data Owner + Manager + Compliance approval

**Approval Stages:**
1. **Data Owner Review** (24h SLA) - Validates business need and data appropriateness
2. **Manager Review** (48h SLA) - Confirms resource allocation and project priority
3. **Compliance Review** (72h SLA) - Ensures regulatory compliance (GDPR, SOX, etc.)

### 4. Automated Provisioning
Once approved, automated provisioning executes:

1. **Azure AD Groups**: Creates dynamic groups based on department/role/project
2. **Fabric Workspace Access**: Assigns appropriate workspace permissions 
3. **Database Permissions**: Sets table/view level access rights
4. **Security Policies**: Applies row-level and column-level security rules
5. **Collibra Updates**: Records granted permissions in catalog
6. **User Notification**: Sends access confirmation with connection details

### 5. User Access & Monitoring
**User receives:**
- Connection details and credentials
- Code examples for data access
- Usage guidelines and restrictions

**Ongoing monitoring includes:**
- Real-time access validation at query time
- Usage pattern analysis and anomaly detection
- Automatic compliance reporting
- Permission review and renewal processes

### 6. Feedback & Optimization
System provides continuous improvement through:
- Usage analytics to identify popular data products
- Access pattern optimization recommendations  
- Periodic permission reviews and cleanup
- Policy updates based on usage insights
- Performance optimization suggestions

## Key Benefits

- **Reduced Access Time**: From days to hours (90% reduction)
- **Self-Service**: 80% of requests handled automatically
- **Full Audit Trail**: Complete governance and compliance tracking
- **Risk Reduction**: Automated security policy enforcement
- **User Experience**: Simple discovery and seamless access

## Usage Example
```python
from knauf_darc_connector import CollibraIntegratedConnector

# Connect with Collibra governance
connector = CollibraIntegratedConnector(
    sql_endpoint="your-fabric-endpoint.datawarehouse.fabric.microsoft.com",
    database="gold_lakehouse",
    collibra_config={
        'user_id': 'user@company.com',
        'api_key': 'your_collibra_api_key'
    }
)

# Access governed data products
with connector:
    # Automatic permission validation
    data = connector.execute_query_with_governance(
        "SELECT * FROM customer_insights WHERE region = 'EMEA'"
    )
    
    # Usage automatically logged to Collibra
    print(f"Retrieved {len(data)} records")
```

This streamlined process ensures governed, audited, and optimized data access while maintaining a simple user experience from discovery to consumption.