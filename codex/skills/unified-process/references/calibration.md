# Reviewer calibration

## Dataset discipline

- Keep development, calibration, and hidden test sets separate.
- Balance PASS and FAIL where practical and include adversarial, ambiguous, and out-of-distribution cases.
- Store the expected verdict outside the reviewer prompt.
- Use neutral case IDs and deliverable names. Never include `pass`, `fail`, expected labels, or diagnostic hints in reviewer-visible identifiers.
- Version each case and record the reviewer/model configuration used. Bind every recorded run to its `case_version` and SHA-256 of the exact raw `artifact`; the scorer rejects stale or unverified inputs.

## Execution protocol

1. Select one reviewer role and one fixture from `assets/evaluation-cases.json`.
2. Start a fresh independent agent/task with only the reviewer contract and the fixture artifact.
3. Instantiate `reviewer-prompt-template.md` with literal metadata values and require the structured verdict protocol. Record infrastructure failures separately.
4. Repeat calibration cases at least three times to measure stability. Execute a hidden test case once per frozen baseline to avoid tuning on repeated hidden outputs.
5. Save predictions as JSON and run `scripts/calibrate.py`.
6. Reject a new reviewer baseline when false negatives increase, stability regresses materially, or infrastructure errors hide coverage.

For the hidden set, freeze reviewer prompts and calibration baseline first, pass only raw artifacts to fresh agents, then score with `--cases assets/hidden-evaluation-cases.json --min-runs 1`. Do not modify reviewers from hidden results until the evaluation is recorded; after modification, create a new hidden dataset version.

## Result format

```json
{
  "model": "gpt-5.6-sol",
  "reasoning_effort": "high",
  "runs": [
    {"case_id": "cal-sec-02", "case_version": "1.0.0", "artifact_sha256": "<64 lowercase hex characters>", "run": 1, "predicted": "FAIL"}
  ],
  "infrastructure_errors": []
}
```

Never include `expected` in the results file. The scorer joins predictions with the protected labels in the fixture dataset. Missing model or effort metadata is an infrastructure/configuration error.
