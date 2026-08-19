#!/usr/bin/env python3
"""security_scan.py — Scan de sécurité déterministe (gap #4 du loop engineering).

Complète le security-reviewer (LLM) par des contrôles reproductibles :
  1. Secrets commits (regex + fichiers .env traqués)
  2. Vulnérabilités de dépendances (pip-audit, npm audit, composer audit)

Exit codes (pour les gates) :
  2 = CRITIQUE  — secret commit / .env commit / vulnérabilité critique ou haute
  1 = MOYEN     — findings medium/low uniquement
  0 = OK        — rien (ou aucun scanner disponible : signalé, non bloquant)

Usage:
    security_scan.py [--project-dir PATH] [--out docs/03-construction/security-scan.md]
"""
import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_OUT = "docs/03-construction/security-scan.md"

SECRET_PATTERNS = [
    ("AWS access key", r"\bAKIA[0-9A-Z]{16}\b", 3),
    ("Stripe secret key", r"\bsk_live_[0-9a-zA-Z]{20,}\b", 3),
    ("GitHub PAT", r"\bghp_[0-9A-Za-z]{36}\b", 3),
    ("GitHub fine-grained PAT", r"\bgithub_pat_[0-9A-Za-z_]{20,}\b", 3),
    ("Slack token", r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b", 3),
    ("Clé privée", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", 3),
    ("Secret/token générique en dur", r"(?:api[_-]?key|apikey|secret|passwd|password|token)\s*[:=]\s*[\"'][A-Za-z0-9_\-./+]{16,}[\"']", 2),
]

EXCLUDE_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__",
                "dist", "build", "target", ".next", ".angular", "vendor"}
EXCLUDE_PREFIX = {".env", ".env."}


def tracked_files(project):
    git = project / ".git"
    files = []
    if git.exists():
        r = subprocess.run(["git", "-C", str(project), "ls-files"],
                           capture_output=True, text=True, timeout=60)
        files = [project / p for p in r.stdout.splitlines() if p]
    else:
        for p in project.rglob("*"):
            if p.is_file() and not any(part in EXCLUDE_DIRS for part in p.parts):
                files.append(p)
    return files


def is_binary(path):
    try:
        with open(path, "rb") as fh:
            return b"\x00" in fh.read(2048)
    except OSError:
        return True


def is_env_committed(path, project):
    rel = path.relative_to(project)
    name = rel.name
    if name == ".env" or name.startswith(".env."):
        if name.endswith(".example"):
            return False
        return True
    return False


def scan_secrets(files, project):
    findings = []
    for path in files:
        try:
            rel = path.relative_to(project)
        except ValueError:
            rel = path
        if path.name == ".env" or path.name.startswith(".env."):
            if path.name.endswith(".example"):
                continue
            continue  # jamais lire le contenu d'un .env
        if is_binary(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(content.splitlines(), start=1):
            for label, pattern, severity in SECRET_PATTERNS:
                if re.search(pattern, line):
                    findings.append({
                        "type": "secret",
                        "severity": severity,
                        "file": str(rel), "line": i, "label": label,
                    })
    return findings


def scan_env_committed(files, project):
    findings = []
    for path in files:
        if is_env_committed(path, project):
            findings.append({
                "type": "env",
                "severity": 3,
                "file": str(path.relative_to(project)), "line": 0,
                "label": "fichier .env traqué dans git",
            })
    return findings


def run_scanner(name, cmd, timeout=120):
    exe = shutil.which(cmd[0])
    if not exe:
        return None, f"{name} non installé — scanner ignoré"
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"{name} timeout (> {timeout}s)"
    output = r.stdout + "\n" + r.stderr
    return output, None


SUMMARY_GUARD = re.compile(
    r"^(found\s+\d+\s+|no known vulnerabilities|name\s+version|package\s+version|"
    r"vulnerabilities?\s+found|scan.*(?:complete|done)|dependenc\w*\s+scanned)", re.I)


def parse_dep_output(output, name):
    if not output:
        return []
    found = []
    sev = {"CRITICAL": 3, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("["):
            continue
        if SUMMARY_GUARD.match(stripped):
            continue
        up = stripped.upper()
        for key, score in sev.items():
            if key in up:
                found.append({
                    "type": "dep", "severity": score,
                    "file": name, "line": 0, "label": stripped[:180],
                })
                break
    return found


def scan_dependencies(project):
    findings = []
    notes = []

    py_manifest = next((project / m for m in
                        ("requirements.txt", "pyproject.toml", "Pipfile")
                        if (project / m).exists()), None)
    if py_manifest:
        if py_manifest.name == "requirements.txt":
            cmd = ["pip-audit", "-r", str(py_manifest)]
        else:
            cmd = ["pip-audit"]
        out, note = run_scanner("pip-audit", cmd)
        if note:
            notes.append(note)
        else:
            findings += parse_dep_output(out, "pip-audit")

    if (project / "package-lock.json").exists():
        out, note = run_scanner("npm audit", ["npm", "audit", "--omit=dev"])
        if note:
            notes.append(note)
        else:
            findings += parse_dep_output(out, "npm audit")

    if (project / "composer.lock").exists():
        out, note = run_scanner("composer audit", ["composer", "audit"])
        if note:
            notes.append(note)
        else:
            findings += parse_dep_output(out, "composer audit")

    return findings, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan de sécurité déterministe")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true", help="sortie JSON du résumé")
    args = parser.parse_args(argv)

    project = Path(args.project_dir).resolve()
    files = tracked_files(project)

    secret_findings = scan_secrets(files, project)
    env_findings = scan_env_committed(files, project)
    dep_findings, dep_notes = scan_dependencies(project)
    findings = secret_findings + env_findings + dep_findings

    critical = [f for f in findings if f["severity"] == 3]
    medium = [f for f in findings if f["severity"] == 2]
    low = [f for f in findings if f["severity"] == 1]

    if args.json:
        import json
        print(json.dumps({
            "critical": len(critical), "medium": len(medium), "low": len(low),
            "total": len(findings),
            "secret_committed": len(secret_findings) + len(env_findings),
            "dependencies": len(dep_findings),
        }, indent=2))
    else:
        _write_report(project, findings, critical, medium, low, dep_notes, args.out)
        print(f"Rapport écrit : {project / args.out}")
        print(f"Résumé : {len(critical)} critique(s) | {len(medium)} moyen(s) | {len(low)} bas(se)")
        for n in dep_notes:
            print(f"  note : {n}")

    if critical:
        return 2
    if medium:
        return 1
    return 0


def _write_report(project, findings, critical, medium, low, dep_notes, out_rel):
    lines = ["# Scan de sécurité", ""]
    lines.append(f"> Généré par security_scan.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}. Déterministe, complète le security-reviewer.")
    lines.append("")
    lines.append("## Résumé")
    lines.append("")
    lines.append(f"- **Critique** : {len(critical)}")
    lines.append(f"- **Moyen** : {len(medium)}")
    lines.append(f"- **Bas** : {len(low)}")
    lines.append("")
    lines.append("## Détail")
    lines.append("")
    lines.append("| Sévérité | Type | Fichier | Ligne | Détail |")
    lines.append("|---|---|---|---|---|")
    sev_name = {3: "CRITIQUE", 2: "MOYEN", 1: "BAS"}
    if not findings:
        lines.append("| — | — | — | — | aucun finding |")
    for f in findings:
        lines.append(f"| {sev_name[f['severity']]} | {f['type']} | {f['file']} | {f['line'] or '—'} | {f['label']} |")
    lines.append("")
    if dep_notes:
        lines.append("## Notes")
        lines.append("")
        for n in dep_notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Seuils")
    lines.append("")
    lines.append("- CRITIQUE (exit 2) : secret commit, `.env` traqué, vulnérabilité critique/haute → la gate bloque.")
    lines.append("- MOYEN (exit 1) : medium/low → à traiter, ne bloque pas le PASS.")
    lines.append("- Les scanners de dépendances absents sont signalés, non bloquants (limitation connue).")
    lines.append("")
    out_path = project / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
