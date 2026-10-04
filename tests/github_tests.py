from reviewer import github


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = "fake response"

    def json(self):
        return self._data


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