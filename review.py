import subprocess

def review_code(code) -> dict:

    res = {
        "findings" : []
    }

    print("Reviewing code\n")


    if "password" in code:
        password = {}

        password["severity"] = "high"
        password["message"] = "Warning: possible password exposure"

        res["findings"].append(password)
    
    if "TODO" in code:
        TODO = {}

        TODO["severity"] = "low"
        TODO["message"] = "TODO comment found"

        res["findings"].append(TODO)

    return res

def read_code(filename):
    with open(filename, "r") as f:
        content = f.read()
    
        return content

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