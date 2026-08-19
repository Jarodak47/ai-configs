# BRC — Gestion de stock librairie

## Objectifs

- O1 : Permettre à un libraire de suivre les stocks en temps réel.
- O2 : Déclencher automatiquement une alerte de réapprovisionnement sous un seuil.
- O3 : Réduire les ruptures de stock de 30 % en 6 mois.

## Contexte

- Plateforme web de gestion de stock pour librairies indépendantes, une boutique par déploiement, accès sur poste de travail.

## Acteurs

- **Libraire** : gère le stock et les commandes de réapprovisionnement.
- **Gestionnaire** : valide les commandes et consulte les rapports.

## Exigences fonctionnelles

- FR-01 : Le système permet au libraire de créer un article (titre, auteur, ISBN, prix, quantité).
- FR-02 : Le système permet au libraire de modifier la quantité d'un article.
- FR-03 : Le système alerte le libraire quand la quantité d'un article passe sous le seuil défini.
- FR-04 : Le système permet au gestionnaire de consulter un rapport de rupture de stock.
- FR-05 : Le système enregistre l'historique des mouvements de stock.

## Correspondance objectifs ↔ exigences

- O1 → FR-01, FR-02, FR-05
- O2 → FR-03
- O3 → FR-04 (données de ruptures) + CS-02, CS-03

## Contraintes

- C-01 : PostgreSQL comme base de données.
- C-02 : API REST versionnée `/api/v1/`.
- C-03 : Authentification obligatoire sur toutes les routes.

## Critères de succès

- CS-01 : 100 % des FR couverts par des tests automatisés.
- CS-02 : Temps de réponse API < 300 ms en charge normale.
- CS-03 : Aucun secret dans le dépôt, `.env.example` fourni.

## Traçabilité

- FR-01 à FR-05 → use cases Phase 02 ; chaque FR liée à un scénario Gherkin.
