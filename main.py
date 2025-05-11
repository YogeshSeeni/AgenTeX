from openai import OpenAI
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace
from models import ImageParser, LatexOutput
from tools import parse_image
import asyncio

load_dotenv()

# Agent #1: parses image
image_parser_agent = Agent(
    name="ImageParserAgent",
    instructions=(
        "Parse the image containing mathematical content and return a JSON object with 'is_valid' and 'text' fields. "
        "IMPORTANT: Transcribe all mathematical expressions exactly as they appear in the image without solving, "
        "simplifying, or modifying them. Do not add any mathematical logic or attempt to solve equations. "
        "Your task is purely to convert the visual content to text accurately with all symbols and expressions preserved verbatim."
        "Do not add any commentary or formatting or solve the problem."
    ),
    output_type=ImageParser,
    tools=[parse_image],
    model="gpt-4o"
)

# Agent #2: generates LaTeX code
latex_generator_agent = Agent(
    name="LatexGeneratorAgent",
    instructions=(
        "Do not solve the problem, just return the LaTeX translation of the problem."
        "Convert the parsed text into LaTeX code. Ensure proper formatting and mathematical notation. "
        "IMPORTANT: Transcribe all mathematical expressions exactly as provided in the input text without solving, "
        "simplifying, or modifying them. Do not add any mathematical logic, interpretations, or attempt to solve equations. "
        "Your task is purely to convert the text to proper LaTeX syntax while preserving the exact mathematical content verbatim."
    ),
    output_type=LatexOutput,
    model="gpt-4o"
)

# Example image URL - replace with your actual image URL
image_url = "https://www.firstforwomen.com/wp-content/uploads/sites/2/2018/02/math-iq-test.jpg?w=750&h=562&crop=1&quality=86&strip=all"



async def main():
    with trace("Deterministic flow"):
        # Run the agents in sequence
        parsed_result = await Runner.run(image_parser_agent, image_url)
        print("Parsed result:", parsed_result.final_output.text)

        # Generate LaTeX code from the parsed text
        latex_result = await Runner.run(latex_generator_agent, parsed_result.final_output.text)
        print("Generated LaTeX:", latex_result.final_output.latex_code)

if __name__ == "__main__":
    asyncio.run(main())