#!/bin/bash

# Build and run the Docker container for Fabric Lakehouse application

echo "Building Docker image..."
docker build -t fabric-lakehouse-app .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "To run the container:"
    echo "1. Copy .env.example to .env and fill in your Azure credentials"
    echo "2. Run: docker-compose up"
    echo ""
    echo "Or run directly with Docker:"
    echo "docker run --env-file .env fabric-lakehouse-app"
else
    echo "❌ Docker build failed!"
    exit 1
fi