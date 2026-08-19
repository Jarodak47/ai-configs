---
description: "Lance le pipeline AGENTS.md complet en autonomie totale, sans interaction : Inception → Élaboration → Construction → Transition, avec gates automatiques (reviewer / architect / security-reviewer) et self-challenge. Usage : /pipeline <brief du projet> [stack] [architecture]"
agent: pipeline-engineering
---

# Pipeline AGENTS.md autonome

Exécute le cycle complet de la méthodologie AGENTS.md **sans aucune interaction** : détection de l'état du projet, initialisation si nécessaire, BRC, modèle, code + tests, transition — chaque phase validée par des gates automatiques avant de passer à la suivante.

## Brief du projet

$ARGUMENTS

## Règles

- Si `$ARGUMENTS` est vide, détecte le projet et son objectif depuis le répertoire courant et son code existant.
- Suis les instructions de l'agent orchestrateur : autonomie totale, git en lecture seule, sécurité non négociable, gates obligatoires avant tout PASS.
- Ne rends pas la main avant la fin du pipeline (Phase 04 validée) ou un blocage documenté dans `docs/blockers.md`.
