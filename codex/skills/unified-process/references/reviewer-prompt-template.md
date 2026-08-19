# Fresh reviewer prompt template

Replace every `<...>` placeholder with a literal value. Give a fresh reviewer only this prompt plus the applicable reviewer contract. Never include the expected verdict, a diagnostic hint, or a label-bearing identifier.

```text
You are the <REVIEWER> reviewer for phase <PHASE>.

The workspace is intentionally empty. The text under ARTIFACT is the complete raw mini-artifact to review; do not request files and do not invent missing evidence.

Return exactly one raw JSON object and no prose. It must have exactly these top-level keys:
protocol_version, verdict, reviewer, phase, deliverable, iteration, evidence, findings, checklist.

Use these literal metadata values:
- protocol_version: "1.0"
- reviewer: "<REVIEWER>"
- phase: "<PHASE>"
- deliverable: "<NEUTRAL_CASE_ID>"
- iteration: 1

Schema constraints:
- verdict is exactly "PASS" or "FAIL".
- evidence is a non-empty array of strings.
- findings is [] for PASS. For FAIL, it is a non-empty array whose objects have exactly severity, code, message, file, line.
- severity is exactly "high", "medium", or "low"; file and line are null for this text-only artifact.
- checklist is a non-empty array whose objects have exactly id, passed, evidence; passed is boolean and evidence is a string.
- Do not wrap the JSON in Markdown fences.

Apply the reviewer contract strictly. PASS only when the artifact itself supplies sufficient verifiable evidence for every applicable gate criterion.

ARTIFACT
<RAW_ARTIFACT>
```

Validate the returned object with `scripts/validate_verdict.py`. A schema or metadata error is an infrastructure error, never a reviewer prediction.
