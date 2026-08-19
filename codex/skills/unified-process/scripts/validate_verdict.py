#!/usr/bin/env python3
"""Validate the Unified Process JSON verdict without third-party packages."""

import argparse
import json
import sys
from pathlib import Path

BEGIN = "VERDICT_JSON_BEGIN"
END = "VERDICT_JSON_END"
REQUIRED = {"protocol_version", "verdict", "reviewer", "phase", "deliverable", "iteration", "evidence", "findings", "checklist"}


def extract(text):
    if BEGIN in text and END in text:
        text = text.split(BEGIN, 1)[1].split(END, 1)[0]
    return json.loads(text.strip().strip("`").removeprefix("json").strip())


def validate(value):
    errors = []
    if not isinstance(value, dict):
        return ["payload must be an object"]
    if set(value) != REQUIRED:
        errors.append("fields must match the protocol exactly")
    if value.get("protocol_version") != "1.0": errors.append("protocol_version must be 1.0")
    if value.get("verdict") not in {"PASS", "FAIL"}: errors.append("verdict must be PASS or FAIL")
    if not isinstance(value.get("reviewer"), str) or not value.get("reviewer"): errors.append("reviewer is required")
    if value.get("phase") is not None and not isinstance(value.get("phase"), str): errors.append("phase must be a string or null")
    if not isinstance(value.get("deliverable"), str) or not value.get("deliverable"): errors.append("deliverable is required")
    if not isinstance(value.get("iteration"), int) or value.get("iteration", 0) < 1: errors.append("iteration must be >= 1")
    evidence = value.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x for x in evidence): errors.append("evidence must be a non-empty string array")
    findings = value.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        if value.get("verdict") == "FAIL" and not findings: errors.append("FAIL requires a finding")
        if value.get("verdict") == "PASS" and findings: errors.append("PASS cannot contain findings")
        for item in findings:
            if not isinstance(item, dict) or set(item) != {"severity", "code", "message", "file", "line"}: errors.append("invalid finding fields"); continue
            if item.get("severity") not in {"high", "medium", "low"}: errors.append("invalid finding severity")
            if not item.get("code") or not item.get("message"): errors.append("finding code and message are required")
            if item.get("line") is not None and (not isinstance(item["line"], int) or item["line"] < 1): errors.append("invalid finding line")
    checklist = value.get("checklist")
    if not isinstance(checklist, list) or not checklist:
        errors.append("checklist must be a non-empty array")
    else:
        for item in checklist:
            if not isinstance(item, dict) or set(item) != {"id", "passed", "evidence"}: errors.append("invalid checklist fields"); continue
            if not item.get("id") or not isinstance(item.get("passed"), bool) or not item.get("evidence"): errors.append("invalid checklist item")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    try:
        errors = validate(extract(text))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
