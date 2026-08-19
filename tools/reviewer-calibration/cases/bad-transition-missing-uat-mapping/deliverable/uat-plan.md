# Plan d'UAT — <Projet>

## Périmètre

- Application web de gestion de profils utilisateurs.
- Modules concernés : authentification, profils, tableau de bord.
- Environnements : staging puis production.

## Acteurs

- Utilisateur final (profil standard).
- Administrateur.
- Responsable de la validation (signe la recette).

## Scénarios

- Scénario 1 : un utilisateur se connecte avec ses identifiants et accède à son profil.
- Scénario 2 : un utilisateur modifie son adresse e-mail et vérifie la confirmation.
- Scénario 3 : un administrateur consulte la liste des utilisateurs.
- Scénario 4 : un utilisateur signale un bug via le formulaire de contact.

## Critères d'entrée

- Le code est déployé sur l'environnement de staging.
- Les comptes de test existent.

## Critères de sortie

- Les 4 scénarios ont été exécutés.
- Les défauts bloquants sont corrigés ou référés.
