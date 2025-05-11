from pydantic import BaseModel

class ImageParser(BaseModel):
    is_valid: bool
    text: str

class LatexOutput(BaseModel):
    latex_code: str
    description: str