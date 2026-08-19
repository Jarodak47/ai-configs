# Tests Gherkin — Plateforme de facturation

```gherkin
Fonctionnalité: Créer une facture
  Afin de facturer correctement un client
  En tant que comptable
  Je veux créer une facture avec ses lignes

  Scénario: Création avec lignes valides
    Étant donné un comptable connecté
    Quand il crée une facture avec deux lignes
    Alors la facture est enregistrée avec le total calculé

  Scénario: Création avec ligne invalide
    Étant donné un comptable connecté
    Quand il crée une facture avec une ligne à prix négatif
    Alors la création est refusée avec un message d'erreur

Fonctionnalité: Envoyer une facture par e-mail
  Afin de transmettre la facture au client
  En tant que comptable
  Je veux envoyer la facture par e-mail

  Scénario: Envoi avec suivi de lecture
    Étant donné une facture validée
    Quand le comptable l'envoie par e-mail
    Alors le client reçoit la facture et le suivi de lecture est activé
```

## Matrice de traçabilité

| FR | Use case | Entité | Scénario Gherkin |
|----|----------|--------|------------------|
| FR-1 | UCB-1, U1 | INVOICE, INVOICE_LINE | Création avec lignes valides |
| FR-2 | UCB-1 | INVOICE | — |
| FR-3 | UCB-2, U3, U5 | PAYMENT | — |
