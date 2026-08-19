---
description: Phase 04 Transition loop. Generate UAT plan, deployment checklist, feedback report template, and improvement backlog from the approved specs, verify with a reviewer, iterate until PASS.
agent: build
---

# Boucle Phase 04 — Transition

À partir de la Phase 03 terminée (tous les use cases implémentés et validés), génère les livrables de Transition et valide-les par un vérifieur indépendant jusqu'à PASS.

Champ optionnel : $ARGUMENTS

## Précondition

`docs/status.md` doit montrer la Phase 03 complète. Sinon, dis-le et renvoie vers `/construction`.

## Étapes (goal loop)

1. Charge le skill `phase-transition`.
2. Lis `docs/status.md` et confirme que la Phase 03 est terminée. Écris l'état : `next: générer transition`, et ajoute la ligne d'itération 1 au log. Démarre la trace : `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py start --loop transition --iteration <n> --phase 04 --livrable <fichier>`.
3. Génère les 4 fichiers dans `docs/04-transition/` :
   - `uat-plan.md` (scope, acteurs, critères d'entrée/sortie, scénarios UAT mappés aux FR)
   - `deployment-checklist.md` (env vars par nom, migrations, backups, rollback, monitoring)
   - `feedback-report-template.md` (ce qui marche / échoue / idées / priorité)
   - `improvement-backlog.md` (backlog priorisé P0/P1/P2, traçable aux feedbacks)
4. Vérifie toi-même : chaque scénario UAT mappe à un FR + un critère de succès, aucun secret dans les fichiers.
5. Exécute le skill `self-challenge` sur les livrables (hypothèses, cas limites, traçabilité, sécurité).
6. Lance le subagent `reviewer` pour exécuter la checklist de validation.
   Valide son bloc JSON avec `tools/verdict/validate_verdict.py`; une sortie
   invalide ou un fallback d'agent est une erreur d'infrastructure, jamais un PASS.
7. Si FAIL : corrige et relance le reviewer. Maximum 3 itérations. À chaque verdict, ajoute une ligne au log d'itérations (itération, verdict, cause du FAIL obligatoire) et un événement à la trace : `trace_log.py add --loop transition --iteration <n> --event verdict --verdict FAIL --cause "<cause>"` puis incrémente `<n>` et `trace_log.py start` pour l'itération suivante.
8. Au PASS : mets à jour `docs/status.md` (`done: transition` / `next: release`) et note le PASS dans le log. Clôture la trace : `trace_log.py end --loop transition --iteration <n> --verdict PASS --cost auto` puis `trace_log.py report`.
9. Propose une branche et un commit (`docs(transition): add uat plan, deployment checklist and feedback template`).

Ne rends pas la main avant PASS ou 3 itérations épuisées.

## Trace du loop

La trace (`tools/loop-trace/trace_log.py`) mesure latence et coût de chaque itération ; elle est écrite dans `.loop-trace/` (append-only) et le rapport dans `docs/loop-trace.md`. Dans les commandes ci-dessous, remplace `trace_log.py` par `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-trace/trace_log.py`. Au blocage (3 itérations épuisées), clôture par `trace_log.py end --loop transition --iteration <n> --verdict FAIL --cause "<blocage>"` puis `trace_log.py report`.
