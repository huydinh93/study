from dotenv import load_dotenv
import os
import openai

dotenv_path = '/home/huydinh/study/sql_query/.env'

load_dotenv(dotenv_path)

def response_parser(response) -> str:
    return response.choices[0].message.content

def prompt(prompt: str, model: str = 'gpt-3.5-turbo-1106', **kwargs) -> str:
    
    response = openai.chat.completions.create(
                model=model,
                messages=[
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                )
    print(response)
    return response_parser(response)

def add_prompt(prompt: str, prompt_add: str,  prompt_input: str, prompt_delimiter: str = '',) -> str:
    new_prompt = prompt + '\n' + prompt_add + '\n' + '\n' + prompt_input + '\n' + prompt_delimiter
    return new_prompt
    