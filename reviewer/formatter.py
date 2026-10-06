from reviewer.models import Review


def format_suggestion(suggestion: str) -> str:
    """Render AI-generated fix guidance without losing its line breaks."""
    fence = "```"
    while fence in suggestion:
        fence += "`"

    return "\n".join(
        [
            "**Suggested fix:**",
            "",
            f"{fence}text",
            suggestion,
            fence,
        ]
    )


def format_review(review: Review) -> str:
    lines  = [
        "<!-- ai-code-review -->",
        "## AI Code Review",
        "",
        review.summary,
        "",
    ]

    for i, finding in enumerate(review.findings, start=1):
        lines.append(f"### Finding {i}")
        lines.append("")
        lines.append(f"**Severity:** {finding.severity.upper()}")
        lines.append(f"**Message:** {finding.message}")
        lines.append(f"**Line:** {finding.line}")
        lines.append(f"**Location:** `{finding.file_path}:{finding.line}`")
        lines.extend(format_suggestion(finding.suggestion).splitlines())
        lines.append("")

    return "\n".join(lines)
