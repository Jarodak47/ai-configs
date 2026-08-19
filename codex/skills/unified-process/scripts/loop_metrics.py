#!/usr/bin/env python3
"""Compute deterministic workflow metrics from docs/status.md."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def parse(path):
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7 or not cells[0].isdigit():
            continue
        verdict = re.search(r"PASS|FAIL", cells[3], re.I)
        rows.append({"deliverable": cells[1], "iteration": int(cells[2]) if cells[2].isdigit() else 1,
                     "verdict": verdict.group(0).upper() if verdict else "UNKNOWN", "cause": cells[4]})
    return rows


def phase(name):
    text = name.lower()
    for number, words in ((1, ("brc", "inception")), (2, ("elab", "model", "use case", "gherkin")),
                          (3, ("construction", "code", "test", "impl")), (4, ("transition", "uat", "deploy", "release"))):
        if any(word in text for word in words): return f"0{number}"
    return "other"


def compute(rows):
    grouped = defaultdict(list)
    for row in rows: grouped[row["deliverable"]].append(row)
    final = []
    for name, attempts in grouped.items():
        final.append({"deliverable": name, "phase": phase(name), "iterations": max(x["iteration"] for x in attempts),
                      "verdict": attempts[-1]["verdict"], "failures": [x["cause"] for x in attempts if x["verdict"] == "FAIL" and x["cause"] not in {"", "-", "—"}]})
    decided = [x for x in final if x["verdict"] in {"PASS", "FAIL"}]
    passed = [x for x in decided if x["verdict"] == "PASS"]
    return {"deliverables": len(final), "decided": len(decided), "passed": len(passed),
            "failed_final": sum(x["verdict"] == "FAIL" for x in decided),
            "pass_rate": round(len(passed) / len(decided), 4) if decided else None,
            "average_iterations_to_pass": round(sum(x["iterations"] for x in passed) / len(passed), 3) if passed else None,
            "by_phase": dict(Counter(x["phase"] for x in final)), "details": final}


def markdown(metrics):
    rate = "—" if metrics["pass_rate"] is None else f'{metrics["pass_rate"] * 100:.1f}%'
    lines = ["# Unified Process metrics", "", f'- Deliverables: {metrics["deliverables"]}', f'- PASS rate: {rate}',
             f'- Final FAIL: {metrics["failed_final"]}', f'- Average iterations to PASS: {metrics["average_iterations_to_pass"] or "—"}', "",
             "| Deliverable | Phase | Iterations | Final verdict |", "|---|---|---:|---|"]
    for item in metrics["details"]:
        deliverable = item["deliverable"].replace("|", "\\|")
        lines.append(f'| {deliverable} | {item["phase"]} | {item["iterations"]} | {item["verdict"]} |')
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    project = args.project_dir.resolve()
    source = project / "docs/status.md"
    if not source.exists(): raise SystemExit(f"missing {source}")
    metrics = compute(parse(source))
    output = project / "docs/metrics.md"
    output.write_text(markdown(metrics), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False) if args.json else f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
