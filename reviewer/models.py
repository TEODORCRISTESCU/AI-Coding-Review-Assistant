from pydantic import BaseModel


class Finding(BaseModel):
    severity: str
    message: str
    line: int


class Review(BaseModel):
    summary: str
    findings: list[Finding]
