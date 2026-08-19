#!/usr/bin/env python3
"""trace_log.py — Trace runtime du loop engineering AGENTS.md.

Enregistre, pour chaque itération d'une boucle de phase, les événements
`start` / `add` / `end` avec horodatage, verdict, cause du FAIL, coût (réel via
`--cost auto` ou manuel) et latence calculée entre `start` et `end`.
Génère un rapport déterministe et détecte les itérations non clôturées.

Complémentaire de `loop_eval.py` :
  - loop_eval : rétrospectif — parse docs/status.md après coup.
  - trace_log  : runtime — mesure la latence et le coût pendant l'exécution.

Coût réel : lu dans la base opencode (`~/.local/share/opencode/opencode.db`,
table `session.cost`), en sommant la session du projet et ses descendants
(sous-agents). `--cost auto` enregistre cette valeur ; le rapport affiche le
coût incrémental par itération (delta entre deux `end` consécutifs d'une même
boucle).

Stockage brut (append-only, jamais réécrit) : <project-dir>/.loop-trace/<loop_id>.jsonl
Rapport : <project-dir>/docs/loop-trace.md

Usage:
    trace_log.py start  --loop <id> --iteration <n> [--phase 01|02|03|04] [--livrable <nom>]
    trace_log.py add    --loop <id> --iteration <n> --event <nom> [--verdict PASS|FAIL] [--cause <texte>] [--cost <n>|auto] [--note <texte>]
    trace_log.py end    --loop <id> --iteration <n> [--verdict PASS|FAIL] [--cause <texte>] [--cost <n>|auto]
    trace_log.py cost   [--project-dir .] [--db <chemin>]
    trace_log.py check  [--project-dir .]
    trace_log.py report [--out docs/loop-trace.md]
"""
import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

VERDICTS = ("PASS", "FAIL")
DEFAULT_DB = Path.home() / ".local/share/opencode/opencode.db"


def trace_file(project_dir, loop):
    return Path(project_dir) / ".loop-trace" / f"{loop}.jsonl"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def resolve_cost(db_path, project_dir):
    """Coût cumulé (session du projet + descendants) depuis la base opencode.

    Retourne (cost, tokens_dict) ou None si aucune session n'est trouvée.
    """
    db_path = Path(db_path)
    proj = str(Path(project_dir).resolve())
    if not db_path.exists():
        return None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, cost, tokens_input, tokens_output, tokens_reasoning "
            "FROM session WHERE directory = ? ORDER BY time_updated DESC LIMIT 1",
            (proj,),
        )
        root = cur.fetchone()
        if not root:
            return None
        root_id, root_cost, ti, to, tr = root
        total = root_cost or 0.0
        tokens = {"input": ti or 0, "output": to or 0, "reasoning": tr or 0}
        cur.execute("SELECT id, parent_id, cost FROM session")
        child_map = {}
        for sid, parent, cost in cur.fetchall():
            child_map.setdefault(parent, []).append((sid, cost or 0.0))
        stack = [root_id]
        while stack:
            parent_id = stack.pop()
            for sid, cost in child_map.get(parent_id, []):
                total += cost
                stack.append(sid)
        return round(total, 4), tokens
    finally:
        con.close()


def append_event(project_dir, loop, **fields):
    path = trace_file(project_dir, loop)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": round(time.time(), 3),
        "iso": now_iso(),
        "loop": loop,
        **fields,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def read_events(project_dir):
    rows = []
    root = Path(project_dir) / ".loop-trace"
    if not root.exists():
        return rows
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _resolve_cost_arg(args, value):
    """Transforme --cost (nombre ou 'auto') en (valeur, source)."""
    if value is None:
        return None, "manual"
    if value != "auto":
        try:
            return float(value), "manual"
        except ValueError:
            raise SystemExit(f"ERREUR: --cost doit être un nombre ou 'auto', obtenu '{value}'")
    resolved = resolve_cost(args.db, args.project_dir)
    if resolved is None:
        print("WARNING: aucune session opencode trouvée pour ce projet — coût non enregistré.",
              file=sys.stderr)
        return None, "auto"
    cost, _tokens = resolved
    return cost, "auto"


def cmd_start(args):
    path = append_event(args.project_dir, args.loop,
                        iteration=args.iteration,
                        event="start", phase=args.phase, livrable=args.livrable)
    print(f"Trace : itération {args.iteration} de {args.loop} démarrée -> {path}")


def cmd_add(args):
    cost, source = _resolve_cost_arg(args, args.cost)
    path = append_event(args.project_dir, args.loop,
                        iteration=args.iteration, event=args.event,
                        verdict=args.verdict, cause=args.cause,
                        cost=cost, cost_source=source, note=args.note)
    print(f"Trace : {args.event} ajouté ({args.loop} #{args.iteration}) -> {path}")


def cmd_end(args):
    cost, source = _resolve_cost_arg(args, args.cost)
    path = append_event(args.project_dir, args.loop,
                        iteration=args.iteration, event="end",
                        verdict=args.verdict, cause=args.cause,
                        cost=cost, cost_source=source)
    print(f"Trace : itération {args.iteration} de {args.loop} clôturée -> {path}")


def cmd_cost(args):
    resolved = resolve_cost(args.db, args.project_dir)
    if resolved is None:
        print("ERREUR: aucune session opencode trouvée pour ce projet "
              f"({Path(args.project_dir).resolve()}).", file=sys.stderr)
        return 1
    cost, tokens = resolved
    print(f"cost: {cost:.4f}")
    print(f"tokens_input: {tokens['input']}")
    print(f"tokens_output: {tokens['output']}")
    print(f"tokens_reasoning: {tokens['reasoning']}")
    return 0


def unclosed_iterations(rows):
    """Itérations (loop, iteration) démarrées mais jamais clôturées."""
    by_iter = {}
    for r in rows:
        by_iter.setdefault((r["loop"], r["iteration"]), []).append(r)
    return [
        (loop, iteration)
        for (loop, iteration), evs in sorted(by_iter.items())
        if any(e["event"] == "start" for e in evs)
        and not any(e["event"] == "end" for e in evs)
    ]


def cmd_check(args):
    rows = read_events(args.project_dir)
    if not rows:
        print("ERREUR: aucun événement dans .loop-trace/ — lance 'trace_log.py start' d'abord.",
              file=sys.stderr)
        return 1
    unclosed = unclosed_iterations(rows)
    if not unclosed:
        print("OK : toutes les itérations tracées sont clôturées.")
        return 0
    print(f"NON CLÔTURÉES : {len(unclosed)} itération(s) sans 'end' :")
    for loop, iteration in unclosed:
        print(f"  - {loop} #{iteration}")
    return 1


def build_report(rows, project_name, generated_at):
    by_iter = {}
    for r in rows:
        by_iter.setdefault((r["loop"], r["iteration"]), []).append(r)

    iters = []
    for (loop, iteration), evs in sorted(by_iter.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        start = next((e for e in evs if e["event"] == "start"), None)
        end = next((e for e in evs if e["event"] == "end"), None)
        phase = next((e.get("phase") for e in evs if e.get("phase")), "—")
        livrable = next((e.get("livrable") for e in evs if e.get("livrable")), "—")
        verdict = next((e.get("verdict") for e in evs if e.get("verdict")), "INCONNU")
        cause = next((e.get("cause") for e in evs if e.get("cause")), "—")
        cost_events = [e for e in evs if e.get("cost") is not None]
        cost = cost_events[-1]["cost"] if cost_events else None
        cost_source = cost_events[-1].get("cost_source", "manual") if cost_events else "manual"
        duration = None
        if start and end:
            duration = max(0.0, end["ts"] - start["ts"])
        iters.append({
            "loop": loop, "iteration": iteration, "phase": phase,
            "livrable": livrable, "start_iso": start["iso"] if start else "—",
            "duration": duration, "verdict": verdict, "cause": cause,
            "cost": cost, "cost_source": cost_source, "closed": end is not None,
        })

    prev_auto = {}
    for it in iters:
        if it["cost"] is None:
            it["cost_display"] = "—"
            continue
        if it["cost_source"] == "auto":
            prev_val = prev_auto.get(it["loop"])
            inc = it["cost"] - prev_val if prev_val is not None else None
            it["cost_display"] = f"{inc:.3f}" if inc is not None else f"{it['cost']:.3f}*"
            prev_auto[it["loop"]] = it["cost"]
        else:
            it["cost_display"] = f"{it['cost']:.3f}"

    by_loop = {}
    for it in iters:
        by_loop.setdefault(it["loop"], []).append(it)

    lines = []
    lines.append(f"# Trace du loop — {project_name or 'projet'}")
    lines.append("")
    lines.append(f"> Généré par `trace_log.py` — {generated_at}. Source : `.loop-trace/*.jsonl` (append-only).")
    lines.append("")

    total_dur = sum(it["duration"] for it in iters if it["duration"] is not None)
    costs = [it["cost"] for it in iters if it["cost"] is not None and it["cost_source"] == "manual"]
    unclosed = unclosed_iterations(rows)
    lines.append("## Résumé")
    lines.append("")
    lines.append(f"- **Boucles** : {len(by_loop)}")
    lines.append(f"- **Itérations tracées** : {len(iters)}")
    lines.append(f"- **Durée totale** : {total_dur:.1f} s")
    if costs:
        lines.append(f"- **Coût total (manuel)** : {sum(costs):.3f}")
    else:
        lines.append("- **Coût total** : voir les coûts cumulés par boucle (`--cost auto`)")
    if unclosed:
        lines.append(f"- **⚠ Itérations non clôturées** : {len(unclosed)} — lance `trace_log.py check`")
    lines.append("")

    lines.append("## Par boucle")
    lines.append("")
    lines.append("| Loop | Itérations | Durée totale (s) | Latence moy. (s) | PASS | FAIL | Coût cumulé |")
    lines.append("|---|---|---|---|---|---|---|")
    for loop, its in sorted(by_loop.items()):
        d = sum(i["duration"] for i in its if i["duration"] is not None)
        n_dur = sum(1 for i in its if i["duration"] is not None)
        avg = d / n_dur if n_dur else 0.0
        pass_n = sum(1 for i in its if i["verdict"] == "PASS")
        fail_n = sum(1 for i in its if i["verdict"] == "FAIL")
        auto_vals = [i["cost"] for i in its if i["cost"] is not None and i["cost_source"] == "auto"]
        manual_vals = [i["cost"] for i in its if i["cost"] is not None and i["cost_source"] == "manual"]
        if auto_vals:
            c = f"{auto_vals[-1]:.3f}*"
        elif manual_vals:
            c = f"{sum(manual_vals):.3f}"
        else:
            c = "—"
        lines.append(f"| {loop} | {len(its)} | {d:.1f} | {avg:.1f} | {pass_n} | {fail_n} | {c} |")
    lines.append("")

    lines.append("## Détail des itérations")
    lines.append("")
    lines.append("| Loop | Itér | Phase | Livrable | Début | Durée (s) | Verdict | Cause du FAIL | Coût |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for it in iters:
        dur = f"{it['duration']:.1f}" if it["duration"] is not None else "—"
        lines.append(f"| {it['loop']} | {it['iteration']} | {it['phase']} | {it['livrable']} | "
                     f"{it['start_iso']} | {dur} | {it['verdict']} | {it['cause']} | {it['cost_display']} |")
    lines.append("")

    lines.append("## Itérations non clôturées")
    lines.append("")
    if unclosed:
        lines.append("| Loop | Itér |")
        lines.append("|---|---|")
        for loop, iteration in unclosed:
            lines.append(f"| {loop} | {iteration} |")
    else:
        lines.append("Aucune — toutes les itérations ont un `end`.")
    lines.append("")

    lines.append("## Méthode")
    lines.append("")
    lines.append("- Événements JSON append-only dans `.loop-trace/<loop>.jsonl`, écrits par les commandes de phase (`/brc`, `/elaboration`, `/construction`, `/transition`).")
    lines.append("- **Latence** = `end.ts - start.ts` de la même itération (horodatage epoch, calcul déterministe).")
    lines.append("- **Coût** : `--cost auto` lit le cumul de session opencode (session du projet + sous-agents) ; le tableau affiche l'incrément entre deux `end` consécutifs d'une même boucle (`*` = première valeur, cumul de session). `--cost <n>` enregistre une valeur manuelle.")
    lines.append("- **Itérations non clôturées** = `start` sans `end` — détectées par `trace_log.py check` (exit 1).")
    lines.append("- Ce rapport est régénéré à chaque `trace_log.py report` — ne pas le modifier à la main.")
    lines.append("")
    return "\n".join(lines)


def cmd_report(args):
    rows = read_events(args.project_dir)
    if not rows:
        print("ERREUR: aucun événement dans .loop-trace/ — lance 'trace_log.py start' d'abord.",
              file=sys.stderr)
        return 1
    project_name = Path(args.project_dir).resolve().name
    out_path = Path(args.project_dir) / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(rows, project_name, now_iso())
    out_path.write_text(report + "\n", encoding="utf-8")
    print(f"Rapport écrit : {out_path}")
    n_loops = len({r["loop"] for r in rows})
    n_iters = len({(r["loop"], r["iteration"]) for r in rows})
    print(f"Itérations tracées : {n_iters} dans {n_loops} boucle(s)")
    unclosed = unclosed_iterations(rows)
    if unclosed:
        print(f"WARNING: {len(unclosed)} itération(s) non clôturée(s) — lance 'trace_log.py check'.",
              file=sys.stderr)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Trace runtime du loop engineering AGENTS.md")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project-dir", default=".")
    common.add_argument("--db", default=str(DEFAULT_DB))
    common.add_argument("--loop", required=True, help="identifiant de la boucle (ex. brc)")
    common.add_argument("--iteration", type=int, required=True)

    p_start = sub.add_parser("start", parents=[common], help="ouvre une itération")
    p_start.add_argument("--phase", choices=["01", "02", "03", "04"])
    p_start.add_argument("--livrable")
    p_start.set_defaults(func=cmd_start)

    p_add = sub.add_parser("add", parents=[common], help="ajoute un événement à l'itération")
    p_add.add_argument("--event", required=True)
    p_add.add_argument("--verdict", choices=VERDICTS)
    p_add.add_argument("--cause")
    p_add.add_argument("--cost", help="valeur numérique ou 'auto' (cumul session opencode)")
    p_add.add_argument("--note")
    p_add.set_defaults(func=cmd_add)

    p_end = sub.add_parser("end", parents=[common], help="clôture une itération (calcule la latence)")
    p_end.add_argument("--verdict", choices=VERDICTS)
    p_end.add_argument("--cause")
    p_end.add_argument("--cost", help="valeur numérique ou 'auto' (cumul session opencode)")
    p_end.set_defaults(func=cmd_end)

    p_cost = sub.add_parser("cost", help="affiche le coût cumulé de la session opencode du projet")
    p_cost.add_argument("--project-dir", default=".")
    p_cost.add_argument("--db", default=str(DEFAULT_DB))
    p_cost.set_defaults(func=cmd_cost)

    p_check = sub.add_parser("check", help="détecte les itérations non clôturées (exit 1 si trouvées)")
    p_check.add_argument("--project-dir", default=".")
    p_check.set_defaults(func=cmd_check)

    p_report = sub.add_parser("report", help="génère docs/loop-trace.md")
    p_report.add_argument("--project-dir", default=".")
    p_report.add_argument("--out", default="docs/loop-trace.md")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
