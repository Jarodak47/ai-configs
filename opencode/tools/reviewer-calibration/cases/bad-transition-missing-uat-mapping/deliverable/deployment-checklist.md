# Checklist de déploiement production

## Préparation

- [ ] Variables d'environnement définies (DB_PASSWORD, SECRET_KEY, SMTP_HOST) — valeurs en placeholders.
- [ ] Migrations de base de données appliquées.
- [ ] Sauvegarde de la base effectuée avant déploiement.
- [ ] Procédure de rollback documentée (rechargement du backup).
- [ ] Monitoring actif (logs, métriques, alertes).

## Déploiement

- [ ] Build validé en staging.
- [ ] Coupure de maintenance annoncée.
- [ ] Déploiement effectué.
- [ ] Smoke tests post-déploiement.
