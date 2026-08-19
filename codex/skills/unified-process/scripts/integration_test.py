#!/usr/bin/env python3
"""Deterministic integrity tests for the Unified Process skill."""

import json
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check(condition, message):
    if not condition: raise AssertionError(message)


def main():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", skill, re.S)
    check(match is not None and "name: unified-process" in match.group(1), "invalid frontmatter")
    for name in ("phase-contracts.md", "gates.md", "pipeline.md", "calibration.md", "reasoning-policy.md", "reviewer-prompt-template.md", "verdict.schema.json"):
        check((ROOT / "references" / name).is_file(), f"missing reference {name}")
    for script in (ROOT / "scripts").glob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
    cases = json.loads((ROOT / "assets/evaluation-cases.json").read_text(encoding="utf-8"))["cases"]
    ids = [case["id"] for case in cases]
    check(json.loads((ROOT / "assets/evaluation-cases.json").read_text(encoding="utf-8"))["schema_version"] == "3.1", "unexpected calibration dataset version")
    check(all(re.fullmatch(r"\d+\.\d+\.\d+", case.get("case_version", "")) for case in cases), "missing semantic case version")
    check(len(ids) == len(set(ids)), "duplicate case ids")
    check(all("pass" not in case_id.lower() and "fail" not in case_id.lower() for case_id in ids), "calibration IDs leak labels")
    for reviewer in {case["reviewer"] for case in cases}:
        labels = {case["expected"] for case in cases if case["reviewer"] == reviewer}
        check(labels == {"PASS", "FAIL"}, f"unbalanced reviewer fixtures: {reviewer}")
    hidden = json.loads((ROOT / "assets/hidden-evaluation-cases.json").read_text(encoding="utf-8"))["cases"]
    check(all(re.fullmatch(r"\d+\.\d+\.\d+", case.get("case_version", "")) for case in hidden), "missing hidden semantic case version")
    check(not set(ids) & {case["id"] for case in hidden}, "hidden cases overlap calibration cases")
    check(all("pass" not in case["id"].lower() and "fail" not in case["id"].lower() for case in hidden), "hidden IDs leak labels")
    check(all(case["split"] == "hidden" for case in hidden), "invalid hidden split")
    report = json.loads((ROOT / "assets/calibration-report.json").read_text(encoding="utf-8"))
    check(report["status"] == "accepted" and report["calibration"]["dataset_version"] == "3.1" and report["hidden"]["dataset_version"] == "2.1", "official calibration report is not accepted or current")
    for reviewer in {case["reviewer"] for case in hidden}:
        labels = {case["expected"] for case in hidden if case["reviewer"] == reviewer}
        check(labels == {"PASS", "FAIL"}, f"unbalanced hidden fixtures: {reviewer}")
    check(".config/opencode" not in skill, "OpenCode path leaked into skill")
    prompt = (ROOT / "references/reviewer-prompt-template.md").read_text(encoding="utf-8")
    check("exactly \"high\", \"medium\", or \"low\"" in prompt and "workspace is intentionally empty" in prompt.lower(), "reviewer prompt contract regressed")
    broad = subprocess.run([sys.executable, str(ROOT / "scripts/init_project.py"), "--project-dir", str(Path.home())], capture_output=True)
    check(broad.returncode != 0 and b"refusing broad" in broad.stderr, "broad project target was accepted")
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory)
        command = [sys.executable, str(ROOT / "scripts/init_project.py"), "--project-dir", str(project)]
        first = json.loads(subprocess.check_output(command, text=True))
        second = json.loads(subprocess.check_output(command, text=True))
        check(first["status"] == "created" and second["status"] == "kept", "initializer is not idempotent")
        check((project / "docs/dependency-graph.json").is_file(), "initializer missed dependency graph")
        status = project / "docs/status.md"
        status.write_text(status.read_text(encoding="utf-8") + "| 1 | BRC inception | 1 | FAIL | exigence manquante | oui | review |\n| 2 | BRC inception | 2 | PASS | — | — | review |\n", encoding="utf-8")
        subprocess.check_call([sys.executable, str(ROOT / "scripts/loop_metrics.py"), "--project-dir", str(project)])
        check("100.0%" in (project / "docs/metrics.md").read_text(encoding="utf-8"), "metrics final PASS calculation failed")
        verdict = project / "verdict.json"
        verdict.write_text(json.dumps({"protocol_version": "1.0", "verdict": "PASS", "reviewer": "functional", "phase": "01", "deliverable": "brc", "iteration": 1, "evidence": ["review"], "findings": [], "checklist": [{"id": "brc", "passed": True, "evidence": "complete"}]}), encoding="utf-8")
        subprocess.check_call([sys.executable, str(ROOT / "scripts/validate_verdict.py"), "--file", str(verdict)])
        graph_result = json.loads(subprocess.check_output([sys.executable, str(ROOT / "scripts/dependency_gate.py"), "--file", str(project / "docs/dependency-graph.json")], text=True))
        check(graph_result["valid"] and graph_result["runnable"] == ["phase-01-brc"], "dependency classification failed")
        results = project / "results.json"
        results.write_text(json.dumps({"model": "test-model", "reasoning_effort": "high", "runs": [{"case_id": case["id"], "case_version": case["case_version"], "artifact_sha256": hashlib.sha256(case["artifact"].encode("utf-8")).hexdigest(), "run": run, "predicted": case["expected"]} for case in cases for run in (1, 2, 3)], "infrastructure_errors": []}), encoding="utf-8")
        calibration = json.loads(subprocess.check_output([sys.executable, str(ROOT / "scripts/calibrate.py"), "--results", str(results)], text=True))
        check(calibration["accuracy"] == 1.0 and calibration["false_negatives"] == 0, "calibration scoring failed")
        official = json.loads(subprocess.check_output([sys.executable, str(ROOT / "scripts/calibrate.py"), "--results", str(ROOT / "assets/calibration-results.json")], text=True))
        check(official["runs_scored"] == 24 and official["accuracy"] == 1.0 and not official["infrastructure_errors"], "official calibration result regressed")
        hidden_official = json.loads(subprocess.check_output([sys.executable, str(ROOT / "scripts/calibrate.py"), "--cases", str(ROOT / "assets/hidden-evaluation-cases.json"), "--results", str(ROOT / "assets/hidden-evaluation-results.json"), "--min-runs", "1"], text=True))
        check(hidden_official["runs_scored"] == 8 and hidden_official["accuracy"] == 1.0 and not hidden_official["infrastructure_errors"], "hidden result regressed")
        malformed = project / "malformed.json"
        malformed.write_text('{"verdict":"PASS"}', encoding="utf-8")
        check(subprocess.run([sys.executable, str(ROOT / "scripts/validate_verdict.py"), "--file", str(malformed)], capture_output=True).returncode == 1, "malformed verdict was accepted")
        cyclic = project / "cycle.json"
        cyclic.write_text(json.dumps({"schema_version": "1.0", "nodes": [{"id": "a", "depends_on": ["b"], "status": "pending"}, {"id": "b", "depends_on": ["a"], "status": "pending"}]}), encoding="utf-8")
        check(subprocess.run([sys.executable, str(ROOT / "scripts/dependency_gate.py"), "--file", str(cyclic)], capture_output=True).returncode == 2, "dependency cycle was accepted")
        infra = project / "infra.json"
        infra.write_text(json.dumps({"model": "test-model", "reasoning_effort": "high", "runs": [], "infrastructure_errors": [{"case_id": "functional-brc-pass", "error": "timeout"}]}), encoding="utf-8")
        check(subprocess.run([sys.executable, str(ROOT / "scripts/calibrate.py"), "--results", str(infra)], capture_output=True).returncode == 2, "infrastructure failure was accepted")
        duplicate = project / "duplicate.json"
        duplicate_run = {"case_id": cases[0]["id"], "case_version": cases[0]["case_version"], "artifact_sha256": hashlib.sha256(cases[0]["artifact"].encode("utf-8")).hexdigest(), "run": 1, "predicted": cases[0]["expected"]}
        duplicate.write_text(json.dumps({"model": "test-model", "reasoning_effort": "high", "runs": [duplicate_run] * 3, "infrastructure_errors": []}), encoding="utf-8")
        check(subprocess.run([sys.executable, str(ROOT / "scripts/calibrate.py"), "--results", str(duplicate)], capture_output=True).returncode == 2, "duplicate or incomplete calibration was accepted")
        stale = project / "stale.json"
        stale_runs = [{"case_id": case["id"], "case_version": case["case_version"], "artifact_sha256": "0" * 64, "run": run, "predicted": case["expected"]} for case in cases for run in (1, 2, 3)]
        stale.write_text(json.dumps({"model": "test-model", "reasoning_effort": "high", "runs": stale_runs, "infrastructure_errors": []}), encoding="utf-8")
        check(subprocess.run([sys.executable, str(ROOT / "scripts/calibrate.py"), "--results", str(stale)], capture_output=True).returncode == 2, "stale artifact hash was accepted")
    print(f"PASS: skill integrity, {len(cases)} calibration + {len(hidden)} hidden fixtures, failure scenarios, Python compilation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
