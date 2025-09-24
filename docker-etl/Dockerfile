# Dockerfile for the Python ETL pipeline
# Use the official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ETL script and the data directory into the container
COPY etl_pipeline.py .
COPY data ./data

# Command to run the ETL script when the container starts
CMD ["python", "etl_pipeline.py"]
