from openai import OpenAI
from dotenv import load_dotenv
import os
from agents import Agent, Runner
from models import ImageParser
from tools import parse_image
load_dotenv()

# Agent #1: generates code
image_parser_agent = Agent(
    name="ImageParserAgent",
    instructions=(
        "Parse the image and return a JSON object with 'is_valid' and 'text' fields."
    ),
    output_type=ImageParser,
    tools=[parse_image],
    model="gpt-4o"
)

# Example image URL - replace with your actual image URL
image_url = "https://www.firstforwomen.com/wp-content/uploads/sites/2/2018/02/math-iq-test.jpg?w=750&h=562&crop=1&quality=86&strip=all"

# Run the agent using Runner
result = Runner.run_sync(image_parser_agent, image_url)
print("Parsed result:", result.final_output)

