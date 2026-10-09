from evals.run import score_judgments


CASES = [
    {"id": "bug_one", "kind": "bug"},
    {"id": "bug_two", "kind": "bug"},
    {"id": "clean_one", "kind": "clean"},
    {"id": "clean_two", "kind": "clean"},
]


def test_score_counts_caught_bugs_and_clean_controls():
    result = score_judgments(
        [
            {"case_id": "bug_one", "caught": True, "false_positive": False},
            {"case_id": "bug_two", "caught": False, "false_positive": False},
            {"case_id": "clean_one", "caught": False, "false_positive": True},
            {"case_id": "clean_two", "caught": False, "false_positive": False},
        ],
        CASES,
    )

    assert result == {
        "caught_seeded_bugs": 1,
        "total_seeded_bugs": 2,
        "clean_controls": 2,
        "false_positive_findings": 1,
    }


def test_score_does_not_treat_missing_judgments_as_findings():
    result = score_judgments([], CASES)

    assert result["caught_seeded_bugs"] == 0
    assert result["false_positive_findings"] == 0
