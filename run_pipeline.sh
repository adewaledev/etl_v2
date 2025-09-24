#!/bin/bash

# ==============================================================================
# ETL Pipeline Automation Script (with .env support)
#
# This script automates the setup and execution of a Dockerized ETL pipeline.
# It loads sensitive database credentials from a .env file to avoid hardcoding.
#
# Steps:
# 1. Load environment variables from .env
# 2. Check for required CSV data file
# 3. Clean up existing Docker containers and network
# 4. Create a dedicated Docker network
# 5. Build Docker images
# 6. Run the database container with credentials from .env
# 7. Wait until the database is ready
# 8. Run the ETL container with credentials from .env
# 9. Verify the pipeline by querying the database
# ==============================================================================
set -e  # Exit immediately if a command fails

# --- Step 1: Load environment variables from .env ---
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "--- Loaded environment variables from .env ---"
else
    echo "Error: .env file not found. Please create one with DB_HOST, DB_NAME, DB_USER, DB_PASSWORD."
    exit 1
fi

# --- Step 2: Check for required files ---
echo "--- Checking for data file and setting up directories ---"
CSV_FILE="people-100.csv"
DATA_DIR="data"
ETL_DIR="docker-etl"

mkdir -p "$DATA_DIR"

if [ ! -f "$DATA_DIR/$CSV_FILE" ]; then
    echo "Error: The file '$CSV_FILE' was not found in the '$DATA_DIR' directory."
    echo "Please place the provided CSV file in the '$DATA_DIR' folder and try again."
    exit 1
fi

echo "Creating data directory within ETL source..."
mkdir -p "$ETL_DIR/$DATA_DIR/"

echo "Copying data file to ETL source directory..."
cp "$DATA_DIR/$CSV_FILE" "$ETL_DIR/$DATA_DIR/"

# --- Step 3: Clean up existing resources ---
echo "--- Cleaning up existing Docker containers and network ---"
docker stop db-container || true
docker stop etl-container || true
docker rm db-container || true
docker rm etl-container || true
docker network rm etl_network || true

# --- Step 4: Create Docker network ---
echo "--- Creating Docker network 'etl_network' ---"
docker network create etl_network

# --- Step 5: Build Docker images ---
echo "--- Building database Docker image ---"
docker build -t db-image ./docker-db

echo "--- Building ETL pipeline Docker image ---"
docker build -t etl-image ./docker-etl

# --- Step 6: Run the database container ---
echo "--- Starting database container 'db-container' ---"
docker run -d \
    --name db-container \
    --network etl_network \
    -e POSTGRES_DB="$DB_NAME" \
    -e POSTGRES_USER="$DB_USER" \
    -e POSTGRES_PASSWORD="$DB_PASSWORD" \
    db-image

# --- Step 7: Wait for the database to be ready ---
echo "--- Waiting for database to be ready (up to 30 seconds) ---"
MAX_TRIES=30
for i in $(seq 1 $MAX_TRIES); do
    if docker exec db-container pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
        echo "Database is ready!"
        break
    else
        echo "Waiting for database... ($i/$MAX_TRIES)"
        sleep 1
    fi

    if [ $i -eq $MAX_TRIES ]; then
        echo "Error: Database did not become ready within the timeout period."
        exit 1
    fi
done

# --- Step 8: Run the ETL pipeline container ---
echo "--- Starting ETL pipeline container 'etl-container' ---"
docker run --rm \
    --name etl-container \
    --network etl_network \
    -e DB_HOST="$DB_HOST" \
    -e DB_NAME="$DB_NAME" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    etl-image

# --- Step 9: Verify data in the database ---
echo "--- Verifying data in the database ---"
docker exec db-container psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM people_data;"

echo "---------------------------------------------------"
echo "ETL Pipeline completed successfully!"
echo "The data has been loaded into the 'people_data' table in the PostgreSQL container."
echo "---------------------------------------------------"

# --- Final instructions ---
echo ""
echo "To clean up all the resources, you can run:"
echo "docker stop db-container etl-container && docker rm db-container etl-container && docker network rm etl_network"
