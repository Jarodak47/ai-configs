#!/usr/bin/env python3
"""Validate a deliverable DAG and compute runnable and dependency-blocked nodes."""

import argparse
import json
from pathlib import Path

STATUSES = {"pending", "in_progress", "done", "blocked", "skipped"}


def validate(graph):
    errors = []
    if graph.get("schema_version") != "1.0" or not isinstance(graph.get("nodes"), list):
        return ["schema_version 1.0 and nodes array are required"]
    nodes = graph["nodes"]
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if len(ids) != len(nodes) or any(not isinstance(node_id, str) or not node_id for node_id in ids):
        errors.append("every node requires a non-empty id")
    if len(ids) != len(set(ids)):
        errors.append("node ids must be unique")
    known = set(ids)
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if set(node) != {"id", "depends_on", "status"}:
            errors.append(f"{node.get('id')}: invalid fields")
        if node.get("status") not in STATUSES:
            errors.append(f"{node.get('id')}: invalid status")
        deps = node.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            errors.append(f"{node.get('id')}: depends_on must be a string array")
        elif not set(deps) <= known:
            errors.append(f"{node.get('id')}: unknown dependencies {sorted(set(deps) - known)}")
    adjacency = {node["id"]: node.get("depends_on", []) for node in nodes if isinstance(node, dict) and node.get("id")}
    visiting, visited = set(), set()

    def visit(node_id):
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        if any(visit(dep) for dep in adjacency.get(node_id, [])):
            return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    if any(visit(node_id) for node_id in adjacency):
        errors.append("dependency graph contains a cycle")
    return errors


def classify(graph):
    by_id = {node["id"]: node for node in graph["nodes"]}
    runnable, waiting, dependency_blocked = [], [], []
    for node in graph["nodes"]:
        if node["status"] != "pending":
            continue
        dependency_statuses = [by_id[dep]["status"] for dep in node["depends_on"]]
        if any(status in {"blocked", "skipped"} for status in dependency_statuses):
            dependency_blocked.append(node["id"])
        elif all(status == "done" for status in dependency_statuses):
            runnable.append(node["id"])
        else:
            waiting.append(node["id"])
    return {"runnable": runnable, "waiting": waiting,
            "dependency_blocked": dependency_blocked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path("docs/dependency-graph.json"))
    args = parser.parse_args()
    try:
        graph = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}))
        return 2
    errors = validate(graph)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, **classify(graph)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
