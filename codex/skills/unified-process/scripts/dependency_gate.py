#!/usr/bin/env python3
"""Validate a deliverable DAG and classify pending nodes."""

import argparse
import json
from pathlib import Path

STATUSES = {"pending", "in_progress", "done", "blocked", "skipped"}


def validate(graph):
    if graph.get("schema_version") != "1.0" or not isinstance(graph.get("nodes"), list):
        return ["schema_version 1.0 and nodes are required"]
    errors, nodes = [], graph["nodes"]
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if len(ids) != len(nodes) or any(not isinstance(x, str) or not x for x in ids): errors.append("every node requires an id")
    if len(ids) != len(set(ids)): errors.append("node ids must be unique")
    known = set(ids)
    adjacency = {}
    for node in nodes:
        if not isinstance(node, dict): continue
        if set(node) != {"id", "depends_on", "status"}: errors.append(f"{node.get('id')}: invalid fields")
        if node.get("status") not in STATUSES: errors.append(f"{node.get('id')}: invalid status")
        deps = node.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps): errors.append(f"{node.get('id')}: invalid dependencies"); deps = []
        if not set(deps) <= known: errors.append(f"{node.get('id')}: unknown dependencies")
        if node.get("id"): adjacency[node["id"]] = deps
    visiting, visited = set(), set()
    def cyclic(node_id):
        if node_id in visiting: return True
        if node_id in visited: return False
        visiting.add(node_id)
        if any(cyclic(dep) for dep in adjacency.get(node_id, [])): return True
        visiting.remove(node_id); visited.add(node_id); return False
    if any(cyclic(node_id) for node_id in adjacency): errors.append("dependency graph contains a cycle")
    return errors


def classify(graph):
    by_id = {node["id"]: node for node in graph["nodes"]}
    result = {"runnable": [], "waiting": [], "dependency_blocked": []}
    for node in graph["nodes"]:
        if node["status"] != "pending": continue
        states = [by_id[x]["status"] for x in node["depends_on"]]
        bucket = "dependency_blocked" if any(x in {"blocked", "skipped"} for x in states) else "runnable" if all(x == "done" for x in states) else "waiting"
        result[bucket].append(node["id"])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path("docs/dependency-graph.json"))
    args = parser.parse_args()
    try: graph = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]})); return 2
    errors = validate(graph)
    print(json.dumps({"valid": not errors, "errors": errors, **({} if errors else classify(graph))}, ensure_ascii=False))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
