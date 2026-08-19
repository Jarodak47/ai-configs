---
description: Phase 01 Inception loop. Generate the BRC, verify it with an independent reviewer, iterate until PASS.
agent: build
---

# Boucle Phase 01 — Inception

Génère la Business Requirements Catalog (BRC) pour le projet décrit ci-dessous, puis valide-la par un vérifieur indépendant jusqu'à PASS.

Projet : $ARGUMENTS

## Étapes (goal loop)

1. Charge le skill `phase-inception`.
2. Si un **cahier de charge** est fourni (chemin de fichier ou texte) : charge le skill `spec-analysis`, analyse-le, produis `docs/01-inception/cahier-de-charge-analysis.md`, résous les ambiguïtés avec moi AVANT d'écrire la BRC. Sinon, pose les questions de cadrage directement.
3. Vérifie si `docs/status.md` existe — sinon copie le modèle `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/templates/status.md`. Écris l'état AVANT de commencer : `next: générer BRC`, et ajoute la ligne d'itération 1 au log. Démarre la trace : `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py start --loop brc --iteration <n> --phase 01 --livrable BRC`.
4. Interroge-moi sur les ambiguïtés AVANT d'écrire (acteurs, portée, contraintes). Si $ARGUMENTS est vague, pose des questions ciblées.
5. Génère `docs/01-inception/brc.md` selon le format du skill.
6. Exécute le skill `self-challenge` sur la BRC (hypothèses, cas limites, alternatives, traçabilité, sécurité).
7. Lance le subagent `reviewer` pour exécuter la checklist de validation sur le fichier.
   Valide son bloc JSON avec `tools/verdict/validate_verdict.py`; une sortie
   invalide ou un fallback d'agent est une erreur d'infrastructure, jamais un PASS.
8. Si le verdict est FAIL : corrige les problèmes signalés et relance le reviewer. Maximum 3 itérations — au-delà, arrête et expose les blocages. À chaque verdict, ajoute une ligne au log d'itérations de `docs/status.md` (itération, verdict, cause du FAIL obligatoire) et un événement à la trace : `trace_log.py add --loop brc --iteration <n> --event verdict --verdict FAIL --cause "<cause>"` puis incrémente `<n>` et `trace_log.py start` pour l'itération suivante.
9. Au PASS : mets à jour `docs/status.md` (`done: BRC approuvée` / `next: Phase 02`) et note le PASS dans le log. Clôture la trace : `trace_log.py end --loop brc --iteration <n> --verdict PASS --cost auto` puis `trace_log.py report` (écrit `docs/loop-trace.md`).
10. Résume le résultat et propose une branche + un message de commit Conventional Commits (`docs(inception): add business requirements catalog`).

Ne rends pas la main avant que le verdict soit PASS ou que les 3 itérations soient épuisées.

## Trace du loop

La trace (`tools/loop-trace/trace_log.py`) mesure latence et coût de chaque itération ; elle est écrite dans `.loop-trace/` (append-only) et le rapport dans `docs/loop-trace.md`. Dans les commandes ci-dessous, remplace `trace_log.py` par `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py`. Au blocage (3 itérations épuisées), clôture l'itération courante par `trace_log.py end --loop brc --iteration <n> --verdict FAIL --cause "<blocage>"` puis `trace_log.py report`.
