# Plan d'UAT

## Périmètre
Gestion des factures (création, envoi, suivi des paiements).

## Acteurs
Comptable, client, administrateur.

## Scénarios (traçés vers les FR)

| Scénario | FR | Critère de succès |
|---|---|---|
| Créer une facture avec lignes | FR-1 | La facture est créée et le total calculé (CS-1) |
| Envoyer une facture par e-mail | FR-1 | Le client reçoit la facture (CS-2) |
| Encaisser un paiement | FR-3 | Le statut passe à « payée » (CS-3) |

## Critères d'entrée / de sortie
- Entrée : staging déployé, comptes de test.
- Sortie : tous les scénarios exécutés, défauts bloquants référés.
