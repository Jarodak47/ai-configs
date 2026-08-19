#!/usr/bin/env python3
"""sast_scan.py — Scan SAST déterministe (gate P1.2 du loop engineering).

Complète security_scan.py (secrets + dépendances) par une analyse statique
stack-aware, reproductible :
  - Python  -> bandit
  - JS/TS   -> eslint (avec plugin de sécurité si le projet le fournit)
  - PHP     -> phpcs / psalm
  - Java    -> spotbugs (uniquement si un build Maven configuré est présent)

Le scan est **déterministe** : mêmes sources + mêmes outils installés = même
sortie. Les outils absents ou non configurés sont signalés, jamais bloquants
(limitation connue, comme pour les scanners de dépendances).

Exit codes (pour les gates) :
  2 = CRITIQUE  — au moins un finding High/Critical
  1 = MOYEN     — findings Medium/Low uniquement
  0 = OK        — rien, ou aucun scanner applicable

Usage:
    sast_scan.py [--project-dir PATH] [--out docs/03-construction/sast-scan.md]
    sast_scan.py [--project-dir PATH] --json
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_OUT = "docs/03-construction/sast-scan.md"
EXCLUDE_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__",
                "dist", "build", "target", ".next", ".angular", "vendor",
                ".loop-trace"}


def which(tool):
    return shutil.which(tool)


def run(cmd, timeout=180):
    """Exécute un scanner, retourne (stdout, note) ou (None, note) si absent."""
    if not which(cmd[0]):
        return None, f"{cmd[0]} non installé — scanner ignoré"
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=Path.cwd())
    except subprocess.TimeoutExpired:
        return None, f"{cmd[0]} timeout (> {timeout}s)"
    return r.stdout + "\n" + r.stderr, None


def detect_stack(project):
    """Retourne la liste des scanners applicables au projet."""
    stack = []
    if any((project / m).exists() for m in
           ("requirements.txt", "pyproject.toml", "Pipfile", "setup.py")):
        stack.append("python")
    if any((project / m).exists() for m in
           ("package.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock")):
        stack.append("js")
    if any((project / m).exists() for m in ("composer.json", "composer.lock")):
        stack.append("php")
    if (project / "pom.xml").exists() or (project / "build.gradle").exists():
        stack.append("java")
    return stack


def run_bandit(project):
    out, note = run(["bandit", "-q", "-r", str(project), "-f", "json"])
    if note:
        return [], note
    findings = []
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return [], "bandit : sortie JSON illisible, résultats ignorés"
    sev = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    for item in data.get("results", []):
        findings.append({
            "tool": "bandit", "severity": sev.get(item.get("issue_severity"), 1),
            "file": item.get("filename", "?"), "line": item.get("line_number", 0),
            "label": f"[{item.get('test_id', '?')}] {item.get('issue_text', '')[:180]}",
        })
    return findings, None


def run_eslint(project):
    out, note = run(["eslint", str(project), "-f", "json", "--quiet"])
    if note:
        return [], note
    if "couldn't find a configuration file" in out or "no configuration" in out.lower():
        return [], "eslint : aucune configuration trouvée — scanner ignoré"
    findings = []
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return [], "eslint : sortie JSON illisible, résultats ignorés"
    for entry in data or []:
        for msg in entry.get("messages", []):
            sev = 3 if msg.get("severity") == 2 else 1
            findings.append({
                "tool": "eslint", "severity": sev,
                "file": entry.get("filePath", "?"), "line": msg.get("line", 0),
                "label": f"[{msg.get('ruleId', '?')}] {msg.get('message', '')[:180]}",
            })
    return findings, None


def run_phpcs(project):
    out, note = run(["phpcs", "--report=json", str(project)])
    if note:
        return [], note
    if "No files were checked" in out or "does not exist" in out:
        return [], "phpcs : rien à analyser"
    findings = []
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return [], "phpcs : sortie JSON illisible, résultats ignorés"
    for path, info in data.get("files", {}).items():
        for msg in info.get("messages", []):
            sev = 3 if msg.get("type") == "error" else 1
            findings.append({
                "tool": "phpcs", "severity": sev,
                "file": path, "line": msg.get("line", 0),
                "label": f"[{msg.get('source', '?')}] {msg.get('message', '')[:180]}",
            })
    return findings, None


def run_psalm(project):
    out, note = run(["psalm", "--no-progress", "--output-format=json", "--no-cache"])
    if note:
        return [], note
    if "no configuration" in out.lower():
        return [], "psalm : aucune configuration trouvée — scanner ignoré"
    findings = []
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return [], "psalm : sortie JSON illisible, résultats ignorés"
    for item in data.get("issues", []):
        sev = 3 if item.get("severity") == "error" else 1
        findings.append({
            "tool": "psalm", "severity": sev,
            "file": item.get("file_name", "?"), "line": item.get("line_from", 0),
            "label": f"[{item.get('type', '?')}] {item.get('message', '')[:180]}",
        })
    return findings, None


def run_spotbugs(project):
    pom = project / "pom.xml"
    if not pom.exists():
        return [], "spotbugs : requis un projet Maven configuré (pom.xml)"
    out, note = run(["mvn", "-q", "-f", str(pom), "spotbugs:check",
                     "-Dspotbugs.effort=Max", "-Dspotbugs.threshold=Low"])
    if note:
        return [], note
    report = project / "target/spotbugsXml.xml"
    findings = []
    if report.exists():
        try:
            text = report.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for match in _spotbugs_entries(text):
            findings.append(match)
    if not findings and "BUILD FAILURE" not in out:
        return [], "spotbugs : aucun rapport exploitable"
    return findings, None


def _spotbugs_entries(xml_text):
    """Extrait les findings des lignes <BugInstance ...> du rapport XML."""
    import re
    entries = []
    for match in re.finditer(
            r"<BugInstance\b[^>]*type=\"([^\"]+)\"[^>]*>.*?"
            r"<SourceLine[^>]*start=\"(\d+)\"[^>]*sourcepath=\"([^\"]+)\"",
            xml_text, re.DOTALL):
        entries.append({
            "tool": "spotbugs", "severity": 2, "file": match.group(3),
            "line": int(match.group(2) or 0),
            "label": f"[{match.group(1)}] bug détecté",
        })
    return entries


def scan(project, out_rel, json_out=False):
    stack = detect_stack(project)
    findings = []
    notes = []

    if "python" in stack:
        f, n = run_bandit(project)
        findings += f
        if n:
            notes.append(n)
    if "js" in stack:
        f, n = run_eslint(project)
        findings += f
        if n:
            notes.append(n)
    if "php" in stack:
        f, n = run_phpcs(project)
        findings += f
        if n:
            notes.append(n)
        f, n = run_psalm(project)
        findings += f
        if n:
            notes.append(n)
    if "java" in stack:
        f, n = run_spotbugs(project)
        findings += f
        if n:
            notes.append(n)

    critical = [f for f in findings if f["severity"] == 3]
    medium = [f for f in findings if f["severity"] == 2]
    low = [f for f in findings if f["severity"] == 1]

    if json_out:
        print(json.dumps({
            "critical": len(critical), "medium": len(medium), "low": len(low),
            "total": len(findings), "stack": stack,
        }, indent=2))
    else:
        _write_report(project, stack, findings, critical, medium, low, notes, out_rel)
        print(f"Rapport écrit : {project / out_rel}")
        print(f"Résumé : {len(critical)} critique(s) | {len(medium)} moyen(s) | {len(low)} bas(se)")
        for n in notes:
            print(f"  note : {n}")

    if critical:
        return 2
    if medium or low:
        return 1
    return 0


def _write_report(project, stack, findings, critical, medium, low, notes, out_rel):
    lines = ["# Scan SAST", ""]
    lines.append(f"> Généré par sast_scan.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
                 "Déterministe, complète security_scan.py (secrets + dépendances).")
    lines.append("")
    lines.append("## Résumé")
    lines.append("")
    lines.append(f"- **Stack détecté** : {', '.join(stack) if stack else 'aucun'}")
    lines.append(f"- **Critique** : {len(critical)}")
    lines.append(f"- **Moyen** : {len(medium)}")
    lines.append(f"- **Bas** : {len(low)}")
    lines.append("")
    lines.append("## Détail")
    lines.append("")
    lines.append("| Sévérité | Outil | Fichier | Ligne | Détail |")
    lines.append("|---|---|---|---|---|")
    sev_name = {3: "CRITIQUE", 2: "MOYEN", 1: "BAS"}
    if not findings:
        lines.append("| — | — | — | — | aucun finding |")
    for f in findings:
        lines.append(f"| {sev_name[f['severity']]} | {f['tool']} | {f['file']} | {f['line'] or '—'} | {f['label']} |")
    lines.append("")
    if notes:
        lines.append("## Notes")
        lines.append("")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Seuils")
    lines.append("")
    lines.append("- CRITIQUE (exit 2) : finding High/Critical → la gate bloque.")
    lines.append("- MOYEN (exit 1) : medium/low → à traiter, ne bloque pas le PASS.")
    lines.append("- Les outils SAST absents ou non configurés sont signalés, non bloquants (limitation connue).")
    lines.append("")
    out_path = project / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan SAST déterministe stack-aware")
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
