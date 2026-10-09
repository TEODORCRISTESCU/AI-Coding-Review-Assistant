"""Run manually invoked model evaluations and score manual judgments."""

import json
import sys
from pathlib import Path
from typing import Any

from reviewer.ai_review import ai_review

ROOT = Path(__file__).parent
CASES_PATH = ROOT / "cases.json"
RESULTS_DIR = ROOT / "results"


def load_cases(path: Path = CASES_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_judgments(judgments: list[dict[str, Any]], cases: list[dict[str, Any]]) -> dict[str, int]:
    by_id = {item["case_id"]: item for item in judgments}
    seeded = [case for case in cases if case["kind"] == "bug"]
    controls = [case for case in cases if case["kind"] == "clean"]
    return {
        "caught_seeded_bugs": sum(bool(by_id.get(case["id"], {}).get("caught")) for case in seeded),
        "total_seeded_bugs": len(seeded),
        "clean_controls": len(controls),
        "false_positive_findings": sum(bool(by_id.get(case["id"], {}).get("false_positive")) for case in controls),
    }


def run() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    for case in load_cases():
        diff = (ROOT / case["fixture"]).read_text(encoding="utf-8")
        review = ai_review(diff)
        output = review.model_dump(mode="json")
        (RESULTS_DIR / f"{case['id']}.json").write_text(
            json.dumps(output, indent=2) + "\n", encoding="utf-8"
        )
        print(f"saved {case['id']}")


def score() -> None:
    judgments_path = RESULTS_DIR / "judgments.json"
    data = json.loads(judgments_path.read_text(encoding="utf-8"))
    result = score_judgments(data["judgments"], load_cases())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"run", "score"}:
        raise SystemExit("usage: python -m evals.run {run|score}")
    (run if sys.argv[1] == "run" else score)()
