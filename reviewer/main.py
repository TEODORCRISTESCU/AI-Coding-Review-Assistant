import subprocess
import os
import requests

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

print("AI Code Reviewer starting...\n Waiting for pull request...\n")

diff = read_diff()

if diff:
    review = ai_review(diff)
    formatted_review = format_review(review)
    print(formatted_review)
    post_comment(formatted_review)

else:
    print("No changes found")
