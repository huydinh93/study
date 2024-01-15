from dotenv import load_dotenv
import os
import logging
from modules.db import PostgresManager
# Load environment variables
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)

DB_URL = os.getenv('POSTGRES_CONNECTION_STRING')

with PostgresManager(DB_URL) as db_manager:
    result = db_manager.run_sql('select * from analytics_common.dim_country limit 1')
    print(result)
    
def main():
    
    prompt = input("Enter your question: ")
    
    # connect to postgres db and get all tables name and schema
    with PostgresManager(DB_URL) as db_manager:
        tables = db_manager.get_all_tables()
        print(f"All tables: {tables}")
    
    # get all tables definition
    for table in tables:
        with PostgresManager(DB_URL) as db_manager:
            table_definition = db_manager.get_table_definition(table)
            print(f"Definition of {table}: {table_definition}")
    
