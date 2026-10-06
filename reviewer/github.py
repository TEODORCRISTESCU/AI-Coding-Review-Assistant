import os

import requests
from reviewer.models import Review

REVIEW_MARKER = "<!-- ai-code-review -->"
INLINE_REVIEW_MARKER = "<!-- ai-inline-review -->"
REQUEST_TIMEOUT = 30


def _github_context() -> tuple[str, str, str]:
    return (
        os.environ["GITHUB_TOKEN"],
        os.environ["GITHUB_REPOSITORY"],
        os.environ["PR_NUMBER"],
    )


def _headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    token, _, _ = _github_context()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
    }


def _pull_url(suffix: str = "") -> str:
    _, repository, pull_number = _github_context()
    return f"https://api.github.com/repos/{repository}/pulls/{pull_number}{suffix}"


def post_comment(markdown: str) -> None:
    _, repository, pull_number = _github_context()

    comments_url = (
        f"https://api.github.com/repos/"
        f"{repository}/issues/{pull_number}/comments"
    )

    headers = _headers()

    comments_response = requests.get(
        comments_url,
        headers=headers,
        params={"per_page": 100},
        timeout=REQUEST_TIMEOUT,
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
            timeout=REQUEST_TIMEOUT,
        )

        action = "update"
    else:
        response = requests.post(
            comments_url,
            headers=headers,
            json={"body": body},
            timeout=REQUEST_TIMEOUT,
        )

        action = "create"

    if not response.ok:
        raise RuntimeError(
            f"Failed to {action} GitHub comment "
            f"({response.status_code}): {response.text}"
        )

def build_inline_comments(review: Review) -> list[dict]:
    return [
        {
            "path": finding.file_path,
            "line": finding.line,
            "side": "RIGHT",
            "body": (
                f"**{finding.severity.upper()}:** {finding.message}\n\n"
                f"**Suggested fix:** {finding.suggestion}"
            ),
        }
        for finding in review.findings
    ]


def list_pr_reviews() -> list[dict]:
    """Return all submitted and pending reviews, following API pagination."""
    reviews = []
    url = _pull_url("/reviews")
    page_number = 1
    params = {"per_page": 100, "page": page_number}

    while url:
        response = requests.get(
            url,
            headers=_headers(),
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        page = response.json()
        reviews.extend(page)

        next_url = getattr(response, "links", {}).get("next", {}).get("url")
        if next_url:
            url = next_url
            params = None
        elif len(page) == 100:
            page_number += 1
            params = {"per_page": 100, "page": page_number}
        else:
            break

    return reviews


def has_duplicate_inline_review(commit_sha: str) -> bool:
    return any(
        review.get("state") == "COMMENTED"
        and review.get("user", {}).get("login") == "github-actions[bot]"
        and INLINE_REVIEW_MARKER in (review.get("body") or "")
        and review.get("commit_id") == commit_sha
        for review in list_pr_reviews()
    )


def post_inline_review(review: Review, commit_sha: str) -> None:
    comments = build_inline_comments(review)

    if not comments or has_duplicate_inline_review(commit_sha):
        return

    url = _pull_url("/reviews")
    payload = {
        "commit_id": commit_sha,
        "body": (
            f"{INLINE_REVIEW_MARKER}\n\n"
            "AI review findings and suggested fixes."
        ),
        "event": "COMMENT",
        "comments": comments,
    }

    response = requests.post(
        url,
        headers=_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()


def get_pr_head_sha() -> str:
    url = _pull_url()
    response = requests.get(
        url,
        headers=_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()["head"]["sha"]
