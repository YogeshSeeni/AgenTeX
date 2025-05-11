from openai import OpenAI
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace, InputGuardrail, GuardrailFunctionOutput
from models import ImageParser, LatexOutput, MathTypeClassification, StepByStepSolution, QualityAssessment, InputClassification
from tools import parse_image, validate_latex, search_formula_database
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

# Agent #2: Math type classifier
math_classifier_agent = Agent(
    name="MathClassifierAgent",
    instructions=(
        "Analyze the mathematical content provided and classify it according to: "
        "1. The branch of mathematics it belongs to (algebra, calculus, geometry, statistics, etc.) "
        "2. The estimated difficulty level (easy, medium, hard) "
        "Provide detailed reasoning for your classification."
    ),
    output_type=MathTypeClassification,
    model="gpt-4o"
)

# Agent #3: Step by step solution generator
solution_generator_agent = Agent(
    name="SolutionGeneratorAgent",
    instructions=(
        "Given a mathematical problem, provide a clear step-by-step solution. "
        "Break down your approach into logical steps, explaining each transition. "
        "Include a final answer that directly addresses the problem statement."
    ),
    output_type=StepByStepSolution,
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

# Agent #4: generates LaTeX code
latex_generator_agent = Agent(
    name="LatexGeneratorAgent",
    instructions=(
        latex_prompt
    ),
    output_type=LatexOutput,
    tools=[validate_latex, search_formula_database],
    model="gpt-4o"
)

# Agent #5: Quality Assurance Agent
qa_agent = Agent(
    name="QualityAssuranceAgent",
    instructions=(
        "You are a mathematical LaTeX quality assurance specialist. Your job is to: "
        "1. Review the provided LaTeX code for correctness and completeness "
        "2. Check for any syntax errors or invalid KaTeX commands "
        "3. Ensure the LaTeX accurately represents the mathematical content "
        "4. Provide an improved version if issues are found "
        "Be thorough in your assessment but don't change mathematical meaning."
    ),
    output_type=QualityAssessment,
    model="gpt-4o"
)

# Agent #6: Triage/Input Classification Agent
async def input_classifier_guard(ctx, agent, input_data):
    classifier_agent = Agent(
        name="InputClassifier",
        instructions="Determine if the input is a mathematical question or expression that needs LaTeX formatting and categorize it.",
        output_type=InputClassification,
    )
    
    result = await Runner.run(classifier_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(InputClassification)
    
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_math_question,
    )

# Create a triage agent that handles the initial input
triage_agent = Agent(
    name="TriageAgent",
    instructions=(
        "You are the entry point for a mathematical expression processing system. "
        "Your job is to determine whether the input is an image URL or a text description "
        "and route it to the appropriate processing pipeline."
    ),
    input_guardrails=[
        InputGuardrail(guardrail_function=input_classifier_guard),
    ],
    model="gpt-4o"
)

# Example image URL - replace with your actual image URL
image_url = "https://www.firstforwomen.com/wp-content/uploads/sites/2/2018/02/math-iq-test.jpg?w=750&h=562&crop=1&quality=86&strip=all"

async def handle_image_input(image_url):
    """Pipeline for handling image inputs"""
    try:
        with trace("Image Processing Pipeline"):
            # Step 1: Parse the image
            parsed_result = await Runner.run(image_parser_agent, image_url)
            print("Parsed result:", parsed_result.final_output.text)
            
            # Step 2: Classify the math problem
            math_type = await Runner.run(math_classifier_agent, parsed_result.final_output.text)
            print(f"Math classification: {math_type.final_output.category}, Difficulty: {math_type.final_output.difficulty}")
            
            # Step 3: Generate solution steps
            solution = await Runner.run(solution_generator_agent, parsed_result.final_output.text)
            print("Solution steps:", solution.final_output.steps)
            
            # Step 4: Generate LaTeX code
            latex_result = await Runner.run(latex_generator_agent, parsed_result.final_output.text)
            print("Generated LaTeX:", latex_result.final_output.latex_code)
            
            # Step 5: Quality assurance
            qa_result = await Runner.run(qa_agent, latex_result.final_output.latex_code)
            
            # Use the improved version if available
            final_latex = qa_result.final_output.improved_latex if qa_result.final_output.improved_latex else latex_result.final_output.latex_code
            
            return {
                "parsed_text": parsed_result.final_output.text,
                "math_type": math_type.final_output.dict(),
                "solution": solution.final_output.dict(),
                "latex": final_latex,
                "qa_issues": qa_result.final_output.issues if not qa_result.final_output.is_correct else []
            }
    except Exception as e:
        # Handle any type of error generically
        error_type = type(e).__name__
        print(f"Error ({error_type}) in image processing: {str(e)}")
        return {"error": f"{error_type}: {str(e)}"}

async def handle_text_input(text_input):
    """Pipeline for handling direct text inputs"""
    try:
        with trace("Text Processing Pipeline"):
            # Step 1: Classify the math problem
            math_type = await Runner.run(math_classifier_agent, text_input)
            print(f"Math classification: {math_type.final_output.category}, Difficulty: {math_type.final_output.difficulty}")
            
            # Step 2: Generate solution steps if it's an actual problem
            solution = await Runner.run(solution_generator_agent, text_input)
            print("Solution steps:", solution.final_output.steps)
            
            # Step 3: Generate LaTeX code
            latex_result = await Runner.run(latex_generator_agent, text_input)
            print("Generated LaTeX:", latex_result.final_output.latex_code)
            
            # Step 4: Quality assurance
            qa_result = await Runner.run(qa_agent, latex_result.final_output.latex_code)
            
            # Use the improved version if available
            final_latex = qa_result.final_output.improved_latex if qa_result.final_output.improved_latex else latex_result.final_output.latex_code
            
            return {
                "original_text": text_input,
                "math_type": math_type.final_output.dict(),
                "solution": solution.final_output.dict(),
                "latex": final_latex,
                "qa_issues": qa_result.final_output.issues if not qa_result.final_output.is_correct else []
            }
    except Exception as e:
        # Handle any type of error generically
        error_type = type(e).__name__
        print(f"Error ({error_type}) in text processing: {str(e)}")
        return {"error": f"{error_type}: {str(e)}"}

async def main():
    # Example of the advanced deterministic flow with error handling
    try:
        # Handle image input
        print("\n=== Image Input Processing ===")
        image_result = await handle_image_input(image_url)
        print("\nFinal Image Result:", image_result)
        
        # Handle text input
        print("\n=== Text Input Processing ===")
        text_input = "Find the derivative of f(x) = x^3 + 2x^2 - 4x + 7"
        text_result = await handle_text_input(text_input)
        print("\nFinal Text Result:", text_result)
        
    except Exception as e:
        print(f"Error in main processing: {e}")

if __name__ == "__main__":
    asyncio.run(main())