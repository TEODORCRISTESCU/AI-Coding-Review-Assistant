from reviewer import main as reviewer_main
from reviewer.models import Finding, Review

DIFF = """diff --git a/calculator.py b/calculator.py
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,3 @@
 def average(numbers):
-    return sum(numbers)
+    total = sum(numbers)
+    return total / len(numbers)
"""


def make_finding(line=3, file_path="calculator.py"):
    return Finding(
        severity="medium",
        message="An empty list causes division by zero.",
        line=line,
        file_path=file_path,
    )


def run_pipeline(monkeypatch, review):
    """Run main with a real parser and mocked external services."""
    captured_reviews = []
    posted_comments = []

    monkeypatch.setattr(reviewer_main, "read_diff", lambda: DIFF)
    monkeypatch.setattr(reviewer_main, "ai_review", lambda diff: review)

    def fake_format_review(filtered_review):
        captured_reviews.append(filtered_review)
        return "Formatted review"

    monkeypatch.setattr(
        reviewer_main, "format_review", fake_format_review
    )
    monkeypatch.setattr(
        reviewer_main, "post_comment", posted_comments.append
    )

    reviewer_main.main()

    assert len(captured_reviews) == 1
    assert posted_comments == ["Formatted review"]

    return captured_reviews[0]


def test_keeps_valid_findings(monkeypatch):
    finding = make_finding()
    review = Review(
        summary="Potential division by zero.",
        findings=[finding],
    )

    result = run_pipeline(monkeypatch, review)

    assert result.findings == [finding]
    assert result.summary == "Potential division by zero."


def test_removes_invalid_line(monkeypatch, capsys):
    valid = make_finding(line=3)
    invalid = make_finding(line=99)
    review = Review(
        summary="Two issues found.",
        findings=[valid, invalid],
    )

    result = run_pipeline(monkeypatch, review)

    assert result.findings == [valid]
    assert "Review incomplete" in result.summary
    assert "1 finding(s)" in result.summary
    assert "calculator.py:99" in capsys.readouterr().out


def test_removes_nonexistent_file(monkeypatch, capsys):
    review = Review(
        summary="An issue found.",
        findings=[make_finding(file_path="missing.py")],
    )

    result = run_pipeline(monkeypatch, review)

    assert result.findings == []
    assert "all findings had invalid locations" in result.summary
    assert "missing.py:3" in capsys.readouterr().out


def test_rejects_unchanged_line(monkeypatch):
    # Line 1 exists, but it is context rather than an added line.
    review = Review(
        summary="An issue found.",
        findings=[make_finding(line=1)],
    )

    result = run_pipeline(monkeypatch, review)

    assert result.findings == []
    assert "Review incomplete" in result.summary


def test_preserves_review_with_no_findings(monkeypatch):
    review = Review(summary="No issues found.", findings=[])

    result = run_pipeline(monkeypatch, review)

    assert result.findings == []
    assert result.summary == "No issues found."


def test_empty_diff_skips_review_and_posting(monkeypatch, capsys):
    monkeypatch.setattr(reviewer_main, "read_diff", lambda: "")

    def unexpected_call(*args, **kwargs):
        raise AssertionError("Should not run for an empty diff")

    monkeypatch.setattr(reviewer_main, "ai_review", unexpected_call)
    monkeypatch.setattr(reviewer_main, "post_comment", unexpected_call)

    reviewer_main.main()

    assert "No changes found" in capsys.readouterr().out