from reviewer import main as reviewer_main
from reviewer.config import ReviewerConfig
from reviewer.diff_operations import filter_diff
from reviewer.models import Review


CODE_DIFF = """diff --git a/calculator.py b/calculator.py
--- a/calculator.py
+++ b/calculator.py
@@ -1 +1 @@
-old_code
+new_code
"""

LOCK_DIFF = """diff --git a/poetry.lock b/poetry.lock
--- a/poetry.lock
+++ b/poetry.lock
@@ -1 +1 @@
-old_dependency
+new_dependency
"""


def test_filter_removes_ignored_files():
    result = filter_diff(CODE_DIFF + LOCK_DIFF, ["*.lock"])

    assert result == CODE_DIFF


def test_filter_keeps_files_when_no_patterns():
    diff = CODE_DIFF + LOCK_DIFF

    assert filter_diff(diff, []) == diff


def setup_pipeline(monkeypatch, diff, config):
    posted_comments = []

    monkeypatch.setattr(reviewer_main, "load_config", lambda: config)
    monkeypatch.setattr(reviewer_main, "read_diff", lambda: diff)
    monkeypatch.setattr(reviewer_main, "get_pr_head_sha", lambda: "sha-1")
    monkeypatch.setattr(
        reviewer_main, "post_comment", posted_comments.append
    )
    monkeypatch.setattr(
        reviewer_main, "post_inline_review", lambda review, commit_sha: None
    )

    return posted_comments


def unexpected_ai_call(diff):
    raise AssertionError("OpenAI should not be called")


def test_all_files_ignored_skips_ai(monkeypatch):
    comments = setup_pipeline(
        monkeypatch,
        LOCK_DIFF,
        ReviewerConfig(ignored_paths=["*.lock"]),
    )
    monkeypatch.setattr(
        reviewer_main, "ai_review", unexpected_ai_call
    )

    reviewer_main.main()

    assert comments == [
        "Review skipped: no eligible changes to review."
    ]


def test_oversized_diff_skips_ai(monkeypatch):
    comments = setup_pipeline(
        monkeypatch,
        CODE_DIFF,
        ReviewerConfig(max_diff_chars=len(CODE_DIFF) - 1),
    )
    monkeypatch.setattr(
        reviewer_main, "ai_review", unexpected_ai_call
    )

    reviewer_main.main()

    assert len(comments) == 1
    assert "exceeds the configured size limit" in comments[0]


def test_ai_receives_filtered_diff_at_size_limit(monkeypatch):
    comments = setup_pipeline(
        monkeypatch,
        CODE_DIFF + LOCK_DIFF,
        ReviewerConfig(
            ignored_paths=["*.lock"],
            max_diff_chars=len(CODE_DIFF),
        ),
    )
    received_diffs = []

    def fake_ai_review(diff):
        received_diffs.append(diff)
        return Review(summary="No issues found.", findings=[])

    monkeypatch.setattr(reviewer_main, "ai_review", fake_ai_review)

    reviewer_main.main()

    assert received_diffs == [CODE_DIFF]
    assert len(comments) == 1
    assert "No issues found." in comments[0]
