# Synthetic evaluation harness

`evals/cases.json` describes ten seeded buggy unified diffs and five clean
controls. The fixtures are deliberately small and synthetic; their results
are not evidence of production accuracy.

To run a live evaluation yourself, configure credentials and run:

```bash
python -m evals.run run
```

This calls `reviewer.ai_review` once per fixture and writes raw model outputs
to `evals/results/`. It is intentionally not run by the test suite or CI.

Create `evals/results/judgments.json` manually with this shape:

```json
{
  "judgments": [
    {"case_id": "bug_sql_concat", "caught": true, "false_positive": false}
  ]
}
```

Include one judgment per case, then run `python -m evals.run score`. A seeded
bug is caught when its `caught` value is true. A clean control contributes a
false positive when its `false_positive` value is true. Do not invent missing
judgments or report these synthetic results as production measurements.
