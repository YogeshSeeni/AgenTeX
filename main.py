from openai import OpenAI
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace
from models import ImageParser, LatexOutput, MathClassification, MathSolution
from tools import parse_image, classify_math_content, generate_solution
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

latex_prompt = """
You are an expert LaTeX code generator for KaTeX (Streamlit's `st.latex`).  
Your task is to take any plain-English description or raw math expression and return **only** the minimal, valid LaTeX snippet—nothing else. This output will be inserted directly into `st.latex()`, so do **not** wrap it in `$…$`, `\[…\]`, or add any explanatory text.

Requirements:
1. **KaTeX‐compatible** – Use only commands supported by KaTeX (see https://katex.org/docs/supported.html).  
2. **No prose** – Output exactly the LaTeX code, no comments, no markdown fences.  
3. **Basic constructs**  
   - Fractions & roots: `\frac{num}{den}`, `\sqrt[root]{arg}`  
   - Superscripts & subscripts: `x^{2}`, `a_{ij}`  
   - Sums & integrals: `\sum_{i=0}^{n}`, `\int_{a}^{b}`  
4. **Functions & operators**  
   - Trig/log/exp: `\sin`, `\cos`, `\tan`, `\ln`, `\exp`, `\log`  
   - Limits & differentials: `\lim_{x\to 0}`, include `\,` before `dx` if needed  
5. **Symbols & Greek letters** – `\alpha`, `\beta`, `\Gamma`, `\partial`, `\infty`, etc.  
6. **Environments** – Matrices and piecewise cases:  
   ```
   \begin{pmatrix} … \end{pmatrix}
   \begin{cases} … \end{cases}
   ```  
7. **No custom macros** – Don't define new commands or load packages.  

Examples:
- Input: "derivative of x squared times sin x"  
  Output:  
  ```
  2x \sin x + x^2 \cos x
  ```
- Input: "integral from 0 to infinity of e to the minus x squared dx equals sqrt(pi) over 2"  
  Output:  
  ```
  \int_{0}^{\infty} e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}
  ```
- Input: "matrix with entries a, b on first row and c, d on second row"  
  Output:  
  ```
  \begin{pmatrix}
    a & b\\
    c & d
  \end{pmatrix}
  ```

Now, convert the following into KaTeX‐valid LaTeX code (no extra text):
> {{USER_INPUT}}

"""

# Agent #2: generates LaTeX code
latex_generator_agent = Agent(
    name="LatexGeneratorAgent",
    instructions=(
        latex_prompt
    ),
    output_type=LatexOutput,
    model="gpt-4o"
)

# Agent #3: classifies mathematical content
math_classifier_agent = Agent(
    name="MathClassifierAgent",
    instructions=(
        "You are a mathematical content classifier. Given a mathematical text or problem, "
        "classify it by type (algebra, calculus, geometry, etc.), difficulty level (easy, medium, hard), "
        "and identify key mathematical concepts involved. Also provide a brief description of what the "
        "mathematical content represents or what problem it's trying to solve."
    ),
    output_type=MathClassification,
    tools=[classify_math_content],
    model="gpt-4o"
)

# Agent #4: provides step-by-step solutions
solution_generator_agent = Agent(
    name="SolutionGeneratorAgent",
    instructions=(
        "You are a mathematics expert. Given a mathematical problem, provide a clear "
        "step-by-step solution with detailed explanations. Break down the solution into "
        "logical steps, provide a final answer, and explain the reasoning behind the solution."
    ),
    output_type=MathSolution,
    tools=[generate_solution],
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

        # Classify the mathematical content
        classification_result = await Runner.run(math_classifier_agent, parsed_result.final_output.text)
        print("Math classification:", classification_result.final_output.math_type)
        print("Difficulty:", classification_result.final_output.difficulty_level)
        print("Concepts:", classification_result.final_output.concepts)

        # Generate step-by-step solution if applicable
        solution_result = await Runner.run(solution_generator_agent, parsed_result.final_output.text)
        print("Solution steps:", solution_result.final_output.solution_steps)
        print("Final answer:", solution_result.final_output.final_answer)

if __name__ == "__main__":
    asyncio.run(main())