#!/usr/bin/env python3
"""calibrate_reviewer.py — Calibration du reviewer (gap #3 du loop engineering).

Lance le subagent `reviewer` sur un jeu de livrables de référence à vérité
connue, compare son verdict au ground truth et produit une matrice de
confusion + métriques (accuracy, précision, rappel, taux FN/FP).

Le ground truth n'est jamais révélé au reviewer dans le prompt.

Usage:
    calibrate_reviewer.py [--case ID] [--timeout 180] [--model MODEL] [--agent reviewer]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("OPENCODE_CONFIG_DIR", Path.home() / ".config" / "opencode"))
TOOL_DIR = CONFIG_HOME / "tools" / "reviewer-calibration"
CASES_DIR = TOOL_DIR / "cases"
RESULTS_PATH = TOOL_DIR / "results.json"
REPORT_PATH = TOOL_DIR / "report.md"
INFRA_REPORT_PATH = TOOL_DIR / "infrastructure-error-report.md"
OPENCODE = shutil.which("opencode") or "/usr/local/bin/opencode"
VERDICT_VALIDATOR = CONFIG_HOME / "tools" / "verdict" / "validate_verdict.py"


def load_cases():
    cases = []
    for case_dir in sorted(CASES_DIR.iterdir()):
        truth = case_dir / "truth.json"
        if not truth.exists():
            continue
        data = json.loads(truth.read_text(encoding="utf-8"))
        cases.append({
            "id": case_dir.name,
            "deliverable": case_dir / "deliverable",
            "truth": data,
        })
    return cases


def build_prompt(case, sandbox):
    truth = case["truth"]
    test_cmd = truth.get("test_command")
    lines = [
        "Tu es le reviewer indépendant de la méthodologie AGENTS.md.",
        "",
        f"Phase concernée : {truth.get('phase', 'non précisée')}.",
        "Livrable à passer en revue : le répertoire courant (.).",
    ]
    if test_cmd:
        lines.append(f"Commande de test à exécuter réellement : {test_cmd}")
    lines += [
        "",
        "Consignes :",
        "- N'édite aucun fichier.",
        "- Applique UNIQUEMENT la checklist de validation de la phase concernée (BRC, élaboration, code+tests, transition).",
        "- N'invente aucune exigence absente de la checklist : ne réclame pas de sections qui n'y figurent pas.",
        "- Pour du code : exécute réellement les tests/lint fournis — un verdict sans exécution est un échec de revue.",
        "- Vérifie aussi l'absence de secrets, de valeurs codées en dur, la conformité de nommage, et les vulnérabilités évidentes du code (IDOR, auth/autorisation manquante, input non validé).",
        "- Produis le verdict humain puis le bloc structuré VERDICT_JSON_BEGIN / VERDICT_JSON_END.",
        "- Le JSON doit respecter protocols/verdict.schema.json et contenir les preuves.",
    ]
    return "\n".join(lines)


def run_reviewer(sandbox, prompt, timeout, model, agent="reviewer"):
    cmd = [OPENCODE, "run", "--dir", str(sandbox), "--agent", agent, "--auto"]
    if model:
        cmd += ["--model", model]
    cmd += [prompt]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired:
        return None, f"TIMEOUT (> {timeout}s)"
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    if re.search(r"agent\s+[\"']?.+?[\"']?\s+is\s+a\s+subagent,\s+not\s+a\s+primary", clean, re.I):
        return None, "INFRA_ERROR: requested agent fell back to the default agent"
    match = re.search(r"VERDICT_JSON_BEGIN\s*(\{.*?\})\s*VERDICT_JSON_END", clean, re.S)
    if not match:
        return None, "INFRA_ERROR: structured verdict missing"
    check = subprocess.run([sys.executable, str(VERDICT_VALIDATOR)], input=match.group(1),
                           capture_output=True, text=True)
    if check.returncode != 0:
        return None, "INFRA_ERROR: " + check.stderr.strip()[:300]
    payload = json.loads(match.group(1))
    reason = "; ".join(item["message"] for item in payload["findings"][:3])
    if not reason:
        reason = "; ".join(payload["evidence"][:3])
    return payload["verdict"], reason[:300]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calibration du reviewer AGENTS.md")
    parser.add_argument("--case", help="ID d'un cas seul (sinon tous)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="timeout par invocation reviewer (s) — les cas à structure docs/ complète dépassent 180 s")
    parser.add_argument("--model", default=None)
    parser.add_argument("--agent", default="calibration-runner",
                        help="agent primaire de relais; un subagent direct est refusé pour éviter les fallbacks")
    parser.add_argument("--runs", type=int, default=1,
                        help="nombre de runs par cas (>=1) pour mesurer la variance")
    args = parser.parse_args(argv)

    cases = load_cases()
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"ERREUR: cas introuvable : {args.case}", file=sys.stderr)
            return 1
    if not cases:
        print("ERREUR: aucun cas dans " + str(CASES_DIR), file=sys.stderr)
        return 1

    results = []
    for case in cases:
        label = f"{args.runs} runs" if args.runs > 1 else "1 run"
        print(f"  {case['id']}: lancement du reviewer ({label})...", flush=True)
        for run in range(1, args.runs + 1):
            with tempfile.TemporaryDirectory(prefix="calib-") as tmp:
                sandbox = Path(tmp) / "deliverable"
                shutil.copytree(case["deliverable"], sandbox)
                prompt = build_prompt(case, sandbox)
                predicted, note = run_reviewer(sandbox, prompt, args.timeout, args.model, args.agent)

            truth = case["truth"]["verdict"]
            correct = (predicted == truth)
            results.append({
                "id": case["id"],
                "phase": case["truth"].get("phase", "?"),
                "truth": truth,
                "run": run,
                "predicted": predicted or "PARSE_FAIL",
                "correct": correct if predicted else None,
                "reason": note,
            })
            status = "✓" if correct else ("⚠" if predicted is None else "✗")
            print(f"    run {run}: {status} truth={truth} prédit={predicted or 'PARSE_FAIL'}")

    decided = [r for r in results if r["predicted"] in ("PASS", "FAIL")]
    tp = sum(1 for r in decided if r["predicted"] == "FAIL" and r["truth"] == "FAIL")
    fp = sum(1 for r in decided if r["predicted"] == "FAIL" and r["truth"] == "PASS")
    fn = sum(1 for r in decided if r["predicted"] == "PASS" and r["truth"] == "FAIL")
    tn = sum(1 for r in decided if r["predicted"] == "PASS" and r["truth"] == "PASS")
    n = len(decided)

    acc = (tp + tn) / n if n else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fn_rate = fn / (tp + fn) if (tp + fn) else 0.0
    fp_rate = fp / (tn + fp) if (tn + fp) else 0.0

    stability = {}
    for r in results:
        d = stability.setdefault(r["id"], {"truth": r["truth"], "preds": []})
        if r["predicted"] in ("PASS", "FAIL"):
            d["preds"].append(r["predicted"])
    stable_cases = sum(1 for d in stability.values()
                       if d["preds"] and len(set(d["preds"])) == 1)
    instable_cases = [cid for cid, d in stability.items()
                      if len(set(d["preds"])) > 1]

    metrics = {"accuracy": acc, "precision": prec, "recall": recall,
               "fn_rate": fn_rate, "fp_rate": fp_rate, "n": n,
               "tp": tp, "fp": fp, "fn": fn, "tn": tn,
               "runs": args.runs, "stable_cases": stable_cases,
               "instable_cases": instable_cases,
               "judge_model": args.model or "session-default",
               "independence": "cross-model" if args.model else "same-model"}

    if not decided:
        lines = ["# Calibration — erreur d'infrastructure", "",
                 f"> {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
                 "Aucun verdict exploitable. Le dernier rapport valide est conservé.", ""]
        for row in results:
            lines.append(f"- **{row['id']}** run {row['run']}: {row['reason']}")
        INFRA_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nErreur d'infrastructure : {INFRA_REPORT_PATH}", file=sys.stderr)
        return 2

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    history = load_history()
    history.append({"ts": now, "metrics": metrics, "cases": results})
    RESULTS_PATH.write_text(json.dumps({"runs": history}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(results, metrics, history)
    print(f"\nRapport écrit : {REPORT_PATH}")
    print(f"Accuracy : {acc:.0%} | Précision : {prec:.0%} | Rappel : {recall:.0%} | FN rate : {fn_rate:.0%} | FP rate : {fp_rate:.0%}")
    if args.runs > 1:
        print(f"Stabilité : {stable_cases}/{len(stability)} cas stables"
              + (f" — instables : {', '.join(instable_cases)}" if instable_cases else ""))
    print(f"Modèle juge : {metrics['judge_model']} ({metrics['independence']})")
    return 0


def load_history():
    if RESULTS_PATH.exists():
        try:
            return json.loads(RESULTS_PATH.read_text(encoding="utf-8")).get("runs", [])
        except (json.JSONDecodeError, OSError):
            pass
    return []


def write_report(results, metrics, history):
    lines = ["# Calibration du reviewer", ""]
    lines.append(f"> Généré par calibrate_reviewer.py — {datetime.now().strftime('%Y-%m-%d %H:%M')} "
                 f"({metrics['runs']} run(s) par cas).")
    lines.append("")
    lines.append("## Matrice de confusion (dernier run)")
    lines.append("")
    lines.append("| | Vérité FAIL | Vérité PASS |")
    lines.append("|---|---|---|")
    lines.append(f"| Prédit FAIL | TP = {metrics['tp']} | FP = {metrics['fp']} |")
    lines.append(f"| Prédit PASS | FN = {metrics['fn']} | TN = {metrics['tn']} |")
    lines.append("")
    lines.append("## Métriques")
    lines.append("")
    lines.append(f"- **Accuracy** : {metrics['accuracy']:.0%} ({metrics['n']} verdicts décidés, "
                 f"{metrics['runs']} run(s) x {metrics['n'] // max(metrics['runs'],1)} cas)")
    lines.append(f"- **Précision** (détection de FAIL) : {metrics['precision']:.0%}")
    lines.append(f"- **Rappel** (détection de FAIL) : {metrics['recall']:.0%}")
    lines.append(f"- **Taux de faux négatifs** : {metrics['fn_rate']:.0%}")
    lines.append(f"- **Taux de faux positifs** : {metrics['fp_rate']:.0%}")
    lines.append("")
    lines.append("## Diversité du modèle juge (P2.8)")
    lines.append("")
    judge_model = metrics.get("judge_model", "session-default")
    independence = metrics.get("independence", "same-model")
    lines.append(f"- **Modèle juge utilisé** : `{judge_model}`")
    lines.append(f"- **Indépendance juge / worker** : `{independence}`")
    if independence == "cross-model":
        lines.append("  - Le modèle juge a été fourni explicitement (`--model`) et déclaré différent du worker.")
    else:
        lines.append("  - La run a utilisé le modèle de session : juge et worker sont le **même modèle** —")
        lines.append("    limitation connue, mesurée et signalée ici (P2.8), coût nul.")
        lines.append("    La lever quand un second modèle est disponible : relancer avec `--model <juge>`.")
        lines.append("    Un écart d'accuracy ≥ 5 points vs le baseline cross-model indiquerait un biais de modèle.")
    lines.append("")
    lines.append("## Par cas")
    lines.append("")
    lines.append("| Cas | Phase | Vérité | Verdicts (runs) | Correct |")
    lines.append("|---|---|---|---|---|")
    from collections import Counter, OrderedDict
    agg = OrderedDict()
    for r in results:
        agg.setdefault(r["id"], {"phase": r["phase"], "truth": r["truth"], "preds": []})
        agg[r["id"]]["preds"].append(r["predicted"])
    for cid, d in agg.items():
        counts = Counter(d["preds"])
        verdicts = ", ".join(f"{v}×{c}" for v, c in sorted(counts.items()))
        ok = all(d["truth"] == p for p in d["preds"])
        lines.append(f"| {cid} | {d['phase']} | {d['truth']} | {verdicts or 'aucun'} | "
                     f"{'✓' if ok else '⚠' if not d['preds'] else '✗'} |")
    lines.append("")
    if metrics["runs"] > 1:
        lines.append("## Stabilité (multi-runs)")
        lines.append("")
        lines.append(f"- **Cas stables** : {metrics['stable_cases']}/{len(agg)} (tous les runs donnent le même verdict).")
        if metrics["instable_cases"]:
            lines.append(f"- **Cas instables** : {', '.join(metrics['instable_cases'])} — le verdict varie selon le run. "
                         "À examiner : renforcer la checklist/prompt, ou accepter la stochasticité en documentant le seuil.")
        else:
            lines.append("- Aucun cas instable : les verdicts sont reproductibles sur ce jeu.")
        lines.append("")
    lines.append("## Raisons des verdicts (dernier run)")
    lines.append("")
    for r in results:
        if r.get("reason"):
            lines.append(f"- **{r['id']}** (run {r['run']}, prédit {r['predicted']}) : {r['reason']}")
    lines.append("")
    lines.append("## Historique")
    lines.append("")
    lines.append("| Run | Date | Accuracy | FN rate | FP rate | Runs/cas | Stables |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, h in enumerate(history, start=1):
        m = h["metrics"]
        stable = f"{m.get('stable_cases')}/{len(m.get('instable_cases', [])) + m.get('stable_cases', 0)}" \
            if m.get("runs", 1) > 1 else "—"
        lines.append(f"| {i} | {h['ts']} | {m['accuracy']:.0%} | {m['fn_rate']:.0%} | "
                     f"{m['fp_rate']:.0%} | {m.get('runs', 1)} | {stable} |")
    lines.append("")
    lines.append("## Interprétation")
    lines.append("")
    if metrics["n"] == 0:
        lines.append("- Aucun verdict exploitable (timeouts/parsing) — corriger avant de conclure.")
    else:
        lines.append(f"- **Faux négatifs ({metrics['fn']})** = problèmes réels manqués par le reviewer (PASS alors que FAIL attendu). "
                     f"Rate : {metrics['fn_rate']:.0%}. Au-delà de ~20 %, ne pas faire confiance aux PASS : renforcer la checklist/le prompt.")
        lines.append(f"- **Faux positifs ({metrics['fp']})** = blocages injustifiés. Rate : {metrics['fp_rate']:.0%}. "
                     "Au-delà de ~30 %, le loop ralentit : clarifier les critères pour éviter les faux blocages.")
        if metrics["runs"] > 1 and metrics["instable_cases"]:
            lines.append(f"- **Stochasticité** : {len(metrics['instable_cases'])} cas instable(s) "
                         f"({', '.join(metrics['instable_cases'])}) — relancer pour confirmer avant conclusion.")
        fn_cases = sorted({r["id"] for r in results if r["correct"] is False and r["truth"] == "FAIL"})
        fp_cases = sorted({r["id"] for r in results if r["correct"] is False and r["truth"] == "PASS"})
        if fn_cases:
            lines.append(f"- Faux négatifs sur : {', '.join(fn_cases)} — à examiner en priorité.")
        if fp_cases:
            lines.append(f"- Faux positifs sur : {', '.join(fp_cases)}.")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
