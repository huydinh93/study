from dotenv import load_dotenv
import os
import logging
from modules.db import PostgresManager
from modules import llm
# Load environment variables
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)

DB_URL = os.getenv('POSTGRES_CONNECTION_STRING')

# with PostgresManager(DB_URL) as db_manager:
#     result = db_manager.run_sql('select * from analytics_common.dim_country limit 1')
#     print(result)
    
def main():
    prompt = input("Enter your question: ")
    logging.info(f'Prompt: {prompt}, type: {type(prompt)}')
    # <code> connect to postgres db and get all tables name and schema
    with PostgresManager(DB_URL) as db_manager:
        tables = db_manager.get_all_tables()
        print(f"All tables: {tables}")
    # <code> get all tables definition
        for table in tables:
            table_definition = db_manager.get_table_definition(table)
            logging.info(f"Definition of {table}: {table_definition}, type: {type(table_definition)}")
            table_def = f"Definition of {table}: {table_definition}"
            print(f"Definition of {table}: {table_definition}")
    # <code> construct a query to get the answer include the table name and table definition
    # delimiter = '----------'
    prompt =llm.add_prompt('write a sql query ' + prompt, 'using this'  + table_def, 'create sql query here: ')
    print(f'Current prompt : {prompt}')
    sql_query = llm.prompt(prompt)
    print(sql_query)
    
    with PostgresManager(DB_URL) as db_manager:
        result = db_manager.run_sql(sql_query)
        print(result)
    # <code> run the query and get the answer
    
if __name__ == "__main__":
    main()
    