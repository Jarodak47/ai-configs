---
name: docs-code
description: Génère et maintient la documentation du code des projets AGENTS.md — README/Markdown, docstrings par stack (Python/Google, JSDoc/TSDoc, Javadoc, PHPDoc), API OpenAPI, sites mkdocs (Material) et Backstage TechDocs (catalog-info.yaml + plugin techdocs-core). Use when the user asks to document code, write a README, generate docs, documentation, mkdocs, Backstage, TechDocs, or "documente le code".
---

# Documentation du code — docs-code

Use this skill whenever code documentation must be written or updated: README, docstrings, API docs, mkdocs sites, or Backstage TechDocs. It applies to new code produced in Phase 03 and to documentation requests.

## Cible et détection automatique

Détecte la ou les cibles dans cet ordre, sans demander :

1. **Backstage TechDocs** — si un `catalog-info.yaml` existe à la racine, ou si la cible est demandée explicitement (Backstage, TechDocs, developer portal).
2. **mkdocs** — si le projet est Python, si `mkdocs.yml` existe, ou si un site de documentation est demandé.
3. **Markdown + docstrings** — toujours : README, docstrings, API docs, docs d'architecture.

On peut produire plusieurs cibles (ex. README + mkdocs), mais jamais de duplication entre elles.

## Décision du périmètre selon le type et la grandeur du projet

L'agent décide **seul** du type et du volume de documentation, selon le **type de projet** et sa **grandeur** — jamais de sur-documentation, jamais de sous-documentation. Cette décision fait partie du livrable et doit être justifiée.

**Priorité :** si l'utilisateur **précise** une cible ou un périmètre (dans le brief, `$ARGUMENTS`, ou en cours de session), **c'est cette spécification qui prime** — l'agent s'y conforme et ne re-décide pas. Si rien n'est spécifié :

- **Contexte interactif** (commande `/docs`, session normale où l'utilisateur peut répondre) → **demande-lui** la cible/le périmètre avant de générer.
- **Workflow manuel de construction** (`/construction`) → la demande de portée se fait **en amont**, une seule fois avant le premier use case ; ensuite la doc suit chaque use case au fil de l'eau, sans re-demander.
- **Contexte autonome** (pipeline automatique `/pipeline`, zéro interaction) → la décision autonome selon le type et la grandeur ci-dessous s'applique.

| Grandeur | Type de projet | Documentation recommandée |
|---|---|---|
| Petite — prototype / POC / outil jetable (< 2 semaines) | Tout type | README seul (description, install, usage, tests). Pas de mkdocs ni Backstage. |
| Moyenne — app en développement actif, équipe 1-5 | API / web service | README + API OpenAPI + docstrings. mkdocs si la doc utilisateur devient non triviale. |
| Moyenne — équipe 1-5 | Fullstack / SPA / frontend | README + docstrings front & back. mkdocs optionnel (plusieurs consommateurs). |
| Grande — entreprise, plusieurs équipes, production | Microservices / plateforme | Backstage TechDocs (catalog-info.yaml par service + mkdocs techdocs-core) + README + OpenAPI. |
| Grande | Bibliothèque / SDK | README + référence API complète + changelog. mkdocs si docs utilisateurs importantes. |
| Toute taille | CLI / scripts / outils internes | README + `--help`/man + docstrings des fonctions publiques. |
| Toute taille | Pipeline data / ETL | README + schéma d'architecture + params/CLI documentés. mkdocs si orchestré/partagé. |

Règles :

- **Grandeur** : juge sur le nombre d'équipes/consommateurs, la durée de vie prévue, la criticité (production) et la complexité.
- Un **POC n'a pas de Backstage** ; un service en **production sans `catalog-info.yaml` est un manque** — l'ajouter.
- En cas de doute, choisis le niveau minimal correct et justifie — un README excellent vaut mieux qu'un mkdocs vide.
- Le choix de périmètre est annoncé dans le résumé final et vérifié dans la checklist.

## Livrables

### 1. README / Markdown générique

Structure minimale d'un README :

- **Nom + description courte** (1 phrase)
- **Prérequis** et **installation** (commandes réelles, pas de pseudo-code)
- **Usage** : exemple minimal qui tourne (input → output)
- **Structure du projet** : arborescence des dossiers clés avec 1 ligne chacun
- **Variables d'environnement** : citées **par nom uniquement** (ex. `DB_PASSWORD`), jamais de valeurs, avec renvoi à `.env.example`
- **Tests** : commande pour lancer les tests et le lint
- **Licence** (si présente dans le dépôt)

Autres docs Markdown : `docs/architecture.md` (vue d'ensemble, patterns, décisions), `docs/api.md` (endpoints, exemples requête/réponse).

### 2. Docstrings et commentaires par stack

- **Python** → style Google (Sections `Args:` / `Returns:` / `Raises:`)
- **TypeScript / JavaScript** → TSDoc / JSDoc (`@param` / `@returns`)
- **Java / Kotlin** → Javadoc / KDoc
- **PHP** → PHPDoc
- **C** → commentaires `/** ... */`

Règles :

- Documente l'**API publique** : modules, classes, méthodes et fonctions exposées — pas les implémentations triviales internes.
- Le commentaire explique le **pourquoi** (logique non évidente), jamais le *quoi* (règle AGENTS.md).
- Un commentaire qui répète le code est du bruit — supprime-le.
- Les fonctions d'action suivent la convention AGENTS.md (verbe initial) et les booleans `is/has/can/should`.

### 3. API (OpenAPI pour REST)

- Contrat exposé au client : description, types, statuts d'erreur, exemples requête/réponse.
- Jamais de détails internes (stack traces, requêtes SQL) dans les docs exposées.
- Versionnage dès le départ : `/api/v1/...`.

### 4. mkdocs

- `mkdocs.yml` à la racine avec `site_name`, `theme: material` et `nav` (accueil + pages).
- Contenu dans `docs/` (fichiers `kebab-case.md`), `docs/index.md` = page d'accueil.
- Pas de duplication avec le README : l'index peut reprendre/citer le README, pas le copier.
- Vérifiable par `mkdocs build` sans erreur.

```yaml
site_name: Mon Service
site_description: Description courte
theme:
  name: material
nav:
  - Accueil: index.md
  - Guide: guide.md
  - API: api.md
```

### 5. Backstage TechDocs

Backstage est un developer portal ; TechDocs rend un site **mkdocs**. Deux fichiers sont nécessaires à la racine :

- `catalog-info.yaml` — entité du catalogue (kind `Component`) :

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: mon-service
  description: Description courte
  annotations:
    backstage.io/techdocs-ref: dir:.
    github.com/project-slug: org/mon-service
spec:
  type: service
  lifecycle: production
  owner: team-backend
```

- `mkdocs.yml` avec le plugin `techdocs-core` :

```yaml
site_name: Mon Service
plugins:
  - techdocs-core
```

Règles TechDocs :

- `backstage.io/techdocs-ref` pointe vers la source des docs : `dir:.` (dépôt courant) ou `url:<href>` pour un dépôt distant.
- `github.com/project-slug` est requis pour la vue "repo" (owner/name).
- `spec.owner` et `spec.lifecycle` obligatoires dans le catalogue.
- Le générateur TechDocs est mkdocs : sans `docs/` + `mkdocs.yml`, pas de TechDocs.
- `techdocs-core` est le seul plugin requis ; ne le duplique pas avec Material.

## Règles transverses

- **Synchronisation** : toute doc générée doit refléter le code réel (commandes, signatures, endpoints). Une doc périmée est pire qu'aucune.
- **Sécurité** : jamais de secrets, valeurs, tokens ou URLs internes. Variables citées par nom, placeholders dans les exemples, renvoi à `.env.example`.
- **Conventions de nommage AGENTS.md** : fichiers `kebab-case.md`, noms explicites, pas d'abréviations inconnues.
- **Traçabilité** : si la doc documente une fonctionnalité, lie-la au use case et aux FR concernés.
- **Décisions d'architecture** : toute décision (stack, pattern, choix) est documentée dans `docs/03-construction/decisions.md` — pas seulement dans un commentaire.

## Validation checklist (utilisée par le reviewer)

- [ ] Cible détectée correctement (Backstage / mkdocs / Markdown) et justifiée
- [ ] Périmètre documentaire proportionné au type et à la grandeur du projet (pas de sur/sous-documentation), choix justifié
- [ ] README couvre : description, prérequis/installation, usage, structure, env vars (par nom), tests, licence
- [ ] Docstrings suivent la convention du stack et couvrent l'API publique
- [ ] Commentaires expliquent le *pourquoi*, pas le *quoi*
- [ ] Aucun secret / valeur réelle ; placeholders et `.env.example` référencé
- [ ] `mkdocs.yml` valide (site_name, nav, theme) et `mkdocs build` passe (si cible mkdocs)
- [ ] Backstage : `catalog-info.yaml` YAML valide, annotations `techdocs-ref` + `project-slug`, `owner`/`lifecycle` définis ; `mkdocs.yml` contient `techdocs-core`
- [ ] Pas de duplication README ↔ mkdocs
- [ ] Conventions de nommage respectées
- [ ] Traçabilité use case → FR → doc (si doc de fonctionnalité)

## Loop behavior

Quand la skill est utilisée dans une boucle (commande `/docs`) :

1. Lis `docs/status.md` ; ajoute la ligne d'itération 1 au log.
2. Détecte la cible et génère les livrables de cette section.
3. Exécute le skill `self-challenge` sur les docs (hypothèses, cas limites, traçabilité, sécurité).
4. Lance le subagent `reviewer` avec la checklist de validation ci-dessus.
5. Si FAIL : corrige précisément et relance. Maximum 3 itérations — au-delà, expose les blocages.
6. Au PASS : mets à jour `docs/status.md` et propose une branche + un commit Conventional Commits (`docs(<scope>): ...`).
