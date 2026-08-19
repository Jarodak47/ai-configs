#!/usr/bin/env python3
"""Initialize Unified Process project records without overwriting files."""

import argparse
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DOC_DIRS = ("01-inception", "02-elaboration", "03-construction", "04-transition")
IGNORE_ENTRIES = (".env", "*.env", "build/", "dist/", "__pycache__/", "node_modules/", "*.log", ".loop-trace/")


def create_once(path, content):
    if path.exists() or path.is_symlink():
        return "kept"
    path.write_text(content, encoding="utf-8")
    return "created"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_dir.resolve()
    if not project.is_dir():
        raise SystemExit(f"project directory does not exist: {project}")
    forbidden = {Path("/").resolve(), Path.home().resolve(), Path.home().joinpath(".codex").resolve()}
    if project in forbidden:
        raise SystemExit(f"refusing broad or configuration directory: {project}")
    docs = project / "docs"
    for name in DOC_DIRS:
        (docs / name).mkdir(parents=True, exist_ok=True)
    project_name = project.name
    status = (SKILL_DIR / "assets/status-template.md").read_text(encoding="utf-8").replace("PROJECT_NAME", project_name)
    graph = (SKILL_DIR / "assets/dependency-graph.json").read_text(encoding="utf-8")
    changes = {
        "status": create_once(docs / "status.md", status),
        "dependency_graph": create_once(docs / "dependency-graph.json", graph),
    }
    ignore = project / ".gitignore"
    existing = ignore.read_text(encoding="utf-8").splitlines() if ignore.exists() else []
    missing = [entry for entry in IGNORE_ENTRIES if entry not in existing]
    if missing:
        prefix = "" if not existing or (ignore.exists() and ignore.read_text(encoding="utf-8").endswith("\n")) else "\n"
        with ignore.open("a", encoding="utf-8") as handle:
            handle.write(prefix + "\n".join(missing) + "\n")
    changes["gitignore_entries_added"] = missing
    print(json.dumps(changes, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
