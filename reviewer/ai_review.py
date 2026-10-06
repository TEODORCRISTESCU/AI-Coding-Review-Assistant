import json

from dotenv import load_dotenv
from openai import OpenAI

from reviewer.models import Review


load_dotenv()


def ai_review(code) -> Review:
    client = OpenAI()

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
      "line": 1,
      "file_path": "reviewer/sample.py",
      "suggestion": "concrete, actionable fix guidance"
    }}
  ]
}}

Severity must be exactly "low", "medium", or "high".
file_path must identify the changed file using its repository-relative path.
line must be the line number in the updated file, not its position in the diff.
Report findings only on added lines.
For every finding, provide a concrete suggested fix that a developer can apply.
If no issues are found, return an empty findings list
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return Review.model_validate(json.loads(response.output_text))
