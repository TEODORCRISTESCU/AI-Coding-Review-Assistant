from reviewer.models import Review


def format_review(review: Review) -> str:
    lines  = [
        "<!-- ai-code-review -->"
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
        lines.append("")

    return "\n".join(lines)