import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import text
from snowflake.snowpark import Session
from snowflake.connector.pandas_tools import pd_writer
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def get_snowflake_session():
    logging.info("Getting Snowflake session")
    return Session.builder.configs({
        "account": os.getenv('SNOWFLAKE_ACCOUNT'),
        "user": os.getenv('SNOWFLAKE_USER'),
        "password": os.getenv('SNOWFLAKE_PASSWORD'),
        "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
        "database": os.getenv('SNOWFLAKE_DATABASE'),
        "schema": os.getenv('SNOWFLAKE_SCHEMA'),
        "role": os.getenv('SNOWFLAKE_ROLE')
    }).create()

def get_postgres_engine():
    logging.info("Creating PostgreSQL engine")
    return sqlalchemy.create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
                                    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")

def convert_schema(snowflake_schema):
    logging.info("Converting Snowflake schema to PostgreSQL schema")
    type_mapping = {
        "NUMBER": "NUMERIC",
        "FLOAT": "REAL",
        "FLOAT4": "REAL",
        "FLOAT8": "DOUBLE PRECISION",
        "VARCHAR": "VARCHAR",  # You might want to handle the length part separately
        "STRING": "TEXT",
        "TEXT": "TEXT",
        "CHAR": "CHAR",
        "BOOLEAN": "BOOLEAN",
        "DATE": "DATE",
        "DATETIME": "TIMESTAMP",
        "TIMESTAMP_LTZ": "TIMESTAMP WITH TIME ZONE",
        "TIMESTAMP_NTZ": "TIMESTAMP",
        "TIMESTAMP_TZ": "TIMESTAMP WITH TIME ZONE",
        "TIME": "TIME",
        "BINARY": "BYTEA",
        "VARBINARY": "BYTEA"
    }

    columns = []
    for column_info in snowflake_schema:
        column_name = column_info['name']
        base_type = column_info['type'].split('(')[0]
        postgres_type = type_mapping.get(base_type.upper(), "TEXT")
        columns.append(f"\"{column_name.lower()}\" {postgres_type}")
    return ', '.join(columns)

def get_table_schema(snowflake_session, table):
    logging.info(f"Getting schema for table {table}")
    result = snowflake_session.sql(f"DESC TABLE {table}").collect()

    schema_data = []
    for row in result:
        schema_data.append({
            'name': row['name'],
            'type': row['type'],
            # ... [rest of the schema extraction]
        })

    return schema_data

def main():
    try:
        with get_snowflake_session() as snowflake_session, get_postgres_engine().connect() as postgres_connection:
            # Prompt user for Snowflake table name and convert to lowercase
            snowflake_table = input("Enter the name of the Snowflake table to copy: ").lower()

            # Parse the Snowflake table string into database, schema, and table components
            try:
                db, schema, table = snowflake_table.split('.')
            except ValueError:
                raise ValueError("Invalid Snowflake table format. Expected format: 'database.schema.table'")
            
            # Log the parsed names
            logging.info(f"Database: {db}, Schema: {schema}, Table: {table}")

            # Collecting data from Snowflake
            logging.info("Collecting data from Snowflake...")
            df = snowflake_session.sql(f"SELECT * FROM {snowflake_table}").collect()
            

            # Convert to DataFrame if necessary
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            df.columns = [c.lower() for c in df.columns]
            # Retrieve the schema for the specified table
            schema_data = get_table_schema(snowflake_session, snowflake_table)

            # Ensure PostgreSQL connection is established
            if not postgres_connection:
                raise Exception("PostgreSQL connection failed.")

            # Create schema in PostgreSQL if it does not exist
            postgres_connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            logging.info(f"Schema '{schema}' created successfully in PostgreSQL")

            # Create table in PostgreSQL
            create_table_query = f"CREATE TABLE IF NOT EXISTS {schema}.{table} ({convert_schema(schema_data)});"
            postgres_connection.execute(text(create_table_query))
            logging.info(f"Table '{table}' created successfully in schema '{schema}' in PostgreSQL")

            # Insert data into PostgreSQL table
            df.to_sql(name=table, con=postgres_connection, schema=schema, if_exists='append', index=False)
            logging.info("Data inserted into PostgreSQL.")

            # Commit the transaction
            postgres_connection.commit()
            logging.info("Transaction committed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()


