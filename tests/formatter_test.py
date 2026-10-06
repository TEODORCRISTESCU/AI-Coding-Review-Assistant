from reviewer.formatter import format_review
from reviewer.models import Finding, Review
from reviewer.main import read_diff

from types import SimpleNamespace

def test_format_review_includes_summary_and_findings():
    review = Review(
        summary="Hard-coded password found.",
        findings=[
            Finding(
                severity="high",
                message="Move the password to an environment variable.",
                line=4,
                file_path="reviewer/sample.py",
            )
        ],
    )

    result = format_review(review)

    assert "AI Code Review" in result
    assert "Hard-coded password found." in result
    assert "Move the password to an environment variable." in result
    assert "4" in result

def test_format_review_no_findings():
    review = Review(
        summary = "No issues found",
        findings = []

    )

    result = format_review(review)

    assert "No issues found" in result
    assert "Finding 1" not in result

def test_format_review_multiple_findings():
    
    review = Review ( 
        summary = "Hard-coded password found. \n TODO left unfinished",
        findings = [
            Finding(
                severity = "high",
                message = "Move password to an environment variable",
                line = 2,
                file_path = "reviewer/sample.py",
            ),

            Finding(
                severity = "low",
                message = "Finish TODO or delete it if not neccessary anymore",
                line = 10,
                file_path = "reviewer/main.py",
            )
        ]
    )


    result = format_review(review)

    for i in range(1, len(review.findings)):
        assert f"Finding {i}" in result

    assert "Hard-coded password found." in result
    assert "TODO left unfinished" in result
    assert "2" and "10" in result 
