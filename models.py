from pydantic import BaseModel

class ImageParser(BaseModel):
    is_valid: bool
    text: str