import subprocess

from .ai_review import ai_review


def read_diff(filename):
    result = subprocess.run(
        ["git", "diff", "--", filename],
        text=True,
        capture_output=True
    )

    return result.stdout


print("AI Code Reviewer starting...\n Waiting for pull request...\n")

diff = read_diff("sample.py")
print(f"{diff}\n")
review = ai_review(diff)
print(review.summary)

for finding in review.findings:
    print(finding.severity)
    print(finding.message)
    print(finding.line)
