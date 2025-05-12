from pydantic import BaseModel

class ImageParser(BaseModel):
    is_valid: bool
    text: str

class LatexOutput(BaseModel):
    latex_code: str
    description: str

class MathClassification(BaseModel):
    math_type: str  # algebra, calculus, geometry, etc.
    difficulty_level: str  # easy, medium, hard
    concepts: list[str]
    description: str

class MathSolution(BaseModel):
    solution_steps: list[str]
    final_answer: str
    explanation: str