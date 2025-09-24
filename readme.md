# Dockerized Python ETL Pipeline

This repository contains a complete, automated, and Dockerized ETL (Extract, Transform, Load) pipeline. The pipeline reads data from a CSV file, transforms it, and loads it into a PostgreSQL database running in a separate Docker container.

The project demonstrates key concepts of Docker, including containerization, networking, and orchestration, all managed by a single bash script. This version enhances security by externalizing sensitive database credentials using environment variables.

Table of Contents
Prerequisites

Project Structure

Getting Started

Pipeline Components

Prerequisites
To run this pipeline, you need to have the following installed:

Docker: Ensure Docker Desktop or Docker Engine is installed and running on your machine.

Bash: A bash-compatible shell (standard on Linux and macOS, available via Git Bash on Windows).

Project Structure
The project is organized into the following directories and files:

.
├── README.md
├── data/
│   └── people-100.csv
├── docker-db/
│   └── Dockerfile
├── docker-etl/
│   ├── Dockerfile
│   ├── etl_pipeline.py
│   └── requirements.txt
└── run_pipeline.sh

Getting Started
Follow these steps to run the ETL pipeline:

Clone the repository:

git clone <your-repository-url>

cd <your-repository-name>

Add the data file: Place the provided people-100.csv file inside the data/ directory.

Run the automation script: The run_pipeline.sh script will handle everything for you.

chmod +x run_pipeline.sh
./run_pipeline.sh

The script will build the necessary Docker images, create a network, start the database container, wait for it to be ready, run the ETL container, and finally display a confirmation message upon success.

Pipeline Components
run_pipeline.sh
This bash script is the orchestrator. This version is more secure, as it now defines the database credentials at the top of the script and passes them to the containers as environment variables using the -e flag during the docker run command. This practice prevents sensitive data from being hardcoded into the images themselves.

docker-etl/etl_pipeline.py
This Python script is the core of the ETL process. It is configured to read the database credentials from environment variables, which aligns perfectly with the updated run_pipeline.sh script.

Dockerfiles
docker-db/Dockerfile: This image remains generic and reusable. The credentials are no longer set within the Dockerfile itself, but are instead provided at runtime.

docker-etl/Dockerfile: This image remains unchanged as it is designed to work with environment variables.

The combination of these files provides a robust and repeatable way to run your data pipeline in an isolated, containerized environment while adhering to a more secure configuration management approach.
