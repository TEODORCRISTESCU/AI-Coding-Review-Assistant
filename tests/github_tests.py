import pytest
import requests

from reviewer import github


class FakeResponse:
    def __init__(self, data, status_code=200, links=None):
        self._data = data
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = "fake response"
        self.links = links or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError(self.text)


def setup_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv(
        "GITHUB_REPOSITORY",
        "TEODORCRISTESCU/AI-Coding-Review-Assistant",
    )
    monkeypatch.setenv("PR_NUMBER", "4")


def test_creates_comment_when_no_review_exists(monkeypatch):
    setup_environment(monkeypatch)

    post_calls = []

    def fake_get(url, **kwargs):
        return FakeResponse([])

    def fake_post(url, **kwargs):
        post_calls.append((url, kwargs))
        return FakeResponse({}, status_code=201)

    monkeypatch.setattr(github.requests, "get", fake_get)
    monkeypatch.setattr(github.requests, "post", fake_post)

    github.post_comment("Test review")

    assert len(post_calls) == 1

    body = post_calls[0][1]["json"]["body"]

    assert "<!-- ai-code-review -->" in body
    assert "Test review" in body


def test_updates_existing_review(monkeypatch):
    setup_environment(monkeypatch)

    patch_calls = []

    existing_comment = {
        "id": 123,
        "body": "<!-- ai-code-review -->\n\nOld review",
        "user": {"login": "github-actions[bot]"},
    }

    def fake_get(url, **kwargs):
        return FakeResponse([existing_comment])

    def fake_patch(url, **kwargs):
        patch_calls.append((url, kwargs))
        return FakeResponse({})

    def fake_post(url, **kwargs):
        raise AssertionError("POST should not be called")

    monkeypatch.setattr(github.requests, "get", fake_get)
    monkeypatch.setattr(github.requests, "patch", fake_patch)
    monkeypatch.setattr(github.requests, "post", fake_post)

    github.post_comment("Updated review")

    assert len(patch_calls) == 1
    assert patch_calls[0][0].endswith("/issues/comments/123")
    assert "Updated review" in patch_calls[0][1]["json"]["body"]


def make_review():
    from reviewer.models import Finding, Review

    return Review(
        summary="One issue",
        findings=[
            Finding(
                severity="high",
                message="This can fail for an empty list.",
                line=8,
                file_path="calculator.py",
                suggestion="Return an error before dividing by the list length.",
            )
        ],
    )


def test_inline_review_payload_and_locations(monkeypatch):
    setup_environment(monkeypatch)
    calls = []

    def fake_get(url, **kwargs):
        return FakeResponse([])

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse({}, status_code=201)

    monkeypatch.setattr(github.requests, "get", fake_get)
    monkeypatch.setattr(github.requests, "post", fake_post)

    github.post_inline_review(make_review(), "sha-123")

    assert calls[0][0].endswith("/pulls/4/reviews")
    payload = calls[0][1]["json"]
    assert payload["event"] == "COMMENT"
    assert payload["commit_id"] == "sha-123"
    assert "ai-inline-review" in payload["body"]
    assert payload["comments"] == [
        {
            "path": "calculator.py",
            "line": 8,
            "side": "RIGHT",
            "body": (
                "**HIGH:** This can fail for an empty list.\n\n"
                "**Suggested fix:**\n\n"
                "```text\n"
                "Return an error before dividing by the list length.\n"
                "```"
            ),
        }
    ]


def test_inline_review_skips_empty_findings_without_requests(monkeypatch):
    setup_environment(monkeypatch)
    calls = []

    def fail_request(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("No GitHub request expected")

    monkeypatch.setattr(github.requests, "get", fail_request)
    monkeypatch.setattr(github.requests, "post", fail_request)

    from reviewer.models import Review

    github.post_inline_review(Review(summary="No issues", findings=[]), "sha-123")

    assert calls == []


def test_duplicate_inline_review_skips_post(monkeypatch):
    setup_environment(monkeypatch)
    post_calls = []
    existing = {
        "state": "COMMENTED",
        "body": "<!-- ai-inline-review -->",
        "user": {"login": "github-actions[bot]"},
        "commit_id": "sha-123",
    }

    monkeypatch.setattr(
        github.requests, "get", lambda url, **kwargs: FakeResponse([existing])
    )
    monkeypatch.setattr(
        github.requests,
        "post",
        lambda url, **kwargs: post_calls.append((url, kwargs)),
    )

    github.post_inline_review(make_review(), "sha-123")

    assert post_calls == []


def test_different_sha_allows_inline_review(monkeypatch):
    setup_environment(monkeypatch)
    post_calls = []
    existing = {
        "state": "COMMENTED",
        "body": "<!-- ai-inline-review -->",
        "user": {"login": "github-actions[bot]"},
        "commit_id": "old-sha",
    }

    monkeypatch.setattr(
        github.requests, "get", lambda url, **kwargs: FakeResponse([existing])
    )
    monkeypatch.setattr(
        github.requests,
        "post",
        lambda url, **kwargs: post_calls.append((url, kwargs)) or FakeResponse({}),
    )

    github.post_inline_review(make_review(), "sha-123")

    assert len(post_calls) == 1


def test_other_authors_unmarked_and_pending_reviews_do_not_suppress(monkeypatch):
    setup_environment(monkeypatch)
    post_calls = []
    reviews = [
        {
            "state": "COMMENTED",
            "body": "<!-- ai-inline-review -->",
            "user": {"login": "someone-else"},
            "commit_id": "sha-123",
        },
        {
            "state": "COMMENTED",
            "body": "unmarked",
            "user": {"login": "github-actions[bot]"},
            "commit_id": "sha-123",
        },
        {
            "state": "PENDING",
            "body": "<!-- ai-inline-review -->",
            "user": {"login": "github-actions[bot]"},
            "commit_id": "sha-123",
        },
    ]

    monkeypatch.setattr(
        github.requests, "get", lambda url, **kwargs: FakeResponse(reviews)
    )
    monkeypatch.setattr(
        github.requests,
        "post",
        lambda url, **kwargs: post_calls.append((url, kwargs)) or FakeResponse({}),
    )

    github.post_inline_review(make_review(), "sha-123")

    assert len(post_calls) == 1


def test_review_list_follows_pagination(monkeypatch):
    setup_environment(monkeypatch)
    requests_seen = []
    first_page = [{"id": i} for i in range(100)]

    def fake_get(url, **kwargs):
        requests_seen.append((url, kwargs))
        if len(requests_seen) == 1:
            return FakeResponse(first_page)
        return FakeResponse([{"id": 101}])

    monkeypatch.setattr(github.requests, "get", fake_get)

    reviews = github.list_pr_reviews()

    assert len(reviews) == 101
    assert requests_seen[0][1]["params"] == {"per_page": 100, "page": 1}
    assert requests_seen[1][1]["params"] == {"per_page": 100, "page": 2}


def test_github_review_list_failure_propagates(monkeypatch):
    setup_environment(monkeypatch)

    def fail_get(*args, **kwargs):
        raise requests.ConnectionError("GitHub unavailable")

    monkeypatch.setattr(github.requests, "get", fail_get)

    with pytest.raises(requests.RequestException):
        github.post_inline_review(make_review(), "sha-123")
