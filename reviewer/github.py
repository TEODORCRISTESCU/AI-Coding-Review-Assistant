import os
import requests


def post_comment(markdown: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    pull_number = os.environ["PR_NUMBER"]

    url = (
        f"https://api.github.com/repos/"
        f"{repository}/issues/{pull_number}/comments"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {
        "body": markdown
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
    )

    print("GitHub status:", response.status_code)
    print("GitHub response:", response.text)
    response.raise_for_status()