from dotenv import load_dotenv
import logging
from openai import OpenAI
import base64
import json
import subprocess
import os

load_dotenv()
logging.basicConfig(filename='log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
# image_path = "/home/huydinh/study/webscraping/screenshots/2024-01-11T05-17-13-479Z/screen1.png"

# Getting the base64 string

client = OpenAI()

prompt = input("Question: ")
logging.info(f'Prompt: {prompt}')

main_message = [
        {
        "role": "system",
        "content": "You are a web crawler. Your job is to give the user a real URL to go to in order to find the answer to their question. Respond in the following JSON format: {\"url\": \"put url here\"}",
        },
        {
        "role": "user",
        "content": prompt
        }
        ]
max_attempts = 3
attempt = 0
while True:
    while attempt < max_attempts:
        attempt += 1
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=main_message,
            max_tokens=300,
            response_format={"type": "json_object"},
            seed=42123
            )

        logging.info(f'Response {response}')

        message = response.choices[0].message
        message_content = json.loads(message.content)
        url = message_content['url']
        main_message = main_message.append({
            "role": "assistant",
            "content": url
        })
        logging.info(message_content)
        print(url)

        subprocess.run(["node", "screenshot.js", url])


        def get_first_screenshot_of_latest_page(screenshot_folder):
            logging.info(f"Getting first screenshot from latest page in folder {screenshot_folder}")
            # Get all subfolders in the screenshots folder
            subfolders = [f.path for f in os.scandir(screenshot_folder) if f.is_dir()]

            if not subfolders:
                logging.warning("No subfolders found in screenshots folder")
                return None

            # Find the latest subfolder based on naming convention (assuming timestamp format '2024-01-11T05-17-13-479Z' format)
            # latest_subfolder = max(subfolders, key=lambda f: int(os.path.basename(f).replace('page', '')))
            latest_subfolder = sorted(subfolders, reverse=True)[0]
            # Construct the path to the first screenshot in the latest subfolder
            first_screenshot_path = os.path.join(latest_subfolder, 'screen1.png')

            if os.path.exists(first_screenshot_path):
                logging.info(f"Found first screenshot at {first_screenshot_path}")
                return first_screenshot_path
            else:
                logging.warning(f"First screenshot not found in {latest_subfolder}")
                return None

        screenshot_folder = "/home/huydinh/study/webscraping/screenshots"
        image_path = get_first_screenshot_of_latest_page(screenshot_folder)
        base64_image = encode_image(image_path)
        message = [[
                {
                "role": "system",
                "content": "You job is to answer the question of the user only base on the given screenshots of a website. Answer the user as an assistant, but don't tell that the information is from a screenshot or an image. If you can't answer the question in the screenshots, only response with the code 'ANSWER_NOT_FOUND' and nothing else"
                }]
                + 
                [{
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": prompt,
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                    },
                ],
                }
            ]]

        logging.info(f"Prompt: {message}")

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=message,
            max_tokens=1024,
            )

        logging.info(f'Response {response}')

        message = response.choices[0].message
        message_content = message.content

        logging.info(message_content)

        if "ANSWER_NOT_FOUND" in message_content:
            print("Answer not found")
            main_message.append(
                    {
                    "role": "user",
                    "content": "I was unable to find the answer to my question. Please try again with a different url."
                    }
                    )
            logging.info(f"main_message: {main_message} ")
        else:
            print(f"GPT answer: {message_content}")
            prompt = input("User :")
            main_message.append(
                    {
                    "role": "user",
                    "content": prompt
                    }
                    )
            logging.info(f"main_message: {main_message} ")