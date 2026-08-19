# Business Use Cases — Plateforme de facturation

```mermaid
flowchart LR
    C[Comptable] -->|Crée/édite une facture| UCF1[(Gestion des factures)]
    Cl[Client] -->|Consulte et paie| UCF2[(Suivi des paiements)]
    A[Administrateur] -->|Gère les comptes| UCF3[(Administration)]
```

## Use cases business

- **UCB-1** : Le comptable crée, modifie et supprime des factures.
- **UCB-2** : Le client consulte ses factures et effectue un paiement.
- **UCB-3** : L'administrateur gère les comptes utilisateurs.
