#!/usr/bin/env python3
"""loop_eval.py — Eval harness déterministe du loop engineering AGENTS.md.

Parse `docs/status.md` et `docs/pipeline-report.md` puis calcule les métriques
du loop : taux de PASS par phase, répartition des itérations, fréquence des
causes de FAIL, blocages. Écrit `docs/metrics.md`.

Lecture seule : ne modifie jamais les sources (historique de status.md intact).

Usage:
    python3 loop_eval.py [--project-dir PATH] [--out docs/metrics.md]
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PHASE_KEYWORDS = {
    3: ("code", "test", "implément", "implement", "documentation", "docs "),
    4: ("transition", "uat", "deploiement", "déploiement", "backlog", "feedback", "release"),
    1: ("brc", "cahier", "inception"),
    2: ("elab", "use case", "entite", "entity", "modele", "model", "gherkin", "scenario", "scénario"),
}

CAUSE_CATEGORIES = {
    "tests": ("test",),
    "lint": ("lint",),
    "sécurité": ("séc", "secur", "auth", "injection", "idor", "csrf"),
    "architecture": ("architect", "pattern", "clean", "hexagonal", "couplage", "solid"),
    "traçabilité / cohérence": ("cohéren", "traç", "trac", "matrice", "manquant de lien"),
    "spec / exigence": ("spéc", "spec", "exigence", " fr "),
    "incomplet / manquant": ("manqu", "absent", "incomplet"),
    "bug / erreur": ("erreur", "bug", "exception", "crash"),
}

PHASE_LABELS = {0: "autre", 1: "01 Inception", 2: "02 Élaboration", 3: "03 Construction", 4: "04 Transition"}


def detect_phase(livrable):
    # La phase 03 est exclusive : un livrable qui mentionne code/tests/docs est
    # de la construction, même s'il cite aussi "use case" (ex. "code use case 1").
    s = livrable.lower()
    for phase in (3, 4, 1, 2):
        if any(k in s for k in PHASE_KEYWORDS[phase]):
            return phase
    return 0


def classify_cause(raw):
    s = raw.lower()
    for cat, kws in CAUSE_CATEGORIES.items():
        if any(k in s for k in kws):
            return cat
    return "autre"


def parse_status(status_path):
    if not status_path.exists():
        return [], "introuvable"
    rows = []
    for line in status_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        if not re.fullmatch(r"\d+", cells[0]):
            continue
        if set(cells[1]) <= set("-: ") or cells[1].lower().startswith("livrable"):
            continue
        rows.append({
            "num": int(cells[0]),
            "livrable": cells[1],
            "iteration": cells[2],
            "verdict": cells[3],
            "cause": cells[4],
            "corrige": cells[5],
        })
    return rows, "ok"


def extract_project_name(status_path):
    if status_path.exists():
        for line in status_path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"#+\s*Status\s*[—–-]\s*(.+)", line)
            if m:
                return m.group(1).strip()
    return ""


def pipeline_phase(text):
    if not text:
        return None
    found = sorted({int(m) for m in re.findall(r"Phase\s+0?([1-4])\b", text)})
    return found[-1] if found else None


def build_report(deliverables, project_name, pipeline_note, generated_at):
    total = len(deliverables)
    decided = [d for d in deliverables if d["final_verdict"] in ("PASS", "FAIL")]
    passed = [d for d in decided if d["final_verdict"] == "PASS"]
    failed = [d for d in decided if d["final_verdict"] == "FAIL"]
    pass_rate = 100.0 * len(passed) / len(decided) if decided else 0.0
    avg_iters = sum(d["iterations"] for d in passed) / len(passed) if passed else 0.0

    per_phase = defaultdict(list)
    for d in deliverables:
        per_phase[d["phase"]].append(d)

    cause_counter = Counter()
    raw_counter = Counter()
    for d in deliverables:
        for c in d["causes"]:
            cause_counter[classify_cause(c)] += 1
            raw_counter[c] += 1

    lines = []
    lines.append(f"# Metrics du loop engineering — {project_name or 'projet'}")
    lines.append("")
    lines.append(f"> Généré par `/metrics` — {generated_at}. Sources : `docs/status.md`, `docs/pipeline-report.md`.")
    lines.append("")
    lines.append("## Vue d'ensemble")
    lines.append("")
    lines.append(f"- **Livrables tentés** : {total}")
    lines.append(f"- **Taux de PASS** : {pass_rate:.1f}% ({len(passed)}/{len(decided)})" if decided else "- **Taux de PASS** : — (aucun livrable journalisé)")
    lines.append(f"- **Bloqués (FAIL final)** : {len(failed)}")
    lines.append(f"- **Itérations moy. par livrable PASS** : {avg_iters:.2f}" if passed else "- **Itérations moy. par livrable PASS** : —")
    if pipeline_note is not None:
        lines.append(f"- **Dernier run pipeline** : {PHASE_LABELS.get(pipeline_note, pipeline_note)}")
    lines.append("")

    lines.append("## Par phase")
    lines.append("")
    lines.append("| Phase | Livrables | PASS | FAIL final | Itérations moy. |")
    lines.append("|---|---|---|---|---|")
    for phase in sorted(per_phase):
        items = per_phase[phase]
        p = [d for d in items if d["final_verdict"] == "PASS"]
        f = [d for d in items if d["final_verdict"] == "FAIL"]
        avg = sum(d["iterations"] for d in p) / len(p) if p else 0.0
        avg_s = f"{avg:.2f}" if p else "—"
        lines.append(f"| {PHASE_LABELS.get(phase, phase)} | {len(items)} | {len(p)} | {len(f)} | {avg_s} |")
    lines.append("")

    lines.append("## Distribution des itérations (verdicts décidés)")
    lines.append("")
    lines.append("| Itérations | Livrables |")
    lines.append("|---|---|")
    dist = Counter()
    for d in decided:
        dist[d["iterations"]] += 1
    if dist:
        for bucket in sorted(dist):
            lines.append(f"| {bucket} | {dist[bucket]} |")
    else:
        lines.append("| — | — |")
    lines.append("")

    lines.append("## Causes de FAIL (catégorisées)")
    lines.append("")
    lines.append("| Cause | Occurrences |")
    lines.append("|---|---|")
    if cause_counter:
        for cat, n in cause_counter.most_common():
            lines.append(f"| {cat} | {n} |")
    else:
        lines.append("| — | — |")
    lines.append("")

    lines.append("## Livrables détaillés")
    lines.append("")
    lines.append("| Livrable | Phase | Itérations | Verdict final | Causes |")
    lines.append("|---|---|---|---|---|")
    for d in sorted(deliverables, key=lambda x: x["phase"]):
        causes = "; ".join(d["causes"]) if d["causes"] else "—"
        lines.append(f"| {d['name']} | {PHASE_LABELS.get(d['phase'], d['phase'])} | {d['iterations']} | {d['final_verdict']} | {causes} |")
    lines.append("")

    lines.append("## Méthode")
    lines.append("")
    lines.append("- Parse déterministe de `docs/status.md` (log d'itérations) — pas de jugement LLM.")
    lines.append("- `verdict final` = dernière ligne de chaque livrable ; `Itérations` = max de la colonne Itération.")
    lines.append("- Catégorisation des causes par mots-clés ; les causes brutes restent dans le log.")
    lines.append("- Ce fichier est régénéré à chaque `/metrics` — modifier les sources, pas ce rapport.")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Eval harness du loop engineering AGENTS.md")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--out", default="docs/metrics.md")
    args = parser.parse_args(argv)

    project = Path(args.project_dir).resolve()
    status_path = project / "docs" / "status.md"
    report_path = project / "docs" / "pipeline-report.md"

    rows, state = parse_status(status_path)
    if state == "introuvable":
        print("ERREUR: docs/status.md introuvable — exécute /new-project ou une commande de phase d'abord.", file=sys.stderr)
        return 1

    pipeline_note = None
    if report_path.exists():
        pipeline_note = pipeline_phase(report_path.read_text(encoding="utf-8", errors="replace"))

    by_livrable = defaultdict(list)
    for r in rows:
        by_livrable[r["livrable"].strip().lower()].append(r)

    deliverables = []
    for key, rs in by_livrable.items():
        iterations = []
        verdicts = []
        causes = []
        for r in rs:
            m = re.fullmatch(r"(\d+)", r["iteration"])
            if m:
                iterations.append(int(m.group(1)))
            v = re.search(r"PASS|FAIL", r["verdict"], re.I)
            verdicts.append(v.group(0).upper() if v else "INCONNU")
            if v and v.group(0).upper() == "FAIL" and r["cause"] and r["cause"].strip() not in ("—", "-", ""):
                causes.append(r["cause"].strip())
        final_verdict = verdicts[-1] if verdicts else "INCONNU"
        max_it = max(iterations) if iterations else len(rs)
        deliverables.append({
            "name": key,
            "phase": detect_phase(key),
            "attempts": len(rs),
            "iterations": max_it,
            "final_verdict": final_verdict,
            "causes": causes,
        })

    project_name = extract_project_name(status_path)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = build_report(deliverables, project_name, pipeline_note, generated_at)

    out_path = project / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report + "\n", encoding="utf-8")

    decided = [d for d in deliverables if d["final_verdict"] in ("PASS", "FAIL")]
    passed = sum(1 for d in decided if d["final_verdict"] == "PASS")
    rate = 100.0 * passed / len(decided) if decided else 0.0
    print(f"Rapport écrit : {out_path}")
    print(f"Livrables tentés : {len(deliverables)} | Taux de PASS : {rate:.1f}% ({passed}/{len(decided)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
