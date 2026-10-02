import subprocess

from reviewer.formatter import format_review
from reviewer.github import post_comment
from .ai_review import ai_review

def read_diff(filename):
    result = subprocess.run(
        ["git", "diff", "main...HEAD", "--", filename],
        text=True,
        capture_output=True
    )

    return result.stdout


print("AI Code Reviewer starting...\n Waiting for pull request...\n")

diff = read_diff("reviewer/sample.py")

if diff:
    review = ai_review(diff)
    formatted_review = format_review(review)
    print(formatted_review)
    post_comment("Test comment from my AI reviewer.")

else:
    print("No changes found")

