import subprocess

def review_code(code) -> dict:

    res = {
        "findings" : []
    }

    print("Reviewing code\n")

    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        if not line.startswith("+") or line.startswith("+++"):
            continue

        changed_line = line[1:]
        if "password" in changed_line:
            password = {}

            password["severity"] = "high"
            password["message"] = "Warning: possible password exposure"
            password["line"] = line_number

            res["findings"].append(password)
    
        if "TODO" in changed_line:
            TODO = {}

            TODO["severity"] = "low"
            TODO["message"] = "TODO comment found"
            TODO["line"] = line_number

            res["findings"].append(TODO)

    return res

def read_diff():
    result = subprocess.run(
    ["git", "diff"],
    text=True,
    capture_output=True
)

    return result.stdout

print("AI Code Reviewer starting...\n Waiting for pull request...\n")

diff = read_diff()
print(review_code(diff))