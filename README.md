# Knauf DARC Data Connector

A Python package for connecting to Microsoft Fabric Lakehouse with flexible authentication methods.

## Features

- **Flexible Azure Authentication**: Support for Service Principal, Azure CLI, Default Azure Credential, and Managed Identity
- **Easy-to-use Connector**: Simple interface for Microsoft Fabric Lakehouse connections
- **Pandas Integration**: Direct integration with pandas for data analysis
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux
- **Docker Support**: Containerized deployment options
- **Structured Architecture**: Well-organized codebase following Python best practices

## Installation

### Prerequisites

1. **ODBC Driver 18 for SQL Server**
   - **Windows**: Download from [Microsoft](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - **macOS**: `brew install msodbcsql18`
   - **Linux**: Follow [Microsoft's installation guide](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

2. **Python 3.8+**

3. **Azure Authentication** (choose one):
   - Azure CLI: `az login`
   - Service Principal credentials via environment variables
   - Managed Identity (when running on Azure)

### Install Package

```bash
# Clone the repository
git clone https://github.com/singhknauf/Knauf-DARC-DataConnector.git
cd Knauf-DARC-DataConnector

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

### Basic Usage

```python
from knauf_darc_connector import FabricLakehouseConnector

# Initialize connector
connector = FabricLakehouseConnector(
    sql_endpoint="your-endpoint.datawarehouse.fabric.microsoft.com",
    database="your-database"
)

# Use context manager for automatic connection handling
with connector:
    # Execute query and get pandas DataFrame
    df = connector.execute_query("SELECT TOP 100 * FROM dbo.orders")
    print(df.head())
    
    # Or use the convenience method for table analysis
    connector.get_table_info("orders", schema="dbo")
```

### Authentication Methods

The connector automatically tries multiple authentication methods in order:

#### 1. Service Principal (Environment Variables)
```bash
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
```

#### 2. Azure CLI
```bash
az login
# The connector will automatically use these credentials
```

#### 3. Custom Credential
```python
from azure.identity import AzureCliCredential
from knauf_darc_connector import FabricLakehouseConnector

# Use specific credential type
credential = AzureCliCredential()
connector = FabricLakehouseConnector(
    sql_endpoint="your-endpoint",
    database="your-database",
    credential=credential
)
```

## Project Structure

```
Knauf-DARC-DataConnector/
├── src/
│   └── knauf_darc_connector/           # Main package
│       ├── __init__.py
│       ├── auth/                       # Authentication modules
│       │   ├── __init__.py
│       │   └── azure_auth.py
│       └── connectors/                 # Database connectors
│           ├── __init__.py
│           └── fabric_connector.py
├── scripts/                            # Example and utility scripts
│   ├── flexible_auth_example.py        # Main usage example
│   ├── pandas_example.py               # Pandas-focused example
│   ├── build.sh                        # Build script
│   └── legacy/                         # Original scripts (for reference)
├── tests/                              # Unit tests
│   ├── conftest.py
│   └── test_auth.py
├── docker/                             # Docker configuration
│   ├── Dockerfile
│   ├── Dockerfile.ubuntu
│   ├── docker-compose.yml
│   └── DOCKER_DEPLOYMENT.md
├── config/                             # Configuration templates
│   └── config.template.yaml
├── docs/                               # Documentation
├── requirements.txt                    # Python dependencies
├── setup.py                           # Package setup
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]  # Install with development extras
```

### Running Examples

```bash
# Run the flexible authentication example
python scripts/flexible_auth_example.py

# Run the pandas-focused example
python scripts/pandas_example.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src/knauf_darc_connector
```

### Code Quality

```bash
# Format code
black src/ tests/ scripts/

# Lint code
flake8 src/ tests/ scripts/

# Type checking
mypy src/
```

## Docker Deployment

For containerized deployments, see the comprehensive guide in `docker/DOCKER_DEPLOYMENT.md`.

### Quick Docker Setup

```bash
cd docker/
docker-compose up --build
```

## Configuration

Copy the configuration template and customize:

```bash
cp config/config.template.yaml config/config.yaml
# Edit config.yaml with your settings
```

## Troubleshooting

### Common Issues

1. **ODBC Driver Issues**: Ensure ODBC Driver 18 for SQL Server is installed
2. **macOS OpenSSL**: The package automatically configures OpenSSL paths for Homebrew installations
3. **Authentication Errors**: Check Azure credentials and permissions
4. **Connection Timeouts**: Verify network access to Fabric workspace

### Debug Mode

Enable detailed logging by setting the environment variable:

```bash
export PYTHONPATH="${PYTHONPATH}:./src"
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the project structure
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write unit tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the DARC team at darc@knauf.com

## Changelog

### v0.1.0
- Initial release
- Flexible Azure authentication
- Fabric Lakehouse connector
- Docker support
- Comprehensive test suite