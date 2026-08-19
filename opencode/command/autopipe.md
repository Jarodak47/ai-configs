---
description: "Gère le watcher local (launchd) qui déclenche le pipeline AGENTS.md en headless. Sous-commandes : add <chemin> [--brief \"...\"], remove <chemin>, run <chemin>, status, list, on, off. Usage : /autopipe [sous-commande]"
agent: build
---

# Gestion du watcher auto-pipeline (launchd)

Le watcher surveille les projets enregistrés et lance le `pipeline-engineering` en headless (`opencode run --agent pipeline-engineering --auto`) quand du travail est en attente — sans GitHub Actions, sans fichier dans les projets.

Script : `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/auto-pipeline/watcher.py`
Registre : `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/projects.json`

Sous-commande : $ARGUMENTS

## Sous-commandes

- `add <chemin> [--brief "..."]` — enregistre un projet. Le `--brief` est **requis pour un projet non initialisé** (il sert de brief à la Phase 01). Sans brief, le projet doit déjà avoir `docs/status.md` avec du travail en attente.
- `remove <chemin>` — retire un projet du registre.
- `run <chemin>` — force un run immédiat pour un projet.
- `status` — état des runs, du verrou et de l'agent launchd.
- `list` — contenu du registre.
- `on` / `off` — charge / décharge l'agent launchd.

## Règles

1. Exécute `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/auto-pipeline/watcher.py <sous-commande>`.
2. Interprète la sortie : si `check` signale un skip « bloqué », explique que c'est une intervention humaine requise ; si « projet non initialisé sans brief », explique qu'il faut ajouter un `--brief`.
3. Après un `add` d'un projet avec brief, précise que le pipeline démarrera à la prochaine passe du watcher (toutes les 15 min) ou immédiatement via `run`.
4. Ne jamais modifier `projects.json` à la main — toujours via le script.
