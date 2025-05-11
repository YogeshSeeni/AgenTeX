from openai import OpenAI
from dotenv import load_dotenv
import os


def parse_image(image_url: str) -> str:
    load_dotenv()

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this math problem in detailed english to later generate latex code"},
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                },
            ],
        }],
    )

    print(response.output_text)
