---
description: "Boucle d'évaluation du loop engineering : parse docs/status.md et docs/pipeline-report.md, calcule les métriques (taux de PASS, itérations, causes de FAIL) via loop_eval.py, écrit docs/metrics.md et propose les prochaines améliorations. Usage : /metrics"
agent: build
---

# Boucle Eval — métriques du loop engineering

Mesure le loop engineering de ce projet avec la skill `loop-eval`, de façon déterministe.

## Étapes (goal loop)

1. Charge le skill `loop-eval`.
2. Vérifie que `docs/status.md` existe. S'il n'existe pas : le dire, ne rien générer (il faut d'abord initialiser le projet via `/new-project` ou lancer une phase).
3. Lance le script : `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-eval/loop_eval.py --project-dir .`
4. Lis le rapport `docs/metrics.md` généré et le résumé stdout.
5. Exécute le skill `self-challenge` sur le rapport (cohérence, hypothèses, cas limites, traçabilité).
6. Propose 1-2 prochaines améliorations ciblées par les données — ex. la phase avec le plus de FAIL, la cause dominante (tests ? lint ? sécurité ?) — et demande quoi faire.
7. Si la donnée révèle un problème de log (causes absentes, livrables nommés différemment), signale-le : c'est une dette de collecte, pas une anomalie du loop.
8. Propose une branche (`docs/loop-metrics`) et un commit Conventional Commits (`docs(metrics): add loop evaluation report`).

Le script étant déterministe, il n'y a pas de gate reviewer : la vérification est la relecture du rapport + self-challenge. Ne modifie jamais `docs/status.md` ni `docs/pipeline-report.md`.
