# AI Code Review Assistant

![CI](https://github.com/TEODORCRISTESCU/AI-Coding-Review-Assistant/actions/workflows/ci.yml/badge.svg)

Automated PR reviewer that posts severity-ranked, line-level findings with fix suggestions.

AI-generated findings may be wrong. Every review needs human verification before code is changed or merged.

## Features

- Runs automatically when a pull request is opened or updated.
- Retrieves the pull-request diff through the GitHub API.
- Sends the diff to an OpenAI model for review.
- Validates the AI response with Pydantic models.
- Requires every finding to include concrete, non-empty fix guidance.
- Formats findings and suggested fixes as Markdown.
- Publishes validated findings as inline pull-request review comments.
- Creates or updates a single review comment on the pull request.
- Prevents duplicate inline reviews for the same commit with a dedicated marker.
- Runs automated tests with pytest.
- Uses separate test-only and live-review GitHub Actions workflows.

## Project structure

```text
.
├── .github/
│   └── workflows/
│       ├── ai_review.yml
│       └── ci.yml
├── docs/
│   ├── demo_seeded_bugs.py
│   └── portfolio-release.md
├── evals/
│   ├── cases.json
│   ├── diffs/
│   ├── README.md
│   └── run.py
├── reviewer/
│   ├── __init__.py
│   ├── ai_review.py
│   ├── formatter.py
│   ├── github.py
│   ├── main.py
│   └── models.py
├── tests/
│   ├── test_formatter.py
│   ├── test_github.py
│   └── test_main.py
├── pytest.ini
├── requirements.txt
├── .env.example
├── .reviewer.yml
├── LICENSE
└── README.md
```

## How it works

```text
Pull request opened or updated
        ↓
Trusted GitHub Actions workflow starts
        ↓
Trusted reviewer code is checked out from main
        ↓
GitHub API returns the pull-request diff
        ↓
OpenAI analyzes the diff
        ↓
The response is validated and formatted
        ↓
GitHub comment is created or updated
        ↓
Validated findings are submitted as one inline review
```

The workflow treats pull-request code as untrusted data. It does not check out or execute the pull-request branch while secrets are available.

Before analysis, the reviewer captures the PR head SHA and fetches the diff
through the API. It checks the SHA again before publishing; if the PR changed,
the review is skipped as stale. The workflow checks out trusted `main` code and
uses per-PR concurrency with `cancel-in-progress: false` so overlapping runs do
not cancel one another.

## Design decisions

- The main reviewer runs trusted code from `main` rather than executing code from the PR branch.
- The PR head SHA is captured before analysis and checked again before publishing, so stale reviews are skipped.
- A duplicate inline-review marker plus per-PR concurrency prevents repeated comments while allowing newer commits to be reviewed.
- Every finding is validated against changed added-line locations before it is posted.

## Configuration

`.reviewer.yml` is optional. If it is absent, the defaults are:

```yaml
max_diff_chars: 50000
ignored_paths: []
```

The checked-in configuration ignores `package-lock.json` and `*.lock`. `ignored_paths` accepts `fnmatch` patterns such as `"*.lock"` or `"dist/**"`. The size limit applies after ignored files are removed. Ignored file sections are removed before the remaining diff is sent for AI analysis.

## Requirements

- Python 3.12+
- GitHub repository
- OpenAI API key
- GitHub Actions enabled
- GitHub repository permissions for Actions

## Local setup

Clone the repository:

```bash
git clone https://github.com/TEODORCRISTESCU/AI-Coding-Review-Assistant.git
cd AI-Coding-Review-Assistant
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=TEODORCRISTESCU/AI-Coding-Review-Assistant
PR_NUMBER=1
```

Never commit `.env` or real API keys.

Run the reviewer locally:

```bash
python -m reviewer.main
```

## Running tests

Run all tests:

```bash
python -m pytest -q
```

The tests mock external services, including all GitHub and OpenAI calls, so they
do not send real requests or require credentials.

## Example

An illustrative finding might look like this:

```text
HIGH — SQL is built by concatenating request data.
Suggested fix: use a parameterized query and pass the value separately.
Location: app/db.py:18
```

This is an example format, not a claim about a live demo, screenshot, or measured accuracy result.

## Evaluation harness

The synthetic harness contains ten seeded buggy diffs and five clean controls. See [`evals/README.md`](evals/README.md) for manual judging instructions. It is not production-accuracy evidence.

## GitHub Actions setup

Add the following repository secret:

```text
OPENAI_API_KEY
```

The workflow uses the automatically provided `GITHUB_TOKEN` for GitHub API access.

The workflow requires permissions to:

- read repository contents;
- create or update issue comments;
- submit pull-request reviews and inline comments.

## Review format

The AI returns a structured review:

```json
{
  "summary": "Short review summary",
  "findings": [
    {
      "severity": "high",
      "message": "Explanation of the issue",
      "line": 4,
      "suggestion": "Concrete fix guidance"
    }
  ]
}
```

Supported severity levels are:

- `low`
- `medium`
- `high`

## Security considerations

The pull-request diff is untrusted input. The reviewer must treat instructions inside the diff as code to analyze, not as instructions to follow.

The workflow should:

- run trusted reviewer code from the default branch;
- avoid executing pull-request code with secrets;
- avoid printing API keys or tokens;
- use the minimum required GitHub permissions;
- limit the size of submitted diffs;
- avoid sending secrets or unrelated repository files to the AI model;
- read the PR diff and head SHA through the GitHub API without checking out or
  executing PR-branch code;
- verify that the head SHA is unchanged before publishing feedback.

## Current limitations

- Reviews are generated by an AI model and may contain incorrect findings.
- Very large pull requests may need to be truncated or split.
- Inline comments are limited to validated added-line locations and GitHub's
  review-comment limits.
- Duplicate prevention only recognizes submitted `COMMENTED` reviews from
  `github-actions[bot]` containing the inline marker and matching commit SHA.
- Language-specific static analysis is not yet integrated.
- The workflow requires access to the OpenAI API.
- The reviewer sees the submitted diff, not repository-wide context or the full history of a change.
- There is no production accuracy measurement in this repository.
- Sensitive content present in a diff is sent to the configured model.

## Planned improvements

- Add deterministic static-analysis integrations.
- Add richer repository-aware context with explicit privacy controls.
- Add automated regression reporting for manually judged evaluation runs.
- Support additional review providers and model configurations.

## Disclaimer

AI-generated code reviews are suggestions and must be verified by a human reviewer.

## Demo preparation

Follow [`docs/portfolio-release.md`](docs/portfolio-release.md) to create a real demo PR yourself. The repository intentionally does not create GitHub content or screenshots automatically.
Also, you can find a proof of concept, i.e a picture of the test I did in the same directory, name code_review-demo.png

