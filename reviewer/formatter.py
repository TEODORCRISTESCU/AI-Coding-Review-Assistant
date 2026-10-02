from reviewer.models import Review


def format_review(review: Review) -> str:
    lines  = [
        "## AI Code Review",
        "",
        review.summary,
        "",
    ]

    for i, finding in enumerate(review.findings, start=1):
        lines.append(f"""### Finding {i} \n 
                        Severity :{finding.severity}\n
                        Message: {finding.message}\n
                        line : {finding.line} \n""")

    return "\n".join(lines)