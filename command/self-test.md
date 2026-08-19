---
description: Exécute le test d'intégration de la config opencode (intégrité des références, frontmatters, checklists de phase, numérotation, smoke tests des outils déterministes). Protection de non-régression — à lancer après toute modification des agents/commandes/skills/outils.
---
# Commande /self-test

Vérifie l'intégrité de la config opencode elle-même, sans LLM.

## Déroulement

1. Exécute :
   `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/integration-test/integration_test.py`

2. Interprète le résultat :
   - `PASS` (exit 0) : la config est saine.
   - `FAIL` (exit 1) : au moins un check casse. Lis `tools/integration-test/report.md` pour le détail et corrige **avant** de modifier d'autres composants.

3. **Itérations trace non clôturées** : si le projet courant contient un dossier `.loop-trace/`, exécute `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py check --project-dir .` et signale les itérations `start` sans `end` (boucles de phase interrompues) — sans rien modifier.

## Ce que le test vérifie

- Structure : agents, commandes, skills, outils, templates attendus présents.
- Frontmatters YAML valides (avec `description`).
- Références croisées : chaque `skill X` / `subagent X` / `tools/X/` / `templates/X` cité existe.
- Checklist de phase : les 4 skills `phase-*` ont leur section « ## Validation checklist » (le reviewer en dépend).
- Numérotation : pas de doublon dans les listes numérotées (section-aware).
- Smoke tests : `security_scan.py` (propre → exit 0, secret leaké → exit 2), `loop_eval.py` (rapport généré), `trace_log.py` (cycle start/add/end → rapport avec latence/coût, `check` détecte les itérations non clôturées, `cost` sans session → erreur propre) sur projets factices.

## Recommandation

Lance `/self-test` avant **chaque** `/calibrate` et après toute modification de la config.
