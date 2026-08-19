---
description: "Calibre les agents de gate sur des cas de référence à vérité connue : reviewer fonctionnel, architecte, security reviewer et design reviewer. Rejette tout fallback d'agent. Usage : /calibrate [reviewer|architect|security-reviewer|design-reviewer|all]"
agent: build
---

# Boucle Calibration du reviewer

Mesure la fiabilité du reviewer de ce workflow avec la skill `reviewer-calibration`.

## Étapes (goal loop)

1. Charge le skill `reviewer-calibration`.
2. Pour le reviewer fonctionnel, exécute `calibrate_reviewer.py --agent calibration-runner --runs 3`.
   Ajoute `--model <juge>` dès qu'un second modèle est disponible — la run est alors marquée `cross-model`.
   Sans `--model`, la run est acceptée mais le rapport signale `same-model` (P2.8 : limitation mesurée, coût nul, pas de pinning GPT).
3. Pour `architect`, `security-reviewer` et `design-reviewer`, exécute
   `agent-evaluation/evaluate_agents.py --runs 3` (ou `--agent <nom>`).
4. **Diversité du modèle juge (P2.8)** : le juge (modèle qui révise) doit être
   différent du worker (modèle qui a produit les livrables). Le script mesure et
   fige cette propriété dans le rapport : `independence: cross-model` si `--model`
   a été fourni, `same-model` sinon (documenté comme limitation, coût nul).
   Si l'accuracy d'une run `cross-model` s'écarte du baseline de **≥ 5 points**,
   suspecte un biais de modèle : documente-le dans
   `tools/reviewer-calibration/report.md` et évalue un second modèle juge avant
   de conclure. Le pinning `model:` par agent reste le chemin d'activation quand
   un second modèle sera disponible (ne pas utiliser GPT par défaut : coût).
5. Tout fallback, verdict JSON invalide ou agent incorrect est une erreur
   d'infrastructure et ne compte jamais comme une prédiction. Un run sans aucun
   verdict exploitable retourne le code 2, conserve le dernier baseline valide
   et écrit `infrastructure-error-report.md`.
6. Lis les rapports et résultats : matrice de confusion, accuracy, FN/FP,
   stabilité et erreurs d'infrastructure.
7. Exécute le skill `self-challenge` sur les rapports.
8. Interprète selon les seuils du skill :
   - **FN rate > 20 %** → des problèmes réels passent : propose de renforcer la checklist de la phase concernée ou le prompt du reviewer, et de re-calibrer après correction.
   - **FP rate > 30 %** → des blocages injustifiés ralentissent le loop : propose de clarifier les critères (le reviewer ne doit pas inventer de sections hors checklist).
   - **Stochasticité** : si un seul run et un cas limite, recommande de relancer ≥ 3 fois avant de conclure.
9. Si un faux négatif précis est identifié : propose une correction ciblée et
   fais re-calibrer — ne modifie jamais la vérité pour faire passer l'agent.
10. Le pipeline autonome est évalué par les tests contractuels déterministes de
   `/self-test` (DAG, blocages, limite d'itérations, gates), et non par une
   matrice PASS/FAIL artificielle.

Ne modifie pas le reviewer (prompt/checklists) sans proposition validée : c'est une décision qui impacte toutes les gates.
