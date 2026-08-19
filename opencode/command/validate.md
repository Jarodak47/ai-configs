---
description: Run the independent validation checkpoint (Business Review) on the current phase deliverables without generating anything.
agent: build
---

# Checkpoint de validation (Business Review)

Exécute la revue indépendante des livrables de la phase courante. Aucune génération : vérifie seulement et rends un verdict.

Phase à valider : $ARGUMENTS

## Comportement

1. Détermine la phase courante à partir de `docs/status.md` (ou de l'argument fourni : `01`, `02`, `03`, `04`).
2. Lance le subagent `reviewer` sur les livrables de cette phase :
   - Phase 01 : `docs/01-inception/brc.md`
   - Phase 02 : `docs/02-elaboration/`
   - Phase 03 : code + tests (le reviewer exécute réellement les tests et le lint)
   - Phase 04 : checklist UAT / déploiement
3. Affiche le verdict brut (PASS/FAIL) avec la checklist remplie.
   Valide d'abord le bloc JSON via `tools/verdict/validate_verdict.py` et vérifie
   que `reviewer` correspond à l'agent demandé. Sans cela, retourne une erreur
   d'infrastructure plutôt qu'un verdict.
4. Si FAIL : liste les problèmes par sévérité et propose le prochain run (re-génération ou correction ciblée). Ne corrige rien toi-même — le maker corrige, le checker juge.
5. Mets à jour `docs/status.md` avec le résultat (`blocked: <problèmes>` si FAIL).
