from dotenv import load_dotenv
import logging
from openai import OpenAI
import base64

load_dotenv()
logging.basicConfig(filename='log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "/home/huydinh/study/webscraping/screenshots/2024-01-11T05-17-13-479Z/screen1.png"

# Getting the base64 string
base64_image = encode_image(image_path)

client = OpenAI()

prompt = "What is in this image?"

message = [
        {
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
    ]
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=message,
    max_tokens=300,
    )

logging.info(f'Response {response}')

message = response.choices[0].message
message_content = message.content

print(message_content)