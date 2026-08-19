---
name: loop-eval
description: Eval harness du loop engineering AGENTS.md. Parse docs/status.md et docs/pipeline-report.md via le script loop_eval.py, produit docs/metrics.md — taux de PASS par phase, répartition des itérations, fréquence des causes de FAIL, blocages. Use when the user asks for metrics, eval, evaluation, "mesurer le loop", /metrics, or after several phase runs.
---

# Eval harness du loop engineering

Measure le loop engineering lui-même : on ne peut pas améliorer ce qu'on ne mesure pas. Les métriques sont **calculées de façon déterministe** par le script `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-eval/loop_eval.py` — jamais par jugement LLM.

## Sources

- `docs/status.md` — le log d'itérations (table `# | Livrable | Itération | Verdict | Cause du FAIL | Corrigé | Evidence`). Source principale.
- `docs/pipeline-report.md` — optionnel : niveau de phase atteint par le dernier run `/pipeline`.

## Métriques produites

| Métrique | Définition |
|---|---|
| Taux de PASS | Livrables dont le verdict final est PASS / livrables à verdict connu |
| Itérations moy. | Moyenne du max d'itérations des livrables PASS |
| Bloqués | Livrables dont le verdict final est FAIL (3 itérations épuisées sans PASS) |
| Par phase | Répartition PASS/FAIL et itérations moyennes par phase (01-04) |
| Distribution itérations | Combien de livrables finissent en 1, 2, 3+ itérations |
| Causes de FAIL | Fréquence des causes, catégorisées par mots-clés (tests, lint, sécurité, architecture, traçabilité, spec, incomplet, bug) |

## Règles de collecte (condition nécessaire)

Les métriques ne valent que ce que vaut le log :

- **Toute** run d'une commande de boucle (`/brc`, `/elaboration`, `/construction`, `/docs`, `/transition`, `/pipeline`) **doit** ajouter une ligne au log : une avant (itération en cours), une à chaque verdict.
- La **Cause du FAIL** est obligatoire pour chaque FAIL — c'est la donnée brute qui alimente l'analyse.
- La **Catégorisation** est un mot-clé, pas un jugement : écris la cause réelle (ex. « tests unitaires manquants », « lint », « vulnérabilité SQL »), le script la classe.
- Ne jamais réécrire une ligne du log : on ajoute, on ne modifie pas l'historique.
- Les livrables se nomment de façon **stable** d'une itération à l'autre (ex. « BRC », « use case 3 », « documentation ») pour que le regroupement fonctionne.

## Lecture seule

- Le script ne modifie **jamais** `docs/status.md` ni `docs/pipeline-report.md`.
- Il régénère `docs/metrics.md` à chaque run — c'est un artefact de sortie : modifier les sources, jamais le rapport.

## Validation checklist (utilisée par le reviewer)

- [ ] Script exécuté sans erreur, sortie cohérente avec le contenu de `docs/status.md`
- [ ] Chaque livrable du log est regroupé correctement (pas de doublon de nommage)
- [ ] Verdicts finaux conformes à la dernière ligne de chaque livrable
- [ ] Phase détectée correctement pour chaque livrable
- [ ] Causes de FAIL catégorisées et causes brutes conservées dans le log
- [ ] `docs/status.md` et `docs/pipeline-report.md` non modifiés
- [ ] Rapport `docs/metrics.md` régénéré et lisible

## Loop behavior

Quand la skill est utilisée dans la boucle `/metrics` :

1. Vérifie que `docs/status.md` existe — sinon, dis qu'il faut initialiser le projet, ne génère rien.
2. Lance `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/loop-eval/loop_eval.py --project-dir .`.
3. Lis `docs/metrics.md` et le résumé stdout.
4. Exécute le skill `self-challenge` sur le rapport (cohérence, hypothèses, cas limites).
5. Propose 1-2 améliorations ciblées par les données (phase la plus faible, causes dominantes).
6. Propose une branche (`docs/loop-metrics`) et un commit Conventional Commits (`docs(metrics): ...`).
