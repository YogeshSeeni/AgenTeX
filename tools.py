from openai import OpenAI
from dotenv import load_dotenv
import os
from models import ImageParser, LatexOutput, MathTypeClassification, StepByStepSolution
from agents import function_tool
import json
import re

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
def validate_latex(latex_code: str) -> dict:
    """
    Validates if the LaTeX code is well-formed by checking for basic syntax errors.
    """
    # Check for balanced braces
    open_braces = latex_code.count('{')
    close_braces = latex_code.count('}')
    
    # Check for balanced environments
    begin_count = len(re.findall(r'\\begin\{', latex_code))
    end_count = len(re.findall(r'\\end\{', latex_code))
    
    # Check for other common errors
    unclosed_commands = re.findall(r'\\[a-zA-Z]+\{[^}]*$', latex_code)
    
    issues = []
    if open_braces != close_braces:
        issues.append(f"Unbalanced braces: {open_braces} opening vs {close_braces} closing")
    
    if begin_count != end_count:
        issues.append(f"Unbalanced environments: {begin_count} \\begin vs {end_count} \\end")
    
    if unclosed_commands:
        issues.append(f"Unclosed commands detected: {unclosed_commands}")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }

@function_tool
def search_formula_database(query: str) -> dict:
    """
    Simulates searching a database of common mathematical formulas.
    In production, this would connect to an actual database.
    """
    # Mock database of formulas
    formula_db = {
        "quadratic": {
            "name": "Quadratic Formula",
            "latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            "description": "Solution to quadratic equation ax^2 + bx + c = 0"
        },
        "pythagorean": {
            "name": "Pythagorean Theorem",
            "latex": "a^2 + b^2 = c^2",
            "description": "Relationship between sides of a right triangle"
        },
        "derivative": {
            "name": "Power Rule for Derivatives",
            "latex": "\\frac{d}{dx}x^n = nx^{n-1}",
            "description": "Rule for differentiating power functions"
        }
    }
    
    # Very simple search - in production would use better matching
    results = []
    query_lower = query.lower()
    
    for key, formula in formula_db.items():
        if query_lower in key or query_lower in formula["description"].lower():
            results.append(formula)
    
    return {
        "found": len(results) > 0,
        "results": results
    }