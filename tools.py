from openai import OpenAI
from dotenv import load_dotenv
import os
from models import ImageParser, LatexOutput, MathClassification, MathSolution
from agents import function_tool

@function_tool
def parse_image(image_url: str) -> ImageParser:
    load_dotenv()

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.responses.create(
        model="gpt-4o",
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

@function_tool
def classify_math_content(text: str) -> MathClassification:
    """Classifies mathematical content by type, difficulty, and identifies key concepts"""
    load_dotenv()
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a mathematical content classifier. Given a mathematical text or problem, classify it by type, difficulty level, identify key mathematical concepts involved, and provide a brief description."
            },
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    
    result = response.choices[0].message.content
    
    # Parse JSON and return MathClassification object
    import json
    data = json.loads(result)
    
    return MathClassification(
        math_type=data.get("math_type", "unclassified"),
        difficulty_level=data.get("difficulty_level", "medium"),
        concepts=data.get("concepts", []),
        description=data.get("description", "")
    )

@function_tool
def generate_solution(text: str) -> MathSolution:
    """Generates a step-by-step solution for a mathematical problem"""
    load_dotenv()
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a mathematics expert. Given a mathematical problem, provide a clear step-by-step solution with detailed explanations."
            },
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    
    result = response.choices[0].message.content
    
    # Parse JSON and return MathSolution object
    import json
    data = json.loads(result)
    
    return MathSolution(
        solution_steps=data.get("solution_steps", []),
        final_answer=data.get("final_answer", ""),
        explanation=data.get("explanation", "")
    )