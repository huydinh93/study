from dotenv import load_dotenv
import os
import logging
from modules.db import PostgresManager
import autogen

config_list_gpt3 = autogen.config_list_from_json(
    env_or_file="/home/huydinh/study/autogen_demo/OAI_CONFIG_LIST.json",  # or OAI_CONFIG_LIST.json if file extension is added
    filter_dict={
        "model": {
            "gpt-3.5-turbo",
        }
    },
)
config_list_gpt4 = autogen.config_list_from_json(
    env_or_file="/home/huydinh/study/autogen_demo/OAI_CONFIG_LIST.json",  # or OAI_CONFIG_LIST.json if file extension is added
    filter_dict={
        "model": {
            "gpt-4",
        }
    },
)

gpt4_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 120,
    "functions": [
            {
                "name": "run_sql",
                "description": "run sql queries against Postgres database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to run against Postgres database.",
                        },
                    },
                    "required": ["sql"],
                },
            }
        ]
}
manager_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 120,
}
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
        
        prompt = f'write a sql query {prompt} using this {table_def}'
        print(f"Current Prompt with table def: {prompt}", type(prompt))
    # <code> construct a query to get the answer include the table name and table definition
    # delimiter = '----------'
        user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message="A human admin. Interact with the Engineer to discuss the plan",
        code_execution_config=False,
        )
        
        engineer = autogen.AssistantAgent(
        name="Engineer",
        llm_config=gpt4_config,
        system_message="""Engineer. You follow an approved plan. You write sql code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
        """,
        )
        
        analyst = autogen.AssistantAgent(
        name="Analyst",
        llm_config=gpt4_config,
        system_message="""Analyst. You follow an approved plan. You run SQL query from Engineer and generate the""",
        function_map={"run_sql": db_manager.run_sql},
        code_execution_config={"workdir": None}
        )
        
        groupchat = autogen.GroupChat(
        agents=[user_proxy, engineer, analyst], messages=[], max_round=50
        )
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=manager_config)
        
        user_proxy.initiate_chat(
        manager,
        message=prompt
        )
    # <code> run the query and get the answer
    
if __name__ == "__main__":
    main()
