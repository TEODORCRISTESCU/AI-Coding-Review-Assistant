import os

import requests


REVIEW_MARKER = "<!-- ai-code-review -->"


def post_comment(markdown: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    pull_number = os.environ["PR_NUMBER"]

    comments_url = (
        f"https://api.github.com/repos/"
        f"{repository}/issues/{pull_number}/comments"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    comments_response = requests.get(
        comments_url,
        headers=headers,
        params={"per_page": 100},
        timeout=30,
    )

    if not comments_response.ok:
        raise RuntimeError(
            f"Failed to fetch GitHub comments "
            f"({comments_response.status_code}): "
            f"{comments_response.text}"
        )

    comments = comments_response.json()

    existing_comment = None

    for comment in comments:
        body = comment.get("body") or ""
        author = comment.get("user", {}).get("login")

        if REVIEW_MARKER in body and author == "github-actions[bot]":
            existing_comment = comment
            break

    body = f"{REVIEW_MARKER}\n\n{markdown}"

    if existing_comment is not None:
        update_url = (
            f"https://api.github.com/repos/"
            f"{repository}/issues/comments/{existing_comment['id']}"
        )

        response = requests.patch(
            update_url,
            headers=headers,
            json={"body": body},
            timeout=30,
        )

        action = "update"
    else:
        response = requests.post(
            comments_url,
            headers=headers,
            json={"body": body},
            timeout=30,
        )

        action = "create"

    if not response.ok:
        raise RuntimeError(
            f"Failed to {action} GitHub comment "
            f"({response.status_code}): {response.text}"
        )