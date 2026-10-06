import os
import requests
import sys
from json import JSONDecodeError
from openai import OpenAIError
from pydantic import ValidationError
from reviewer.diff_parser import diff_parser
from reviewer.formatter import format_review
from reviewer.github import post_comment
from .ai_review import ai_review

def read_diff():
    token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    pull_number = os.environ["PR_NUMBER"]

    url = (
        f"https://api.github.com/repos/"
        f"{repository}/pulls/{pull_number}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.diff",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.text

def main():
    print("AI Code Reviewer starting...\n Waiting for pull request...\n")

    diff = read_diff()

    if diff:
        review = ai_review(diff)
        parser_res = diff_parser(diff)
        valid_findings = []

        for finding in review.findings:

            valid_lines = parser_res.get(finding.file_path, set())
            
            if finding.line in valid_lines:
                valid_findings.append(finding)

            else:
                print(
                f"Rejected invalid location: "
                f"{finding.file_path}:{finding.line}"
            )

        
        rejected_count = len(review.findings) - len(valid_findings)
        review.findings = valid_findings

        if rejected_count:
        # Replace the original summary because it may describe rejected findings.
            review.summary = (
             f"Review incomplete: {rejected_count} finding(s) had invalid "
                "locations and were excluded. Remaining findings are shown below."
            if valid_findings
            else "Review incomplete: all findings had invalid locations "
                 "and were excluded."
        )

        formatted_review = format_review(review)
        print(formatted_review)
        post_comment(formatted_review)

    else:
        print("No changes found")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException:
        print(
            "Review failed: GitHub request failed.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OpenAIError:
        print(
            "Review failed: OpenAI request failed.",
            file=sys.stderr,
        )
        sys.exit(1)
    except JSONDecodeError:
        print(
            "Review failed: AI returned invalid JSON.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValidationError:
        print(
            "Review failed: AI response did not match the schema.",
            file=sys.stderr,
        )
        sys.exit(1)
    except RuntimeError:
        print(
            "Review failed: operation could not be completed.",
            file=sys.stderr,
        )
        sys.exit(1)