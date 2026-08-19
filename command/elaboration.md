---
description: Phase 02 Elaboration loop. Generate use cases, entity model, and Gherkin tests from the BRC, verify traceability with a reviewer, iterate until PASS.
agent: build
---

# Boucle Phase 02 — Elaboration

À partir de la BRC (`docs/01-inception/brc.md`), génère les livrables d'Élaboration et valide la traçabilité FR → use case → entité → scénario Gherkin jusqu'à PASS.

Champ optionnel : $ARGUMENTS

## Précondition

`docs/01-inception/brc.md` doit exister et être approuvée. Si elle n'existe pas, dis-le et renvoie vers la commande `/brc`.

## Étapes (goal loop)

1. Charge le skill `phase-elaboration`.
2. Lis la BRC et `docs/status.md` (s'il existe). Écris l'état : `next: générer élaboration`, et ajoute la ligne d'itération 1 au log. Démarre la trace : `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py start --loop elaboration --iteration <n> --phase 02 --livrable <fichier>`.
3. Génère les 4 fichiers dans `docs/02-elaboration/` :
   - `business-use-cases.md` (Mermaid)
   - `entity-model.md` (erDiagram)
   - `system-use-cases.md` (Mermaid)
   - `test-cases.md` (Gherkin + matrice de traçabilité FR → use case → entité → scénario)
4. Vérifie toi-même la matrice : chaque FR a au moins un use case, une entité et un scénario. Toute ligne manquante = boucle non finie.
5. Exécute le skill `self-challenge` sur les livrables (hypothèses, cas limites, alternatives, traçabilité, sécurité).
6. Lance le subagent `reviewer` pour vérifier la couverture et la qualité.
   Valide son bloc JSON avec `tools/verdict/validate_verdict.py`; une sortie
   invalide ou un fallback d'agent est une erreur d'infrastructure, jamais un PASS.
7. Si FAIL : corrige et relance le reviewer. Maximum 3 itérations. À chaque verdict, ajoute une ligne au log d'itérations (itération, verdict, cause du FAIL obligatoire) et un événement à la trace : `trace_log.py add --loop elaboration --iteration <n> --event verdict --verdict FAIL --cause "<cause>"` puis incrémente `<n>` et `trace_log.py start` pour l'itération suivante.
8. Au PASS : mets à jour `docs/status.md` (`done: élaboration validée` / `next: Phase 03`) et note le PASS dans le log. Clôture la trace : `trace_log.py end --loop elaboration --iteration <n> --verdict PASS --cost auto` puis `trace_log.py report`.
9. Résume et propose un commit (`docs(elaboration): add use cases, entity model and test cases`).

Ne rends pas la main avant PASS ou 3 itérations épuisées.

## Trace du loop

La trace (`tools/loop-trace/trace_log.py`) mesure latence et coût de chaque itération ; elle est écrite dans `.loop-trace/` (append-only) et le rapport dans `docs/loop-trace.md`. Dans les commandes ci-dessous, remplace `trace_log.py` par `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py`. Au blocage (3 itérations épuisées), clôture par `trace_log.py end --loop elaboration --iteration <n> --verdict FAIL --cause "<blocage>"` puis `trace_log.py report`.
