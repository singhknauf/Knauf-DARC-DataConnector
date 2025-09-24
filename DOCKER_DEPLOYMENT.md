# Docker Deployment Guide

This guide explains how to deploy the Fabric Lakehouse application using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Azure credentials (Service Principal or Managed Identity)
- Access to Microsoft Fabric Lakehouse

## Quick Start

### 1. Setup Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your Azure credentials
nano .env
```

Fill in your Azure credentials:
```
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_TENANT_ID=your-tenant-id-here
```

### 2. Build and Run with Docker Compose (Recommended)

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### 3. Build and Run with Docker Commands

```bash
# Build the image
docker build -t fabric-lakehouse-app .

# Run the container
docker run --env-file .env fabric-lakehouse-app
```

### 4. Use the Build Script

```bash
# Make executable and run
chmod +x build.sh
./build.sh
```

## Deployment Options

### Local Development
```bash
docker-compose up
```

### Azure Container Instances
```bash
# Build and push to registry
docker build -t myregistry.azurecr.io/fabric-lakehouse-app .
docker push myregistry.azurecr.io/fabric-lakehouse-app

# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name fabric-lakehouse-app \
  --image myregistry.azurecr.io/fabric-lakehouse-app \
  --environment-variables \
    AZURE_CLIENT_ID=your-client-id \
    AZURE_TENANT_ID=your-tenant-id \
  --secure-environment-variables \
    AZURE_CLIENT_SECRET=your-client-secret
```

## Security Best Practices

- Never commit .env file to version control
- Use Managed Identity when possible
- Rotate secrets regularly
- Run containers as non-root user (already configured)