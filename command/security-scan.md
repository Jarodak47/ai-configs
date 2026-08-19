---
description: Exécute le scan de sécurité déterministe (secrets commits, .env traqués, vulnérabilités de dépendances) et écrit le rapport dans docs/03-construction/security-scan.md. Complète le security-reviewer par des contrôles reproductibles.
---
# Commande /security-scan

Exécute le scan de sécurité déterministe sur le projet courant.

## Déroulement

1. Exécute :
   `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/security-scan/security_scan.py`
   depuis la racine du projet.

2. Interprète le code de sortie :
   - `2` (CRITIQUE) : secret commité, `.env` traqué, ou vulnérabilité critique/haute. **La gate bloque** — corrige immédiatement :
     - secret commité → retire le secret du fichier, purge l'historique git (filter-repo) si déjà poussé,
     - `.env` traqué → `git rm --cached .env`, ajoute `.env` au `.gitignore`,
     - vulnérabilité dépendance → upgrade/mise à jour de version.
     - Applique le skill `security-hardening` si tu corriges du code.
     - Re-lance le scan jusqu'à exit `0` ou `1`.
   - `1` (MOYEN) : findings medium/low → signale-les au développeur, traite-les si raisonnable, ne bloque pas.
   - `0` : propre.
3. Le rapport est écrit dans `docs/03-construction/security-scan.md`. Mentionne-le dans ta réponse.

## Sortie JSON

Pour un résumé consommable par d'autres étapes :

`python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/security-scan/security_scan.py --json`
