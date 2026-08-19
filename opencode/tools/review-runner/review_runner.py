#!/usr/bin/env python3
"""Run reviewer commands in an isolated temporary copy of a project.

The command is executed without a shell. Git metadata and every .env variant
except .env.example are excluded from the copy. The source project is never the
working directory of the child process.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED_EXECUTABLES = {
    "python", "python3", "pytest", "ruff", "bandit", "pip-audit",
    "node", "npm", "npx", "pnpm", "yarn", "bun", "eslint", "tsc",
    "composer", "php", "mvn", "mvnw", "gradle", "gradlew",
    "make", "cmake", "ctest", "cargo", "go", "gitleaks", "semgrep",
    "osv-scanner",
}
FORBIDDEN_TOKENS = {"--force", "--delete", "--write", "--fix", "-w"}


def ignore_entries(_directory, names):
    ignored = set()
    for name in names:
        if name == ".git" or (name.startswith(".env") and name != ".env.example"):
            ignored.add(name)
        if name in {".loop-trace", "dist", "build", "coverage", ".pytest_cache", "__pycache__"}:
            ignored.add(name)
    return ignored


def validate_command(command):
    executable = Path(command[0]).name
    if executable not in ALLOWED_EXECUTABLES and not executable.startswith("python3"):
        raise ValueError(f"executable not allowed: {executable}")
    forbidden = FORBIDDEN_TOKENS.intersection(command[1:])
    if forbidden:
        raise ValueError(f"mutating option not allowed: {', '.join(sorted(forbidden))}")
    if executable in {"npm", "pnpm", "yarn", "bun"}:
        allowed_actions = {"test", "run", "exec", "audit", "lint", "check"}
        if len(command) < 2 or command[1] not in allowed_actions:
            raise ValueError(f"package-manager action not allowed: {command[1:]}")
    if executable in {"mvn", "mvnw", "gradle", "gradlew"} and not any(
        token in {"test", "check", "verify"} for token in command[1:]
    ):
        raise ValueError("build tool is restricted to test/check/verify")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    try:
        validate_command(command)
    except ValueError as error:
        print(f"DENIED: {error}", file=sys.stderr)
        return 2
    source = args.project_dir.resolve()
    if not source.is_dir():
        print(f"DENIED: project directory not found: {source}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="opencode-review-") as temporary:
        isolated = Path(temporary) / "project"
        shutil.copytree(source, isolated, symlinks=True, ignore=ignore_entries)
        environment = os.environ.copy()
        environment.update({"CI": "1", "OPENCODE_REVIEW_ISOLATED": "1"})
        try:
            result = subprocess.run(command, cwd=isolated, env=environment,
                                    text=True, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT after {args.timeout}s", file=sys.stderr)
            return 124
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
