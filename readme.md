# Dockerized Python ETL Pipeline

This repository contains a complete, automated, and Dockerized **ETL (Extract, Transform, Load) pipeline**.  
The pipeline reads data from a CSV file, transforms it, and loads it into a PostgreSQL database running in a separate Docker container.  

The project demonstrates key concepts of **Docker**, including containerization, networking, and orchestration — all managed by a single bash script.  
This version enhances security by **storing sensitive database credentials in a `.env` file** instead of hardcoding them.  

------------------------------------------------------------------

## Table of Contents

- [Prerequisites] (#-prerequisites)  
- [Project Structure] (#-project-structure)  
- [Environment Variables] (#-environment-variables)  
- [Getting Started] (#-getting-started)  
- [Pipeline Components] (#-pipeline-components)  

------------------------------------------------------------------

🔧 Prerequisites
To run this pipeline, you need:  

- **Docker**: Ensure Docker Desktop or Docker Engine is installed and running.  
- **Bash**: A bash-compatible shell (standard on Linux/macOS, available via Git Bash on Windows).  

------------------------------------------------------------------

## Project Structure

```text
.
├── README.md
├── .env                 # Environment variables (DB credentials)
├── data/
│   └── people-100.csv   # Input dataset
├── docker-db/
│   └── Dockerfile       # PostgreSQL image setup
├── docker-etl/
│   ├── Dockerfile       # ETL image setup
│   ├── etl_pipeline.py  # ETL process script
│   └── requirements.txt # Python dependencies
└── run_pipeline.sh      # Orchestration script
```

------------------------------------------------------------------

## Environment Variables

All sensitive configuration is stored in a `.env` file at the root of the project.  
Example `.env` file:  

```sh
DB_HOST=db
DB_NAME=etldb
DB_USER=user
DB_PASSWORD=pass
DB_PORT=5432
```

## Getting Started

1. **Clone the repository**  

    ```git
      git clone https://github.com/adewaledev/etl_v2
      cd etl_v2
    ```

2. **Set up environment variables**  
   Copy `.env.example` to `.env` and adjust values if needed:  
   cp .env.example .env

3. **Add the data file**  
   Place the provided `people-100.csv` inside the `data/` directory.  

4. **Run the automation script**  
   chmod +x run_pipeline.sh
   ./run_pipeline.sh

The script will:  
✅ Build the Docker images  
✅ Create a Docker network  
✅ Start the PostgreSQL container (using credentials from `.env`)  
✅ Run the ETL container (reads same `.env`)  
✅ Load transformed data into the database  
✅ Show confirmation of success  

------------------------------------------------------------------

## Pipeline Components

**.env**
Holds all database credentials and connection details.  

## **run_pipeline.sh**

- Orchestrates the pipeline.  
- Loads environment variables from `.env`.  
- Passes them securely to containers.  

## **docker-etl/etl_pipeline.py**

- Core ETL logic.  
- Reads credentials from environment variables.  
- Extracts → Transforms → Loads into Postgres.  

## **Dockerfiles**

- **docker-db/Dockerfile** → Builds PostgreSQL container (generic, no credentials).  
- **docker-etl/Dockerfile** → Builds ETL container with Python dependencies.  

------------------------------------------------------------------

## With this setup, the pipeline is  

- **Secure** → credentials externalized in `.env`.  
- **Reproducible** → same results every run.  
- **Isolated** → runs fully inside Docker containers.
