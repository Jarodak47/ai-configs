---
description: Meta-loop. Analyze the iteration log in docs/status.md, find recurring FAIL causes, and propose targeted improvements to AGENTS.md, skills, commands, or the reviewer. Does not modify anything without approval.
agent: build
---

# Rétrospective du loop engineering

Analyse le log d'itérations de `docs/status.md` pour améliorer la boucle elle-même. C'est l'étape "Repeat" qui nourrit le système : aucune génération, uniquement diagnostic + propositions.

Champ optionnel : $ARGUMENTS (ex. `seulement phase 02`, `causes Gherkin`)

## Étapes

1. Lis `docs/status.md` (log d'itérations), le dernier état `done / next / blocked`, **`docs/loop-trace.md` et `.loop-trace/*.jsonl`** (trace du loop).
2. Analyse la trace au niveau itération — table trace-level :
   | Itération | Livrable | Verdict | Durée | Coût |
   Compare latence et coût des itérations **FAIL vs PASS** : une itération FAIL coûte en moyenne combien de fois une PASS ? Repère les itérations anormalement longues ou coûteuses (dérive d'effort sur un livrable).
3. Agrège le log par livrable et par cause de FAIL. Construis la table de fréquence :
   | Cause de FAIL | Occurrences | Livrables concernés | Correctifs déjà tentés |
4. Identifie les 3 causes les plus fréquentes. Pour chacune, détermine la racine :
   - Le skill est-il incomplet ou ambigu ?
   - La commande omet-elle une étape ?
   - Le reviewer est-il trop laxiste / trop strict / sans evidence ?
   - Le livrable manquait-il de précondition (phase précédente non validée) ?
   - La trace montre-t-elle un coût/latence anormal sur une itération précise ?
5. Pour chaque racine, propose un correctif CIBLÉ et minimal (une ligne de skill, une étape de commande, un item de checklist reviewer...). Rien de global.
6. **Suivi des actions passées** : vérifie le statut des propositions des rétrospectives précédentes (appliquée ? effet mesuré ?). Une proposition validée mais jamais appliquée est elle-même une cause de boucle.
7. Affiche la table de fréquence + les propositions. Classe-les par impact (fort/moyen/faible).
8. **N'applique rien toi-même** : demande mon approbation, proposition par proposition.
9. Si aucune cause récurrente : affiche le constat "boucle saine" et les métriques (nombre d'itérations moyennes, taux de PASS au premier run, latence/coût moyens par phase).

## Règles

- Ne modifie aucun fichier sans approbation explicite.
- Une cause isolée (1 occurrence) n'est PAS une amélioration de boucle : ignore-la, sauf si elle bloque une phase.
- Propose des correctifs mesurables : "ajouter X à la checklist" plutôt que "améliorer la qualité".
- Chaque proposition d'action porte un `[Owner]` et une `[Date]` cible, et est ajoutée au suivi de la rétro suivante.
