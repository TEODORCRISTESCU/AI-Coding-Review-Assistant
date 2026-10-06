from pydantic import BaseModel, Field
from typing import Literal

class Finding(BaseModel):
    severity: Literal["low", "medium", "high"]
    message: str = Field(min_length=1)
    line: int = Field(gt=0)
    file_path: str = Field(min_length=1)


class Review(BaseModel):
    summary: str
    findings: list[Finding]