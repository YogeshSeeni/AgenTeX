from openai import OpenAI
from dotenv import load_dotenv
import os
from models import ImageParser, LatexOutput
from agents import function_tool

@function_tool
def parse_image(image_url: str) -> ImageParser:
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
                    "image_url": image_url,
                },
            ],
        }],
    )

    # Return a proper ImageParser object
    return ImageParser(
        is_valid=True,  # You might want to add validation logic here
        text=response.output_text
    )