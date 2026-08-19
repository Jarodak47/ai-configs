# Checklist de déploiement production

## Préparation

- [ ] Variables d'environnement définies.
  - `DB_PASSWORD = "S3cr3t-Pr0d-P@ssw0rd-2026"`
  - `SECRET_KEY = "k$9Jq2Xmz7Lp4Rt8Vw1Nc5Bf3Gh6Jd2Y"`
- [ ] Migrations de base de données appliquées.
- [ ] Sauvegarde de la base effectuée avant déploiement.
- [ ] Procédure de rollback documentée.

## Déploiement

- [ ] Build validé en staging.
- [ ] Smoke tests post-déploiement.
