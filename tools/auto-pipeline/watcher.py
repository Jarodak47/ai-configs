#!/usr/bin/env python3
"""watcher.py — Auto-pipeline AGENTS.md (Option A : watcher local launchd).

Surveille une liste de projets (registre) et lance le pipeline-engineering en
headless (`opencode run`) quand du travail est en attente. Zéro fichier ajouté
dans les projets : toute la config vit sous OPENCODE_CONFIG_DIR.

Commandes :
    watcher.py check                 (défaut) évalue et lance les runs dus
    watcher.py list                  liste le registre
    watcher.py add --path P [--name N] [--brief "..."] [--force]
    watcher.py remove --path P
    watcher.py status                état des runs + état launchd
    watcher.py run --path P          force un run immédiat pour un projet
    watcher.py on                    charge l'agent launchd
    watcher.py off                   décharge l'agent launchd
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("OPENCODE_CONFIG_DIR", Path.home() / ".config/opencode"))
TOOLS_DIR = CONFIG_HOME / "tools" / "auto-pipeline"
REGISTRY_PATH = CONFIG_HOME / "projects.json"
RUNS_PATH = TOOLS_DIR / "runs.json"
LOCK_PATH = TOOLS_DIR / ".lock"
LOGS_DIR = TOOLS_DIR / "logs"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.jarodak47.opencode-autopipe.plist"

OPENCODE = shutil.which("opencode") or "/usr/local/bin/opencode"
AGENT = "pipeline-engineering"

TERMINAL_NEXT = {"", "—", "-", "aucune", "rien", "ras", "terminé", "terminée", "phase 04 terminée", "done", "fait", "fait."}


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            log(f"AVERTISSEMENT: {path} illisible — réinitialisation.")
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_registry():
    return load_json(REGISTRY_PATH, {"projects": [], "options": {"cooldownHours": 6, "maxRunHours": 4}})


def load_runs():
    return load_json(RUNS_PATH, {})


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def parse_iso(s):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def read_status_field(project_dir, field):
    p = Path(project_dir) / "docs" / "status.md"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if f"**{field}**" in line or re.match(rf"^-\s*{field}\s*:", line):
            m = re.search(r":\s*(.*)$", line)
            if m:
                return m.group(1).strip()
    return None


def is_terminal_next(value):
    if value is None:
        return False
    return value.strip().lower() in TERMINAL_NEXT


def git_head(project_dir):
    r = subprocess.run(["git", "-C", project_dir, "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def git_dirty(project_dir):
    r = subprocess.run(["git", "-C", project_dir, "status", "--porcelain"],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def has_pending_work(proj):
    path = Path(proj["path"])
    status_path = path / "docs" / "status.md"

    if not status_path.exists():
        # Projet pas encore initialisé : il faut un brief pour démarrer seul.
        return bool(proj.get("brief")), ("brief absent : projet non initialisé" if not proj.get("brief") else "projet non initialisé, brief présent")

    blocked = read_status_field(str(path), "blocked")
    if blocked and not is_terminal_next(blocked):
        return False, f"bloqué ({blocked}) — intervention requise"

    next_val = read_status_field(str(path), "next")
    if next_val is None:
        return True, "statut illisible, run de régularisation"
    if not is_terminal_next(next_val):
        return True, f"next : {next_val}"
    return False, f"terminé (next : {next_val})"


def decide(proj, runs, options):
    """Retourne (lancer: bool, raison: str)."""
    name = proj["name"]
    path = str(proj["path"])
    state = runs.get(name, {})
    last_end = parse_iso(state.get("lastRunEnd"))
    last_head = state.get("lastHead")
    last_next = state.get("lastNext")
    last_status = state.get("lastStatus")

    head = git_head(path) if Path(path).joinpath(".git").exists() else None
    dirty = git_dirty(path) if Path(path).joinpath(".git").exists() else False
    next_now = read_status_field(path, "next")
    changed = (head is not None and head != last_head) or dirty or (next_now != last_next)

    pending, reason = has_pending_work(proj)
    if not pending:
        return False, reason

    if last_end and not changed and last_status in ("success", "blocked"):
        return False, f"rien de nouveau depuis le dernier run ({last_status})"

    cooldown = float(options.get("cooldownHours", 6))
    if last_end and not changed and (datetime.now() - last_end).total_seconds() / 3600 < cooldown:
        return False, "cooldown actif"

    return True, reason


def lock_held():
    if not LOCK_PATH.exists():
        return False
    try:
        pid = int(LOCK_PATH.read_text().strip())
    except ValueError:
        return True
    if pid_alive(pid):
        return True
    LOCK_PATH.unlink(missing_ok=True)
    return False


def launch(proj, runs, msg, force=False):
    name = proj["name"]
    path = str(proj["path"])
    if lock_held() and not force:
        log(f"  {name}: un run est déjà en cours — saut.")
        return

    logs_dir = LOGS_DIR / name
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_log = logs_dir / f"run-{stamp}.log"

    cmd = [OPENCODE, "run", "--dir", path, "--agent", AGENT, "--auto", msg]
    log(f"  {name}: lancement -> {' '.join(cmd[:6])}...")

    with open(out_log, "w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT,
                                start_new_session=True)

    head = git_head(path) if Path(path).joinpath(".git").exists() else None
    next_now = read_status_field(path, "next")
    runs[name] = {
        "lastRunStart": now_iso(),
        "projectDir": path,
        "pid": proc.pid,
        "status": "running",
        "lastHead": head,
        "lastNext": next_now,
        "log": str(out_log),
    }
    save_json(RUNS_PATH, runs)
    LOCK_PATH.write_text(str(proc.pid), encoding="utf-8")
    log(f"  {name}: lancé (pid {proc.pid}), log {out_log}")


def reap(runs, options):
    """Met à jour l'état des runs terminés et libère le verrou."""
    changed = False
    max_hours = float(options.get("maxRunHours", 4))
    now = datetime.now()

    for name, state in list(runs.items()):
        if state.get("status") != "running":
            continue
        pid = state.get("pid")
        start = parse_iso(state.get("lastRunStart"))
        elapsed_hours = (now - start).total_seconds() / 3600 if start else 0

        if pid_alive(pid) and elapsed_hours <= max_hours:
            continue

        if pid_alive(pid) and elapsed_hours > max_hours:
            try:
                os.kill(pid, 15)
            except OSError:
                pass
            state["status"] = "timeout"
            log(f"  {name}: dépassement de {max_hours}h — run tué.")
        else:
            project_dir = Path(state.get("projectDir") or name)
            report = project_dir / "docs" / "pipeline-report.md"
            blockers = project_dir / "docs" / "blockers.md"
            start_ts = start.timestamp() if start else 0
            if blockers.exists() and blockers.stat().st_mtime >= start_ts:
                state["status"] = "blocked"
            elif report.exists() and report.stat().st_mtime >= start_ts:
                state["status"] = "success"
            else:
                state["status"] = "failed"
            log(f"  {name}: terminé ({state['status']}).")

        state["lastRunEnd"] = now_iso()
        state.pop("pid", None)
        if LOCK_PATH.exists():
            try:
                if int(LOCK_PATH.read_text().strip()) == pid:
                    LOCK_PATH.unlink(missing_ok=True)
            except ValueError:
                pass
        changed = True

    if changed:
        save_json(RUNS_PATH, runs)


def cmd_check(args):
    registry = load_registry()
    runs = load_runs()
    reap(runs, registry["options"])
    save_json(RUNS_PATH, runs)

    launched = 0
    for proj in registry["projects"]:
        name = proj["name"]
        if not Path(proj["path"]).exists():
            log(f"  {name}: chemin introuvable — saut.")
            continue
        run, reason = decide(proj, runs, registry["options"])
        log(f"  {name}: {'À LANCER' if run else 'skip'} — {reason}")
        if run:
            msg = proj.get("brief") or "Continue le pipeline AGENTS.md : reprends à l'état « next » de docs/status.md."
            launch(proj, runs, msg)
            launched += 1

    log(f"check terminé : {launched} run(s) lancé(s).")


def cmd_list(args):
    registry = load_registry()
    if not registry["projects"]:
        print("Registre vide. Ajoute un projet : watcher.py add --path <chemin> [--brief \"...\"]")
        return
    for p in registry["projects"]:
        flag = "*" if Path(p["path"]).exists() else "!"
        print(f"  {flag} {p['name']:30} {p['path']}  {'brief: '+p['brief'][:40] if p.get('brief') else ''}")


def cmd_add(args):
    path = str(Path(args.path).expanduser().resolve())
    if not Path(path).exists():
        print(f"ERREUR: chemin introuvable : {path}", file=sys.stderr)
        return 1
    registry = load_registry()
    name = args.name or Path(path).name
    for p in registry["projects"]:
        if p["path"] == path or p["name"] == name:
            if not args.force:
                print(f"ERREUR: projet déjà dans le registre ({p['name']}). Utilise --force pour écraser.", file=sys.stderr)
                return 1
            p.update({"name": name, "path": path, "brief": args.brief})
            save_json(REGISTRY_PATH, registry)
            print(f"  {name} mis à jour.")
            return 0
    registry["projects"].append({"name": name, "path": path, "brief": args.brief})
    save_json(REGISTRY_PATH, registry)
    print(f"  {name} ajouté au registre.")
    print("  Pour surveiller immédiatement, assure-toi que l'agent launchd est chargé : watcher.py on")


def cmd_remove(args):
    path = str(Path(args.path).expanduser().resolve())
    registry = load_registry()
    before = len(registry["projects"])
    registry["projects"] = [p for p in registry["projects"] if p["path"] != path and p["name"] != args.path]
    if len(registry["projects"]) == before:
        print(f"ERREUR: projet introuvable : {args.path}", file=sys.stderr)
        return 1
    save_json(REGISTRY_PATH, registry)
    print(f"  {args.path} retiré du registre.")


def cmd_run(args):
    path = str(Path(args.path).expanduser().resolve())
    registry = load_registry()
    runs = load_runs()
    for proj in registry["projects"]:
        if proj["path"] == path or proj["name"] == args.path:
            if not Path(proj["path"]).exists():
                print("ERREUR: chemin introuvable.", file=sys.stderr)
                return 1
            pending, reason = has_pending_work(proj)
            if not pending and not proj.get("brief"):
                print(f"Rien à lancer : {reason}. Utilise --brief pour un projet non initialisé.", file=sys.stderr)
                return 1
            msg = proj.get("brief") or "Continue le pipeline AGENTS.md : reprends à l'état « next » de docs/status.md."
            launch(proj, runs, msg, force=True)
            save_json(RUNS_PATH, runs)
            return 0
    print(f"ERREUR: projet introuvable dans le registre : {args.path}", file=sys.stderr)
    return 1


def cmd_status(args):
    runs = load_runs()
    print("== Registre ==")
    cmd_list(args)
    print("\n== Runs ==")
    if not runs:
        print("  (aucun run enregistré)")
    for name, s in sorted(runs.items()):
        pid = s.get("pid")
        running = f" (pid {pid} actif)" if pid and pid_alive(pid) else ""
        print(f"  {name:30} statut={s.get('status','?')}{running}  début={s.get('lastRunStart','—')}")
        if s.get("status") == "running" and not (pid and pid_alive(pid)):
            print("    ⚠  marqué running mais processus absent — sera réconcilié au prochain check")
    print("\n== Verrou ==")
    print("  occupé" if lock_held() else "  libre")
    print("\n== launchd ==")
    r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    loaded = "com.jarodak47.opencode-autopipe" in r.stdout
    print(f"  agent {'chargé' if loaded else 'non chargé'} ({PLIST_PATH.name})")


def cmd_on(args):
    if not PLIST_PATH.exists():
        print(f"ERREUR: plist introuvable : {PLIST_PATH}", file=sys.stderr)
        return 1
    subprocess.run(["launchctl", "load", str(PLIST_PATH)])
    print("  agent launchd chargé.")


def cmd_off(args):
    if PLIST_PATH.exists():
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)])
    print("  agent launchd déchargé.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Auto-pipeline AGENTS.md (watcher local launchd)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("check")
    sub.add_parser("list")
    p_add = sub.add_parser("add")
    p_add.add_argument("--path", required=True)
    p_add.add_argument("--name")
    p_add.add_argument("--brief")
    p_add.add_argument("--force", action="store_true")
    p_rm = sub.add_parser("remove")
    p_rm.add_argument("--path", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--path", required=True)
    sub.add_parser("status")
    sub.add_parser("on")
    sub.add_parser("off")
    args = parser.parse_args(argv)

    cmd = args.command or "check"
    handlers = {
        "check": cmd_check, "list": cmd_list, "add": cmd_add,
        "remove": cmd_remove, "run": cmd_run, "status": cmd_status,
        "on": cmd_on, "off": cmd_off,
    }
    try:
        return handlers[cmd](args) or 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
