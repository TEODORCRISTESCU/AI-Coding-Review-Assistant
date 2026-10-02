import json

from dotenv import load_dotenv
from openai import OpenAI

from .models import Review


load_dotenv()

client = OpenAI()


def ai_review(code) -> Review:
    prompt = f"""
You are a code reviewer.

Review this Git diff:
{code}

Return only valid JSON. Do not use Markdown fences.

Use exactly this structure:
{{
  "summary": "short summary",
  "findings": [
    {{
      "severity": "low, medium, or high",
      "message": "clear explanation",
      "line": 1
    }}
  ]
}}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return Review.model_validate(json.loads(response.output_text))
