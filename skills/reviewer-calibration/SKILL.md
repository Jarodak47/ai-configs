---
name: reviewer-calibration
description: Mesure la fiabilité du subagent reviewer AGENTS.md. Lance le vrai reviewer (via l'agent relais calibration-runner) sur un jeu de livrables de référence à vérité connue, calcule la matrice de confusion et les métriques (accuracy, précision, rappel, taux FN/FP). Use when the user asks to calibrate the reviewer, measure reviewer reliability, check reviewer accuracy, /calibrate, or after changing the reviewer prompt/checklists.
---

# Calibration du reviewer

Le reviewer est la gate du loop : un reviewer qui rate des problèmes (faux négatifs) fait passer du code défectueux ; un reviewer trop strict (faux positifs) ralentit le loop. On ne peut pas lui faire confiance à l'aveugle — on le **mesure** sur un jeu de référence à vérité connue.

## Méthode

1. Dataset : `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/reviewer-calibration/cases/<id>/`
   - `deliverable/` — le livrable à revoir
   - `truth.json` — `{phase, verdict, issues, test_command}` (la vérité connue, jamais révélée au reviewer)
2. Exécution : `calibrate_reviewer.py` lance le **vrai** subagent `reviewer` en headless (`opencode run --agent reviewer --auto`). Optionnel : `--agent calibration-runner` pour passer par l'agent relais (spawn via task tool).
3. Comparaison prédit vs vérité → matrice de confusion.

## Variance (mesurer la stochasticité)

- `calibrate_reviewer.py --runs N` répète chaque cas N fois (défaut 1).
- Un cas est **stable** si tous les runs donnent le même verdict ; **instable** sinon.
- Pour une mesure fiable : `--runs 3`. L'accuracy se lit sur l'ensemble des runs (N × cas).
- Rapport : section « Stabilité (multi-runs) » + colonne « Verdicts (runs) » par cas.

## Métriques

| Métrique | Définition | Seuil d'alerte |
|---|---|---|
| Accuracy | (TP+TN)/N | < 80 % |
| Précision | TP/(TP+FP) — qualité des blocs | — |
| Rappel | TP/(TP+FN) — problèmes détectés | — |
| **Taux de faux négatifs** | FN/(TP+FN) — problèmes manqués | > 20 % : ne pas faire confiance aux PASS |
| **Taux de faux positifs** | FP/(TN+FP) — faux blocages | > 30 % : le loop ralentit |

Les faux négatifs sont **le danger prioritaire** : un PASS trompeur est pire qu'un FAIL. Les faux positifs sont secondaires (ils coûtent des itérations, pas la qualité).

## Règles

- **Le ground truth n'est jamais transmis** au reviewer (ni dans le prompt, ni dans les fichiers — `truth.json` est exclu de la copie).
- L'évaluation est **stochastique** : un run isolé peut être bruité. Pour une mesure stable, relancer avec `--runs 3` et regarder l'historique, pas le dernier run.
- Un cas TIMEOUT/PARSE_FAIL est exclu des métriques mais visible dans le rapport.
- Quand un faux négatif apparaît : examiner la raison, renforcer la checklist de la phase concernée ou le prompt du reviewer, puis **re-calibrer** (le loop de calibration fait partie de l'amélioration).
- Ne jamais modifier `truth.json` pour "faire passer" le reviewer — c'est le reviewer qui doit s'adapter, pas le dataset.

## Validation checklist (utilisée par le reviewer)

- [ ] Tous les cas du dataset ont été exécutés (aucun silencieusement sauté)
- [ ] Ground truth jamais révélé dans les prompts
- [ ] Raisons des verdicts capturées et lisibles (pas d'ANSI/warning)
- [ ] Métriques calculées correctement (matrice cohérente)
- [ ] Stabilité mesurée sur les cas (multi-runs) quand `--runs > 1` ; cas instables listés
- [ ] Interprétation : seuils FN (>20 %) et FP (>30 %) commentés
- [ ] Historique conservé dans `results.json`

## Loop behavior

Quand la skill est utilisée dans la boucle `/calibrate` :

1. Exécute `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/reviewer-calibration/calibrate_reviewer.py --runs 3` (variance incluse).
2. Lis `report.md` (matrice, métriques, stabilité, raisons, historique).
3. Exécute le skill `self-challenge` sur le rapport.
4. Interprète selon les seuils : FN élevé → renforcer checklist/prompt ; FP élevé → clarifier les critères (ne pas inventer de sections) ; cas instables → relancer ou documenter la stochasticité.
5. Propose la suite : enrichir le dataset, relancer pour stabiliser, ou ajuster le prompt du reviewer.
