# Checklist de déploiement production

## Préparation
- [ ] Variables d'environnement définies — valeurs en placeholders uniquement :
  - `DB_PASSWORD`, `SECRET_KEY`, `SMTP_HOST` (référencées par nom, jamais par valeur)
- [ ] Migrations de base de données appliquées.
- [ ] Sauvegarde de la base effectuée avant déploiement.
- [ ] Procédure de rollback documentée (restauration du backup).
- [ ] Monitoring actif (logs, métriques, alertes).

## Déploiement
- [ ] Build validé en staging.
- [ ] Déploiement effectué.
- [ ] Smoke tests post-déploiement.
