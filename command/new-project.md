---
description: "Initialize a new project following the AGENTS.md methodology: create docs/01-04 structure, .gitignore, AGENTS.md symlink, and the status.md loop log from the template."
agent: build
---

# Initialisation d'un nouveau projet

Prépare la structure du projet selon AGENTS.md (Project Initialization) et initialise le log du loop engineering. Aucun code de fonctionnalité n'est généré.

Projet : $ARGUMENTS

## Étapes

1. Confirme que tu es à la racine du nouveau projet (pas un dossier existant). Si `$ARGUMENTS` est vide, demande le chemin.
2. Vérifie qu'il ne s'agit pas d'un projet legacy déjà en production — si oui, applique la Legacy Projects Policy (adoption minimale, pas de refonte).
3. Exécute le script d'initialisation d'AGENTS.md :

   ```bash
   mkdir -p docs/01-inception \
            docs/02-elaboration \
            docs/03-construction \
            docs/04-transition

   touch .gitignore
   while IFS= read -r entry; do
     grep -qxF -- "$entry" .gitignore || echo "$entry" >> .gitignore
   done << 'GITIGNORE'
   .env
   *.env
   build/
   dist/
   __pycache__/
   node_modules/
   *.log
   GITIGNORE

   AGENTS_SRC="$HOME/AGENTS.md"
   if [ ! -e ./AGENTS.md ] && [ ! -L ./AGENTS.md ]; then
     ln -s "$AGENTS_SRC" ./AGENTS.md
   fi
   ```

4. Résous `OPENCODE_CONFIG_DIR` (défaut : `$HOME/.config/opencode`), puis copie
   `templates/status.md` vers `docs/status.md` et
   `templates/dependency-graph.json` vers `docs/dependency-graph.json` uniquement
   si ces fichiers n'existent pas. Remplis le titre du statut avec le nom du projet.
5. Demande la confirmation du stack (Python/Django/FastAPI, JS/TS/React/Next.js/Angular, Java/Spring Boot, PHP, C...) et de l'architecture (Monolithic, Microservices, Hexagonal, Clean, MVC, Layered, Event-Driven, CQRS...) AVANT toute génération de code.
6. Résume la structure créée et propose le point de départ : Phase 01 — Inception via `/brc`.

## Règles

- N'exécute le script que si les répertoires n'existent pas déjà (idempotent).
- Ne génère aucune spécification ni code ici — uniquement la structure.
- Si le projet est déjà initialisé (docs/ et AGENTS.md présents), le dis et passe directement à la question stack/architecture.
