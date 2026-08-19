# BRC — Gestion de stock librairie

## Objectifs

- O1 : Permettre à un libraire de suivre les stocks en temps réel.
- O2 : Déclencher automatiquement une alerte de réapprovisionnement sous un seuil.

## Exigences fonctionnelles

- FR-01 : Le système permet de créer un article (titre, auteur, ISBN, prix, quantité).
- FR-02 : Le système permet de modifier la quantité d'un article.
- FR-03 : Le système alerte quand la quantité d'un article passe sous le seuil défini.

## Contraintes

- C-01 : PostgreSQL comme base de données.
- C-02 : API REST versionnée `/api/v1/`.

## Critères de succès

- CS-01 : 100 % des FR couverts par des tests automatisés.
