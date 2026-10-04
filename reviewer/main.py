import subprocess

from reviewer.formatter import format_review
from reviewer.github import post_comment
from .ai_review import ai_review

from logging import Logger

def read_diff(path=None):
    command = ["git", "diff", "origin/main...HEAD"]

    if path:
        command.extend(["--", path])

    result = subprocess.run(
        command,
        text=True,
        capture_output=True
    )

    if getattr(result, "returncode", 0) != 0:
        raise RuntimeError(f"Git diff failed: {getattr(result, 'stderr', '').strip()}")
    
    return result.stdout


def main():
    print("AI Code Reviewer starting...\n Waiting for pull request...\n")

    diff = read_diff()

    if diff:
        review = ai_review(diff)
        formatted_review = format_review(review)
        print(formatted_review)
        post_comment(formatted_review)
    else:
        print("No changes found")


if __name__ == "__main__":
    main()
