#!/usr/bin/env python3
"""Calibrate checker agents on hidden-truth sandbox fixtures."""

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

CONFIG = Path(os.environ.get("OPENCODE_CONFIG_DIR", Path.home() / ".config" / "opencode"))
CASES = CONFIG / "tools/agent-evaluation/cases.json"
OPENCODE = shutil.which("opencode") or "/usr/local/bin/opencode"
VALIDATOR = CONFIG / "tools/verdict/validate_verdict.py"


def materialize(case, root):
    for relative, content in case["files"].items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_case(case, timeout):
    with tempfile.TemporaryDirectory(prefix="agent-eval-") as temporary:
        fixture = Path(temporary) / "fixture"
        fixture.mkdir()
        materialize(case, fixture)
        prompt = (f"TARGET_AGENT: {case['agent']}\nFIXTURE: current directory (.)\n\n"
                  f"{case['instruction']}\nDo not reveal or infer any expected verdict from the harness.")
        command = [OPENCODE, "run", "--dir", str(fixture), "--agent",
                   "evaluation-runner", "--auto", prompt]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, "timeout"
        output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + "\n" + result.stderr)
        if "INFRA_ERROR" in output or re.search(r"is a subagent, not a primary", output, re.I):
            return None, "agent fallback or infrastructure error"
        match = re.search(r"VERDICT_JSON_BEGIN\s*(\{.*?\})\s*VERDICT_JSON_END", output, re.S)
        if not match:
            tail = " ".join(output[-1200:].split())
            return None, "structured verdict missing; output=" + tail
        validation = subprocess.run(["python3", str(VALIDATOR)], input=match.group(1),
                                    capture_output=True, text=True)
        if validation.returncode != 0:
            return None, validation.stderr.strip() + "; payload=" + " ".join(match.group(1).split())[:900]
        payload = json.loads(match.group(1))
        if payload["reviewer"] != case["agent"]:
            return None, f"wrong reviewer: {payload['reviewer']}"
        detail = [item["message"] for item in payload["findings"][:3]]
        detail.extend(payload["evidence"][:2])
        return payload["verdict"], "; ".join(detail)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent")
    parser.add_argument("--case")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--out", type=Path, default=CONFIG / "tools/agent-evaluation/results.json")
    args = parser.parse_args()
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    cases = [case for case in payload["cases"]
             if (not args.agent or case["agent"] == args.agent)
             and (not args.case or case["id"] == args.case)]
    if not cases:
        parser.error("no matching evaluation cases")
    results = []
    for case in cases:
        for run in range(1, args.runs + 1):
            predicted, evidence = run_case(case, args.timeout)
            results.append({"id": case["id"], "agent": case["agent"], "run": run,
                            "truth": case["truth"], "predicted": predicted or "INFRA_ERROR",
                            "correct": predicted == case["truth"] if predicted else None,
                            "evidence": evidence})
            print(f"{case['id']} run={run}: {predicted or 'INFRA_ERROR'}")
    metrics = {}
    for agent in sorted({case["agent"] for case in cases}):
        rows = [row for row in results if row["agent"] == agent]
        decided = [row for row in rows if row["predicted"] in {"PASS", "FAIL"}]
        tp = sum(row["predicted"] == "FAIL" and row["truth"] == "FAIL" for row in decided)
        fp = sum(row["predicted"] == "FAIL" and row["truth"] == "PASS" for row in decided)
        fn = sum(row["predicted"] == "PASS" and row["truth"] == "FAIL" for row in decided)
        tn = sum(row["predicted"] == "PASS" and row["truth"] == "PASS" for row in decided)
        metrics[agent] = {
            "decided": len(decided),
            "infrastructure_errors": len(rows) - len(decided),
            "accuracy": (sum(row["correct"] for row in decided) / len(decided)) if decided else None,
            "precision_fail": tp / (tp + fp) if tp + fp else None,
            "recall_fail": tp / (tp + fn) if tp + fn else None,
            "false_positive_rate": fp / (fp + tn) if fp + tn else None,
            "false_negative_rate": fn / (fn + tp) if fn + tp else None,
            "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
            "stable_cases": sum(1 for case_id in {row["id"] for row in rows}
                                if len({row["predicted"] for row in rows if row["id"] == case_id}) == 1),
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"metrics": metrics, "results": results}, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return 0 if results and all(row["correct"] is True for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
