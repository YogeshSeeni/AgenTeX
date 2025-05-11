from pydantic import BaseModel
from typing import List, Optional

class ImageParser(BaseModel):
    is_valid: bool
    text: str

class LatexOutput(BaseModel):
    latex_code: str
    description: str

class MathTypeClassification(BaseModel):
    category: str  # algebra, calculus, geometry, etc.
    difficulty: str  # easy, medium, hard
    reasoning: str

class StepByStepSolution(BaseModel):
    steps: List[str]
    final_answer: str
    
class QualityAssessment(BaseModel):
    is_correct: bool
    issues: List[str]
    improved_latex: Optional[str] = None

class InputClassification(BaseModel):
    is_math_question: bool
    category: Optional[str] = None
    reasoning: str