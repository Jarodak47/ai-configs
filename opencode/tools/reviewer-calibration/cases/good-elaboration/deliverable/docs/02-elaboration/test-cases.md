# Tests Gherkin

```gherkin
Fonctionnalité: Réserver une salle
  Afin de garantir la disponibilité d'une salle
  En tant que client
  Je veux réserver une salle pour une plage horaire

  Scénario: Réservation réussie sur salle libre
    Étant donné une salle libre sur la plage demandée
    Quand le client réserve la salle
    Alors la réservation est enregistrée

  Scénario: Réservation refusée sur salle déjà occupée
    Étant donné une réservation existante sur cette plage
    Quand le client réserve la même salle
    Alors la réservation est refusée avec un message de conflit

Fonctionnalité: Annuler une réservation
  Afin de libérer une salle
  En tant que client
  Je veux annuler ma réservation

  Scénario: Annulation avant le délai
    Étant donné une réservation à plus de 24 h
    Quand le client annule la réservation
    Alors la salle redevient disponible et la réservation est clôturée

  Scénario: Annulation refusée après le délai
    Étant donné une réservation commençant dans moins de 24 h
    Quand le client tente d'annuler la réservation
    Alors l'annulation est refusée avec un message de délai dépassé

Fonctionnalité: Créer une salle
  Afin d'étendre l'offre
  En tant qu'administrateur
  Je veux créer une nouvelle salle

  Scénario: Création avec capacité valide
    Étant donné un administrateur connecté
    Quand il crée une salle avec une capacité positive
    Alors la salle est disponible pour les réservations

  Scénario: Création refusée avec capacité invalide
    Étant donné un administrateur connecté
    Quand il crée une salle avec une capacité nulle ou négative
    Alors la création est refusée avec un message d'erreur
```

## Matrice de traçabilité

| FR | Use case | Entité | Scénario Gherkin |
|----|----------|--------|------------------|
| FR-1 | UCB-1, U1 | RESERVATION, SALLE | Réservation réussie / refusée |
| FR-2 | UCB-1, U2 | RESERVATION | Annulation avant le délai / refusée après le délai |
| FR-3 | UCB-2, U3 | SALLE | Création avec capacité valide / refusée capacité invalide |
