# Microsoft Fabric Lakehouse SQL Connection Setup on macOS

This README documents the steps to resolve SSL provider errors when connecting to Microsoft Fabric Lakehouse using pyodbc on macOS.

## Problem Statement

When trying to connect to Microsoft Fabric Lakehouse using pyodbc, you might encounter this error:
```
pyodbc.OperationalError: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]SSL Provider: [OpenSSL library could not be loaded, make sure OpenSSL 1.0, 1.1, or 3.0 is installed] (-1) (SQLDriverConnect)')
```

This occurs even when OpenSSL is installed because the ODBC driver cannot locate the OpenSSL libraries.

## Solution Overview

The solution involves:
1. Installing Homebrew package manager
2. Installing Microsoft ODBC Driver 18 for SQL Server
3. Properly configuring OpenSSL
4. Updating Python code to use the newer driver and set environment variables

## Step-by-Step Installation Commands

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Add Homebrew to PATH

```bash
echo >> /Users/$(whoami)/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/$(whoami)/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3. Install unixODBC (if not already installed)

```bash
brew install unixodbc
```

### 4. Add Microsoft SQL Server ODBC Driver repository

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
```

### 5. Install Microsoft ODBC Driver 18 and SQL Tools

```bash
brew install microsoft/mssql-release/msodbcsql18 microsoft/mssql-release/mssql-tools18
```

**Note:** You'll need to accept the license terms by typing `YES` when prompted.

### 6. Install and Link OpenSSL

```bash
brew install openssl
brew link openssl@3
```

### 7. Verify ODBC Drivers Installation

```bash
odbcinst -q -d
```

Expected output should include:
```
[ODBC Driver 17 for SQL Server]
[ODBC Driver 18 for SQL Server]
```

### 8. Check OpenSSL Installation

```bash
openssl version
which openssl
brew --prefix openssl
```

## Python Code Changes

### Required Python Packages

Make sure you have the following Python packages installed:
```bash
pip install pyodbc azure-identity
```

### Updated Python Code

The key changes in your Python script (`fabric_lakehouse_sql2.py`):

1. **Import os module and set environment variables:**
```python
import os
import struct
from itertools import chain, repeat

import pyodbc
from azure.identity import AzureCliCredential

# Set OpenSSL environment variables for macOS compatibility
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/openssl@3/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
os.environ['OPENSSL_ROOT_DIR'] = '/opt/homebrew/opt/openssl@3'
```

2. **Update connection string to use ODBC Driver 18:**
```python
connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_endpoint},1433;Database={database};Encrypt=Yes;TrustServerCertificate=No"
```

3. **Add error handling:**
```python
try:
    connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    rows = cursor.fetchall()
    print("Connection successful!")
    print("Query result:", rows)
    
    cursor.close()
    connection.close()
    print("Connection closed successfully.")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    print("Make sure you have:")
    print("1. ODBC Driver 18 for SQL Server installed")
    print("2. OpenSSL properly configured")
    print("3. Valid Azure credentials")
```

## Testing the Connection

Run your Python script to test the connection:
```bash
python fabric_lakehouse_sql2.py
```

Expected successful output:
```
Connection successful!
Query result: [(1,)]
Connection closed successfully.
```

## Alternative Method (Environment Variables in Terminal)

If you prefer not to set environment variables in Python code, you can set them in your terminal session:

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/openssl@3/lib:$DYLD_LIBRARY_PATH"
export OPENSSL_ROOT_DIR="/opt/homebrew/opt/openssl@3"
python fabric_lakehouse_sql2.py
```

## Troubleshooting

### Common Issues and Solutions

1. **"command not found: brew"**
   - Make sure Homebrew is properly installed and added to PATH
   - Restart your terminal or run: `eval "$(/opt/homebrew/bin/brew shellenv)"`

2. **"odbcinst: command not found"**
   - Install unixODBC: `brew install unixodbc`

3. **Still getting SSL errors**
   - Verify OpenSSL installation: `brew list openssl@3`
   - Check if OpenSSL is linked: `brew link openssl@3`
   - Ensure environment variables are set correctly

4. **Authentication errors**
   - Make sure you're logged into Azure CLI: `az login`
   - Verify your Azure credentials have access to the Fabric workspace

## Files in This Project

- `fabric_lakehouse_sql2.py` - Main script with fixes applied
- `fabric_lakehouse_sql2_fixed.py` - Alternative version with same fixes
- `README.md` - This documentation file

## System Requirements

- macOS (tested on Apple Silicon)
- Python 3.x
- Azure CLI (for authentication)
- Active Microsoft Fabric workspace access

## Dependencies

- `pyodbc` - Python ODBC database connectivity
- `azure-identity` - Azure authentication library
- Microsoft ODBC Driver 18 for SQL Server
- OpenSSL 3.x
- unixODBC

---

## Docker Installation (Required for Containerized Deployment)

If you want to use the Docker containerized version of this application, you'll need to install Docker:

### macOS Docker Installation

#### Option 1: Docker Desktop (Recommended)
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install the .dmg file (requires admin privileges)
3. Start Docker Desktop application

#### Option 2: Via Homebrew (requires admin privileges)
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker
```

#### Option 3: Without Admin Privileges
If you don't have admin access:
- Contact your system administrator to install Docker
- Use cloud-based development environments (GitHub Codespaces, Azure Cloud Shell)
- Use the native Python version without Docker

### Verify Docker Installation
```bash
docker --version
docker-compose --version
```

### Docker Files Available
- `Dockerfile` - Container definition (Debian-based)
- `Dockerfile.ubuntu` - Alternative Ubuntu-based container
- `docker-compose.yml` - Orchestration setup
- `DOCKER_DEPLOYMENT.md` - Detailed deployment guide

### Running Without Docker (Alternative)

If Docker installation is not possible, you can run the application directly:

#### Prerequisites
1. **Install Azure CLI** (required for authentication):
   ```bash
   # macOS
   brew install azure-cli
   
   # Or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Run the Python application**:
   ```bash
   python fabric_lakehouse_pandas.py
   ```

#### Troubleshooting Docker Build Issues

If you encounter Docker build errors:

1. **Ensure Docker Desktop is running** (check menu bar for Docker whale icon)

2. **Try the Ubuntu-based Dockerfile**:
   ```bash
   docker build -f Dockerfile.ubuntu -t fabric-lakehouse-app .
   ```

3. **Check Docker version**:
   ```bash
   docker --version
   docker-compose --version
   ```

---

**Last Updated:** September 24, 2025  
**Tested On:** macOS with Apple Silicon (M1/M2)