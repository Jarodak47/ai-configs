---
name: security-scan
description: Deterministic, reproducible security scanning that complements the security-reviewer LLM — scans git-tracked files for committed secrets and tracked .env files (without ever reading their contents), and runs dependency vulnerability scanners (pip-audit, npm audit, composer audit) stack-aware. Use in any security gate, before/after security fixes, or via /security-scan.
---

# Skill : security-scan

Scan de sécurité **déterministe et reproductible** qui complète le `security-reviewer` (LLM) par des contrôles que l'on peut re-exécuter sans variabilité.

## Quand utiliser

- Avant/dans toute gate de sécurité (commande `/construction`, agent `pipeline-engineering` Phase 03).
- À la demande via `/security-scan`.
- Avant tout livrable qui touche auth, input, données ou secrets.

## Contenu

| Élément | Emplacement |
|---|---|
| Script | `${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/security-scan/security_scan.py` |
| Commande | `/security-scan` |

## Comportement du script

1. **Secrets commits** : scanne les fichiers **traqués par git** (via `git ls-files`, donc respecte `.gitignore`) pour des patterns connus (clés AWS, Stripe, GitHub PAT, Slack, clés privées, secrets génériques en dur). Les fichiers `.env` ne sont **jamais lus** — seulement leur présence en tracking est signalée.
2. **Vulnérabilités de dépendances** : détecte le manifest selon le stack et lance le scanner dispo :
   - Python (`requirements.txt`/`pyproject.toml`/`Pipfile`) → `pip-audit`
   - Node (`package-lock.json`) → `npm audit --omit=dev`
   - PHP (`composer.lock`) → `composer audit`
   - Scanner absent → noté, **non bloquant** (limitation connue).

## Codes de sortie (gates)

| Code | Sens | Action gate |
|---|---|---|
| `2` | CRITIQUE (secret, `.env` traqué, vulnérabilité critique/haute) | **Bloque** — corriger avant de continuer |
| `1` | MOYEN (findings medium/low) | Signaler, traiter si raisonnable |
| `0` | Rien | PASS |

## Règles

- Un secret commité se corrige en deux temps : le retirer du fichier **et** purger l'historique git (le simple commit suivant ne retire pas le secret de l'historique).
- Ne jamais lire/afficher le contenu d'un `.env` ; ne signaler que sa présence.
- Le rapport produit (`docs/03-construction/security-scan.md`) est l'**evidence** à citer dans le verdict de gate.

## Check-list du scan

- [ ] Le script a tourné (`security_scan.py`) sans erreur.
- [ ] Exit `2` → corrigé et re-scané jusqu'à `0` ou `1`.
- [ ] Rapport `docs/03-construction/security-scan.md` présent et à jour.
- [ ] Findings moyens signalés au développeur.
