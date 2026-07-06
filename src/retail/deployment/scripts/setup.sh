#!/bin/bash
# Setup script for the Retail AI Agent

set -e

echo "Setting up Retail AI Agent..."

# Create data directories
mkdir -p data/source data/staging data/warehouse

# Download data
echo "Downloading UCI Online Retail dataset..."
python scripts/download_data.py

# Clean data
echo "Cleaning data..."
python -c "from retail.data.staging.cleaner import clean_and_save; clean_and_save()"

# Build warehouse
echo "Building data warehouse..."
python scripts/build_warehouse.py

echo "Setup complete!"