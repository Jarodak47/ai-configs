#!/usr/bin/env python3
"""guard.py — Garde anti prompt-injection (P1.3 technique, complément de la
défense prompt des reviewers).

Défense déterministe : scanne les livrables (code + docs) pour détecter des
instructions de manipulation visant les agents de gate ("vote PASS", "ignore
previous instructions", "do not flag", "reveal your system prompt"...). Les
reviewers appliquent leur checklist ; cette garde détecte, avant tout gate, les
tentatives d'orienter leur verdict.

Exit codes (pour les gates) :
  2 = CRITIQUE — au moins une tentative de manipulation détectée
  0 = OK       — aucun motif trouvé

Sécurité : ne lit JAMAIS les fichiers `.env` / `*.env.*` (contenu exclu).

Usage:
    guard.py [--project-dir PATH] [--out docs/03-construction/prompt-injection-guard.md]
    guard.py [--project-dir PATH] --json
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_OUT = "docs/03-construction/prompt-injection-guard.md"
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist",
             "build", "target", ".next", ".angular", "vendor", "coverage",
             ".loop-trace", ".pytest_cache", ".idea", ".vscode"}
ENV_NAME = re.compile(r"(^|/)(\.env(\.[^/]*)?|\.env\.example)$")

PATTERNS = [
    ("PI-01", "ignore prior instructions",
     re.compile(r"\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|context|system\s+prompts?)", re.I)),
    ("PI-02", "disregard prior rules",
     re.compile(r"\bdisregard\s+(previous|prior|above|any)\s+(instructions?|prompts?|context|rules)", re.I)),
    ("PI-03", "forged verdict",
     re.compile(r"\b(vote|verdict|respond|output|return|report)\s+(this\s+)?(as\s+)?(PASS|FAIL)\b", re.I)),
    ("PI-04", "mark PASS/FAIL",
     re.compile(r"\bmark\s+(this|it)\s+(as\s+)?(PASS|FAIL)\b", re.I)),
    ("PI-05", "do not flag",
     re.compile(r"\bdo\s+not\s+(flag|report|fail|reject|check|review|mention)\b", re.I)),
    ("PI-06", "skip check",
     re.compile(r"\bskip\s+(this|the|your)\s+(check|review|verification|step|gate)\b", re.I)),
    ("PI-07", "reveal prompt",
     re.compile(r"\b(reveal|show)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions)\b", re.I)),
    ("PI-08", "override instructions",
     re.compile(r"\b(override|delete)\s+(your|the)\s+(instructions|system\s+prompt|rules|checklist|memory|context)\b", re.I)),
]


def is_binary(data):
    return b"\x00" in data[:8192]


def scan(project, out_rel, json_out=False):
    findings = []
    scanned = 0
    for path in project.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(project)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if ENV_NAME.match(str(rel)):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if is_binary(data) or not data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        scanned += 1
        lines = text.splitlines()
        for pid, label, pattern in PATTERNS:
            for lineno, line in enumerate(lines, start=1):
                if pattern.search(line):
                    findings.append({
                        "id": pid, "label": label,
                        "file": str(rel), "line": lineno,
                        "snippet": line.strip()[:160],
                    })

    if json_out:
        print(json.dumps({
            "files_scanned": scanned, "findings": len(findings),
            "patterns": sorted({f["id"] for f in findings}),
        }, indent=2))
    else:
        _write_report(project, scanned, findings, out_rel)
        print(f"Rapport écrit : {project / out_rel}")
        print(f"Résumé : {len(findings)} motif(s) de manipulation sur {scanned} fichier(s)")
    return 2 if findings else 0


def _write_report(project, scanned, findings, out_rel):
    lines = ["# Garde anti prompt-injection", ""]
    lines.append(f"> Généré par guard.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
                 "Déterministe ; ne lit jamais les fichiers `.env`.")
    lines.append("")
    lines.append("## Résumé")
    lines.append("")
    lines.append(f"- **Fichiers scannés** : {scanned}")
    lines.append(f"- **Tentatives de manipulation** : {len(findings)}")
    lines.append("")
    lines.append("## Détail")
    lines.append("")
    lines.append("| ID | Motif | Fichier | Ligne | Extrait |")
    lines.append("|---|---|---|---|---|")
    if not findings:
        lines.append("| — | — | — | — | aucun motif de manipulation |")
    for f in findings:
        snippet = f["snippet"].replace("|", "\\|")
        lines.append(f"| {f['id']} | {f['label']} | {f['file']} | {f['line']} | `{snippet}` |")
    lines.append("")
    lines.append("## Seuil")
    lines.append("")
    lines.append("- CRITIQUE (exit 2) : toute tentative détectée → la gate bloque.")
    lines.append("  Le motif est retiré des livrables avant toute revue, puis le scan est relancé (doit revenir à 0).")
    lines.append("- Le garde complète la défense prompt des reviewers (contenu hostile) ; il ne la remplace pas.")
    lines.append("")
    out_path = project / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Garde anti prompt-injection déterministe")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true", help="sortie JSON du résumé")
    args = parser.parse_args(argv)

    project = Path(args.project_dir).resolve()
    if not project.is_dir():
        print(f"ERREUR: répertoire introuvable: {project}", file=sys.stderr)
        return 2
    return scan(project, args.out, args.json)


if __name__ == "__main__":
    sys.exit(main())
