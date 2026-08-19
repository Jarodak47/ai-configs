---
description: "Boucle de génération de documentation du code via la skill docs-code : détection de la cible (Backstage TechDocs / mkdocs / Markdown+docstrings), génération, self-challenge, gate reviewer, itération jusqu'à PASS. Usage : /docs [cible: backstage|mkdocs|md]"
agent: build
---

# Boucle Documentation du code — docs-code

Génère ou met à jour la documentation du code du projet avec le skill `docs-code`, validée par un vérifieur indépendant.

Cible (optionnel) : $ARGUMENTS

## Préconditions

- Code en place (Phase 03 avancée ou terminée). Si aucun code n'existe, le dire et ne pas générer de fausse documentation.
- `docs/status.md` présent — sinon copier le modèle `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/templates/status.md`.

## Étapes (goal loop)

1. Charge le skill `docs-code`.
2. Décide de la cible : si `$ARGUMENTS` précise une cible (backstage, mkdocs, md...), elle prime. Sinon, **demande à l'utilisateur** le périmètre souhaité (offre les options : Backstage TechDocs / mkdocs / Markdown+docstrings) avant de générer — la décision autonome n'existe que dans le pipeline automatique sans interaction.
3. Lis `docs/status.md` ; écris l'état (`next: générer documentation`) et ajoute la ligne d'itération 1 au log.
4. Génère les livrables de la cible détectée (README, docstrings, OpenAPI, mkdocs, catalog-info.yaml + mkdocs.yml TechDocs...).
5. Exécute le skill `self-challenge` sur les docs générées.
6. Lance le subagent `reviewer` avec la checklist de validation du skill (il vérifie `mkdocs build` s'il y a un `mkdocs.yml`).
7. Si FAIL : corrige les problèmes signalés et relance le reviewer. Maximum 3 itérations — au-delà, arrête et expose les blocages. À chaque verdict, ajoute une ligne au log de `docs/status.md` (itération, verdict, cause du FAIL obligatoire).
8. Au PASS : mets à jour `docs/status.md` (`done: documentation générée` / `next: <prochaine étape du projet>`).
9. Résume le résultat et propose une branche (`docs/<scope>-<description>`) + un commit Conventional Commits (`docs(<scope>): ...`).

Ne rends pas la main avant le verdict PASS ou les 3 itérations épuisées.
