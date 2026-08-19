# Plan d'UAT — Gestion des réservations

## Périmètre
Réservation de salles, annulation, administration.

## Acteurs
Client, administrateur.

## Scénarios (traçés vers les FR et critères de succès)

| Scénario | FR | Critère de succès |
|---|---|---|
| Réserver une salle libre | FR-1 | CS-1 : réservation confirmée en moins de 2 s |
| Réservation refusée sur conflit | FR-1 | CS-1 : message de conflit clair |
| Annuler avant le délai | FR-2 | CS-2 : salle libérée immédiatement |
| Créer une salle | FR-3 | CS-3 : salle disponible à la réservation |

## Critères d'entrée / de sortie
- Entrée : staging déployé, comptes de test, jeux de données.
- Sortie : tous les scénarios exécutés, défauts bloquants référés ou corrigés.
