#!/usr/bin/env python3
"""Score independent reviewer predictions against protected fixture labels."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=SKILL_DIR / "assets/evaluation-cases.json")
    parser.add_argument("--min-runs", type=int, default=3)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    expected = {case["id"]: case["expected"] for case in cases}
    case_versions = {case["id"]: case["case_version"] for case in cases}
    artifact_hashes = {case["id"]: hashlib.sha256(case["artifact"].encode("utf-8")).hexdigest() for case in cases}
    results = json.loads(args.results.read_text(encoding="utf-8"))
    runs = results.get("runs", [])
    errors = list(results.get("infrastructure_errors", []))
    if not results.get("model") or results.get("reasoning_effort") not in {"low", "medium", "high", "xhigh"}:
        errors.append({"error": "model and valid reasoning_effort metadata are required"})
    counts = Counter()
    predictions = defaultdict(list)
    seen_runs = set()
    for run in runs:
        case_id, predicted = run.get("case_id"), run.get("predicted")
        if case_id not in expected or predicted not in {"PASS", "FAIL"}:
            errors.append({"run": run, "error": "unknown case or invalid prediction"}); continue
        if run.get("case_version") != case_versions[case_id] or run.get("artifact_sha256") != artifact_hashes[case_id]:
            errors.append({"run": run, "error": "stale or unverified case version/artifact hash"}); continue
        run_key = (case_id, run.get("run"))
        if not isinstance(run.get("run"), int) or run.get("run", 0) < 1:
            errors.append({"run": run, "error": "run must be an integer >= 1"}); continue
        if run_key in seen_runs:
            errors.append({"run": run, "error": "duplicate case_id/run"}); continue
        seen_runs.add(run_key)
        actual = expected[case_id]
        predictions[case_id].append(predicted)
        counts[(actual, predicted)] += 1
    for case_id in expected:
        if len(predictions[case_id]) < args.min_runs:
            errors.append({"case_id": case_id, "error": f"requires at least {args.min_runs} valid runs"})
    tp, tn = counts[("FAIL", "FAIL")], counts[("PASS", "PASS")]
    fp, fn = counts[("PASS", "FAIL")], counts[("FAIL", "PASS")]
    total = tp + tn + fp + fn
    stability = [len(set(values)) == 1 for values in predictions.values() if len(values) > 1]
    report = {"model": results.get("model"), "reasoning_effort": results.get("reasoning_effort"),
              "runs_scored": total, "accuracy": (tp + tn) / total if total else None,
              "fail_precision": tp / (tp + fp) if tp + fp else None, "fail_recall": tp / (tp + fn) if tp + fn else None,
              "false_positives": fp, "false_negatives": fn,
              "stability": sum(stability) / len(stability) if stability else None,
              "cases_covered": len(predictions), "cases_total": len(expected), "infrastructure_errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if errors or not total else 0


if __name__ == "__main__":
    raise SystemExit(main())
