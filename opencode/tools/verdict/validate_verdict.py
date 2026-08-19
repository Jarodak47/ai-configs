#!/usr/bin/env python3
"""Validate the stable JSON gate-verdict protocol without third-party packages."""

import argparse
import json
import sys
from pathlib import Path

BEGIN = "VERDICT_JSON_BEGIN"
END = "VERDICT_JSON_END"
REQUIRED = {
    "protocol_version", "verdict", "reviewer", "phase", "deliverable",
    "iteration", "evidence", "findings", "checklist",
}
SEVERITIES = {"high", "medium", "low"}


def extract_payload(text):
    if BEGIN in text and END in text:
        text = text.split(BEGIN, 1)[1].split(END, 1)[0]
    return json.loads(text.strip().strip("`").removeprefix("json").strip())


def validate(payload):
    errors = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    missing = REQUIRED - payload.keys()
    extra = payload.keys() - REQUIRED
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"unexpected fields: {', '.join(sorted(extra))}")
    if payload.get("protocol_version") != "1.0":
        errors.append("protocol_version must be 1.0")
    if payload.get("verdict") not in {"PASS", "FAIL"}:
        errors.append("verdict must be PASS or FAIL")
    if not isinstance(payload.get("reviewer"), str) or not payload.get("reviewer"):
        errors.append("reviewer must be a non-empty string")
    if payload.get("phase") is not None and not isinstance(payload.get("phase"), str):
        errors.append("phase must be a string or null")
    if not isinstance(payload.get("deliverable"), str) or not payload.get("deliverable"):
        errors.append("deliverable must be a non-empty string")
    if not isinstance(payload.get("iteration"), int) or payload.get("iteration", 0) < 1:
        errors.append("iteration must be an integer >= 1")
    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x for x in evidence):
        errors.append("evidence must be a non-empty string array")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        if payload.get("verdict") == "FAIL" and not findings:
            errors.append("FAIL requires at least one finding")
        if payload.get("verdict") == "PASS" and findings:
            errors.append("PASS cannot contain findings")
        for index, finding in enumerate(findings):
            if not isinstance(finding, dict):
                errors.append(f"findings[{index}] must be an object")
                continue
            if set(finding) != {"severity", "code", "message", "file", "line"}:
                errors.append(f"findings[{index}] has invalid fields")
            if finding.get("severity") not in SEVERITIES:
                errors.append(f"findings[{index}].severity is invalid")
            if not finding.get("code") or not finding.get("message"):
                errors.append(f"findings[{index}] requires code and message")
            if finding.get("line") is not None and (not isinstance(finding["line"], int) or finding["line"] < 1):
                errors.append(f"findings[{index}].line is invalid")
    checklist = payload.get("checklist")
    if not isinstance(checklist, list) or not checklist:
        errors.append("checklist must be a non-empty array")
    else:
        for index, item in enumerate(checklist):
            if not isinstance(item, dict) or set(item) != {"id", "passed", "evidence"}:
                errors.append(f"checklist[{index}] has invalid fields")
                continue
            if not item.get("id") or not isinstance(item.get("passed"), bool) or not item.get("evidence"):
                errors.append(f"checklist[{index}] is invalid")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    try:
        payload = extract_payload(text)
    except (ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: malformed JSON: {error}", file=sys.stderr)
        return 1
    errors = validate(payload)
    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
