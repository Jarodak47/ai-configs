# Business Requirements Catalog — Gestion des réservations

## Objectifs
- **O1** : Permettre aux clients de réserver une salle en ligne en moins de 2 minutes.
- **O2** : Réduire les conflits de réservation à zéro.
- **O3** : Permettre à l'administrateur de gérer le parc de salles.

## Acteurs
- **Client** : réserve et annule ses réservations.
- **Administrateur** : gère les salles (création, désactivation).

## Exigences fonctionnelles
- **FR-1** : Le système permet à un client de réserver une salle libre sur une plage horaire.
- **FR-2** : Le système permet à un client d'annuler sa propre réservation jusqu'à 24 h avant le début.
- **FR-3** : Le système permet à un administrateur de créer une salle avec une capacité positive.

## Contraintes
- Application web responsive.
- Les réservations ne peuvent pas se chevaucher sur une même salle.

## Critères de succès
- **CS-1** : Une réservation est confirmée en moins de 2 secondes (O1).
- **CS-2** : Aucun conflit de réservation enregistré sur 30 jours (O2).
- **CS-3** : Une salle créée est disponible à la réservation immédiatement (O3).
