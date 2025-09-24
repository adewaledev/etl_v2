import pandas as pd
import psycopg2
import os
from datetime import date
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Load .env file for local development
# In Docker, the -e environment variables override these automatically
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Database connection details (no defaults for production safety)
# -----------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATA_PATH = '/app/data/people-100.csv'  # path inside Docker container

# Fail immediately if any environment variable is missing
required_vars = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD
}

missing_vars = [var for var, val in required_vars.items() if not val]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}")

# -----------------------------------------------------------------------------
# Step 1: Extract
# -----------------------------------------------------------------------------


def extract():
    print("Step 1: Extracting data from CSV...")
    try:
        df = pd.read_csv(DATA_PATH)
        print("Extraction successful. Shape:", df.shape)
        return df
    except FileNotFoundError:
        print(f"Error: The file {DATA_PATH} was not found.")
        exit(1)

# -----------------------------------------------------------------------------
# Step 2: Transform
# -----------------------------------------------------------------------------


def transform(df):
    print("Step 2: Transforming data...")

    # Standardize column names
    df.columns = [col.lower().replace(' ', '_').replace(
        '.', '').replace('-', '_') for col in df.columns]

    # Rename 'sex' → 'gender'
    df.rename(columns={'sex': 'gender'}, inplace=True)

    # Convert date_of_birth to datetime
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])

    # Calculate age
    today = date.today()
    df['age'] = df['date_of_birth'].apply(
        lambda dob: today.year - dob.year -
        ((today.month, today.day) < (dob.month, dob.day))
    )

    # Clean phone numbers
    df['phone'] = df['phone'].astype(str).str.replace(r'[()x.\-]', '', regex=True)\
        .str.replace(r'^\+', '')\
        .str.replace(r'^[0-9]{3}', '', regex=True)

    print("Transformation successful.")
    return df

# -----------------------------------------------------------------------------
# Step 3: Load
# -----------------------------------------------------------------------------


def load(df):
    print("Step 3: Loading data into PostgreSQL...")
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS people_data (
            index INT,
            user_id VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            gender VARCHAR(50),
            email VARCHAR(255),
            phone VARCHAR(255),
            date_of_birth DATE,
            job_title VARCHAR(255),
            age INT
        );
        """
        cur.execute(create_table_query)
        conn.commit()

        # Insert data row by row
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO people_data (
                index, user_id, first_name, last_name, gender, email, phone, date_of_birth, job_title, age
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data_to_insert = (
                row['index'],
                row['user_id'],
                row['first_name'],
                row['last_name'],
                row['gender'],
                row['email'],
                row['phone'],
                row['date_of_birth'],
                row['job_title'],
                row['age']
            )
            cur.execute(insert_query, data_to_insert)

        conn.commit()
        print("Loading successful. Data inserted into 'people_data' table.")

        # Verify total rows
        cur.execute("SELECT COUNT(*) FROM people_data;")
        count = cur.fetchone()[0]
        print(f"Total rows in table: {count}")

    except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
        print(f"Database error: {e}")
        exit(1)
    finally:
        if conn:
            cur.close()
            conn.close()


# -----------------------------------------------------------------------------
# Main ETL Orchestration
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    df = extract()
    if not df.empty:
        transformed_df = transform(df)
        load(transformed_df)

    print("\nETL pipeline finished.")
