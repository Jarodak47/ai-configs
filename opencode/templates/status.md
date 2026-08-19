# Status — <Nom du projet>

> Modèle de `docs/status.md` pour le loop engineering. Copié par `/new-project`, mis à jour par chaque commande de phase (`/brc`, `/elaboration`, `/construction`, `/transition`, `/retrospective`).

## État courant

- **Phase** : 01 Inception
- **done** : <dernier livrable validé>
- **next** : <prochain livrable>
- **blocked** : <bloquants éventuels, sinon "—">
- **waiting** : <livrables en attente de dépendances, sinon "—">
- **skipped** : <livrables non exécutables car une dépendance est bloquée, sinon "—">

Le graphe machine-readable correspondant vit dans `docs/dependency-graph.json`.

## Log d'itérations

| # | Livrable | Itération | Verdict | Cause du FAIL | Corrigé | Evidence |
|---|----------|-----------|---------|---------------|---------|----------|
| 1 | BRC | 1 | FAIL | <cause> | oui | <sortie reviewer / checklist> |
| 2 | BRC | 2 | PASS | — | — | <sortie reviewer / checklist> |

## Règles de mise à jour

1. Chaque run de commande ajoute une ligne au log **avant** (itération en cours) et **après** (verdict final).
2. Le champ **Cause du FAIL** est obligatoire pour chaque FAIL — c'est la donnée brute qui alimente `/retrospective`.
3. Le champ **Evidence** est obligatoire : cite la preuve du verdict (sortie tests/lint, `docs/03-construction/security-scan.md` pour la gate sécurité, verdict reviewer/architect). Un verdict sans evidence n'est pas un verdict.
4. Ne jamais réécrire une ligne : on ajoute, on ne modifie pas l'historique.
5. `done` / `next` / `blocked` / `waiting` / `skipped` reflètent le dernier état validé uniquement.
6. Un PASS sans cause de FAIL antérieure est noté `—`.
7. Après tout changement d'état, exécuter `dependency_gate.py` : seules les
   entrées `runnable` peuvent avancer. Une entrée `dependency_blocked` est
   marquée `skipped` jusqu'à résolution du blocage amont.
