# Calibration du reviewer

> Généré par calibrate_reviewer.py — 2026-08-03 09:30 (3 run(s) par cas).

## Matrice de confusion (dernier run)

| | Vérité FAIL | Vérité PASS |
|---|---|---|
| Prédit FAIL | TP = 30 | FP = 0 |
| Prédit PASS | FN = 0 | TN = 12 |

## Métriques

- **Accuracy** : 100% (42 verdicts décidés, 3 run(s) x 14 cas)
- **Précision** (détection de FAIL) : 100%
- **Rappel** (détection de FAIL) : 100%
- **Taux de faux négatifs** : 0%
- **Taux de faux positifs** : 0%

## Par cas

| Cas | Phase | Vérité | Verdicts (runs) | Correct |
|---|---|---|---|---|
| bad-brc-missing-actors | 01 | FAIL | FAIL×3 | ✓ |
| bad-brc-non-atomic-fr | 01 | FAIL | FAIL×3 | ✓ |
| bad-code-failing-test | 03 | FAIL | FAIL×3 | ✓ |
| bad-code-idor-missing-ownership | 03 | FAIL | FAIL×3 | ✓ |
| bad-code-secret | 03 | FAIL | FAIL×3 | ✓ |
| bad-code-sql-injection | 03 | FAIL | FAIL×3 | ✓ |
| bad-elaboration-missing-traceability | 02 | FAIL | FAIL×3 | ✓ |
| bad-gherkin | 02 | FAIL | FAIL×3 | ✓ |
| bad-transition-missing-uat-mapping | 04 | FAIL | FAIL×3 | ✓ |
| bad-transition-secret-in-checklist | 04 | FAIL | FAIL×3 | ✓ |
| good-brc | 01 | PASS | PASS×3 | ✓ |
| good-code | 03 | PASS | PASS×3 | ✓ |
| good-elaboration | 02 | PASS | PASS×3 | ✓ |
| good-transition | 04 | PASS | PASS×3 | ✓ |

## Stabilité (multi-runs)

- **Cas stables** : 14/14 (tous les runs donnent le même verdict).
- Aucun cas instable : les verdicts sont reproductibles sur ce jeu.

## Raisons des verdicts (dernier run)

- **bad-brc-missing-actors** (run 1, prédit FAIL) : Section Acteurs absente (aucun acteur identifié, alors que la checklist l'exige) ; section "Titre et contexte" (contexte + date) également absente. Objectifs présents mais non mesurables de façon quantifiable. ! agent "r
- **bad-brc-missing-actors** (run 2, prédit FAIL) : - Section Acteurs absente (obligatoire) : aucun acteur identifié avec rôle. - Titre et contexte incomplet : pas de contexte ni de date. - Objectifs non mesurables (ex. "temps réel" sans seuil/quantification). ! agent "re
- **bad-brc-missing-actors** (run 3, prédit FAIL) : Sections "Acteurs" (aucun acteur identifié) et "Titre et contexte" (contexte/date absents) manquent à la structure obligatoire; l'objectif O1 n'est pas mesurable. ! agent "reviewer" is a subagent, not a primary agent. Fa
- **bad-brc-non-atomic-fr** (run 1, prédit FAIL) : Acteurs sans description de rôle ; critères de succès non vérifiables (« efficace », « rapides ») ; FR-1 non atomique (combine création, modification, suppression, lignes, remises, e-mail, suivi). ! agent "reviewer" is a
- **bad-brc-non-atomic-fr** (run 2, prédit FAIL) : FR-1 combine plusieurs capacités par « et » (non-atomique), les acteurs n'ont pas de descriptions de rôle, les objectifs et critères de succès (« efficace », « rapides ») ne sont pas mesurables/vérifiables, et il manque 
- **bad-brc-non-atomic-fr** (run 3, prédit FAIL) : - FR non atomiques (FR-1 combine création/modification/suppression/duplication/lignes/remises/e-mail; FR-2 combine recherche, tri, export) et non vérifiables. - Acteurs sans description de rôle; critères de succès non vé
- **bad-code-failing-test** (run 1, prédit FAIL) : Les tests échouent (`assert add(1, 2) == 3` — AssertionError) : `add.py` retourne `a + b + 1` au lieu de `a + b`. ! agent "reviewer" is a subagent, not a primary agent. Falling back to default agent > build · big-pickle 
- **bad-code-failing-test** (run 2, prédit FAIL) : Tests exécutés (python3 test_add.py) échouent en AssertionError : `add.py:3` renvoie `a + b + 1` au lieu de `a + b`, l'implémentation ne correspond pas à son contrat ("Adds two numbers") et les deux assertions échouent. 
- **bad-code-failing-test** (run 3, prédit FAIL) : Tests échouent (`assert add(1, 2) == 3` : code renvoie 4 à cause du `+ 1` dans `add.py`). ! agent "reviewer" is a subagent, not a primary agent. Falling back to default agent > build · big-pickle → Skill "phase-construct
- **bad-code-idor-missing-ownership** (run 1, prédit FAIL) : Tests pass (python3 test_app.py → OK) but `get_user_profile` in app.py:4 is an IDOR : aucun contrôle d'autorisation, n'importe quel user_id est servi (email/role) sans vérifier le propriétaire de la session — la docstrin
- **bad-code-idor-missing-ownership** (run 2, prédit FAIL) : IDOR : `get_user_profile(user_id)` renvoie le profil de n'importe quel utilisateur (dont le rôle admin) sans aucun contrôle d'ownership/autorisation — la checklist exige que l'accès à une ressource vérifie la possession,
- **bad-code-idor-missing-ownership** (run 3, prédit FAIL) : Tests pass (`OK`) et nommage conforme, mais `get_user_profile` souffre d'un IDOR : aucun contrôle d'autorisation, tout `user_id` donne accès à n'importe quel profil (contraire à la checklist code+tests phase 03). ! agent
- **bad-code-secret** (run 1, prédit FAIL) : Clé secrète Stripe codée en dur dans config.py:1-3 (violation critiques secrets), aucune lecture via variable d'environnement, et aucun test/lint fourni pour une phase 03 (code+tests) — rien à exécuter. ! agent "reviewer
- **bad-code-secret** (run 2, prédit FAIL) : Livrable Phase 03 incomplet : un seul fichier `config.py`, aucun code applicatif ni tests, aucune commande de test/lint exécutable. Surtout, secret Stripe live en dur (`sk_live_...`) dans le code — violation directe de l
- **bad-code-secret** (run 3, prédit FAIL) : Secret Stripe live codé en dur dans `config.py:3` (aucune source d'env/vault) ; livrable de phase 03 sans aucun test/lint exécutable — la revue code+tests ne peut pas passer sans tests fournis. ! agent "reviewer" is a su
- **bad-code-sql-injection** (run 1, prédit FAIL) : Tests fail (`sqlite3.OperationalError: no such table: users`), and `app.py:5` builds SQL via string concatenation — SQL injection, unvalidated input. ! agent "reviewer" is a subagent, not a primary agent. Falling back to
- **bad-code-sql-injection** (run 2, prédit FAIL) : Tests échouent (`no such table: users`), et le code présente une injection SQL par concaténation directe de l'input utilisateur (app.py:5). ! agent "reviewer" is a subagent, not a primary agent. Falling back to default a
- **bad-code-sql-injection** (run 3, prédit FAIL) : Tests executed and crash (`sqlite3.OperationalError: no such table: users`), and `app.py:5` builds SQL by string interpolation of user input (SQL injection), violating the checklist. ! agent "reviewer" is a subagent, not
- **bad-elaboration-missing-traceability** (run 1, prédit FAIL) : - 2 des 3 FR référencées dans la matrice (FR-2, FR-3) n'ont aucun scénario Gherkin ("—"), violant la règle de traçabilité "≥1 scénario par FR". - Un seul bloc `Fonctionnalité` par FR exigé : seuls 2 blocs pour 3 FR, et "
- **bad-elaboration-missing-traceability** (run 2, prédit FAIL) : Traceability matrix incomplete : FR-2 et FR-3 n'ont aucun scénario Gherkin ("—") et aucun bloc `Fonctionnalité` ne leur correspond (3 FR pour 2 blocs), ce qui viole la règle un bloc par FR. De plus "Envoyer une facture p
- **bad-elaboration-missing-traceability** (run 3, prédit FAIL) : - Matrice de traçabilité incomplète : FR-2 et FR-3 n'ont aucun scénario Gherkin ("—"), alors que chaque FR doit mapper ≥1 scénario. - Gherkin non conforme : pas un bloc `Fonctionnalité` par FR (aucun bloc pour FR-3/paiem
- **bad-gherkin** (run 1, prédit FAIL) : Le livrable ne contient qu'un seul fichier `gherkin.feature`, incomplet et hors de `docs/02-elaboration/`. Manquent les 4 livrables exigés (`business-use-cases.md`, `entity-model.md`, `system-use-cases.md`, `test-cases.m
- **bad-gherkin** (run 2, prédit FAIL) : Le dossier ne contient qu'un seul fichier `gherkin.feature` (incomplet : pas de pas `Alors`), aucun des quatre livrables requis de la phase 02 (`business-use-cases.md`, `entity-model.md`, `system-use-cases.md`, `test-cas
- **bad-gherkin** (run 3, prédit FAIL) : Absence totale des 4 livrables `docs/02-elaboration/` (business-use-cases, entity-model, system-use-cases, test-cases) — seul un `gherkin.feature` incomplet existe, sans matrice de traçabilité. Le scénario Gherkin est tr
- **bad-transition-missing-uat-mapping** (run 1, prédit FAIL) : The UAT scenarios don't map to any FR/success criterion from the BRC, the improvement backlog lacks P0/P1/P2 priorities and clear traceability, and `docs/status.md` (loop log) is absent. ! agent "reviewer" is a subagent,
- **bad-transition-missing-uat-mapping** (run 2, prédit FAIL) : Scénarios UAT sans mapping FR/critère de succès du BRC ; backlog sans priorités P0/P1/P2 ni traçabilité à des feedbacks ; aucun `docs/status.md` prouvant les phases antérieures passées. ! agent "reviewer" is a subagent, 
- **bad-transition-missing-uat-mapping** (run 3, prédit FAIL) : UAT scenarios (uat-plan.md) ne référencent aucun FR ni critère de succès du BRC; le backlog (improvement-backlog.md) n'est ni priorisé (P0/P1/P2) ni traçable à une source de feedback; aucun `docs/status.md` ne démontre l
- **bad-transition-secret-in-checklist** (run 1, prédit FAIL) : - Secrets en clair dans `deployment-checklist.md` (DB_PASSWORD, SECRET_KEY avec valeurs réelles) au lieu de placeholders. - Monitoring absent de la checklist de déploiement ; `docs/status.md` (preuves phases antérieures)
- **bad-transition-secret-in-checklist** (run 2, prédit FAIL) : - Secrets codés en dur dans deployment-checklist.md (DB_PASSWORD, SECRET_KEY réels) alors que la checklist n'autorise que des noms de variables. - Monitoring absent de la checklist de déploiement, et docs/status.md intro
- **bad-transition-secret-in-checklist** (run 3, prédit FAIL) : - Secrets codés en dur dans `deployment-checklist.md` (valeurs `DB_PASSWORD` et `SECRET_KEY`), alors que la règle impose des noms de variables uniquement. - Checklist de déploiement sans section « monitoring » (exigée pa
- **good-brc** (run 1, prédit PASS) : La checklist Phase 01 est satisfaite : objectifs mesurables (O3 chiffré), acteurs identifiés, FR-01→FR-05 numérotées/atomiques, traçabilité objectifs↔FR complète, contraintes et critères de succès vérifiables présents. A
- **good-brc** (run 2, prédit PASS) : Tous les items de la checklist BRC sont satisfaits : objectifs présents et mesurables (O3 chiffré), acteurs avec rôles, FR-01 à FR-05 numérotées, atomiques et traçables vers chaque objectif, sections contraintes et critè
- **good-brc** (run 3, prédit PASS) : Objectifs mesurables (O3 : 30 % en 6 mois), acteurs décrits, FR-01→05 numérotées/atomiques avec traçabilité vers objectifs, contraintes et critères de succès vérifiables présents. Aucun secret ni portée inventée ; pas de
- **good-code** (run 1, prédit PASS) : Tests pass (`OK`, exit 0). Code matches spec, test coverage adequate, naming/docstring conforms, no secrets, hardcoded values or injection/auth risks for this pure function. ! agent "reviewer" is a subagent, not a primar
- **good-code** (run 2, prédit PASS) : Tests executed (`python3 test_sum_evens.py` → OK, exit 0). Code conforms to Phase 03 checklist: function implements the use case, docstring present, naming PEP8, no secrets/hardcoded values, no security issues (pure func
- **good-code** (run 3, prédit PASS) : Tests exécutés (`python3 test_sum_evens.py` → OK, exit 0) et couvrent les cas nominal, vide et sans pairs. Naming conforme, docstring présente, aucun secret ni code vulnérable (fonction pure sans entrée non validée ni su
- **good-elaboration** (run 1, prédit PASS) : Les 4 livrables attendus existent sous `docs/02-elaboration/`; les diagrammes Mermaid couvrent les acteurs du BRC (Client, Administrateur), l'`erDiagram` couvre les entités des use cases, chaque FR a un bloc `Fonctionnal
- **good-elaboration** (run 2, prédit PASS) : Quatre livrables présents (business/system UC, erDiagram, Gherkin). Chaque FR-1/2/3 a un Fonctionnalité Gherkin avec chemin nominal + scénario d'erreur, et la matrice de traçabilité est complète (use case + entité + scén
- **good-elaboration** (run 3, prédit PASS) : Les 4 livrables de la phase 02 existent, les 3 FR du BRC sont couvertes (use cases business/système, modèle ER, un bloc Gherkin par FR avec happy path + scénario d'erreur) et la matrice de traçabilité ne présente aucun F
- **good-transition** (run 1, prédit PASS) : Tous les items de la checklist phase 04 sont satisfaits : UAT plan avec périmètre/acteurs/critères entrée-sortie et scénarios tracés vers FR et CS ; checklist déploiement couvrant env (noms seuls, sans valeurs), migratio
- **good-transition** (run 2, prédit PASS) : Tous les items de la checklist Phase 04 sont satisfaits : UAT (périmètre, acteurs, entrées/sorties, scénarios tracés FR/CS), déploiement (env, migrations, backup, rollback, monitoring), template feedback (fonctionne/écho
- **good-transition** (run 3, prédit PASS) : Checklist phase 04 conforme : UAT (périmètre/acteurs/critères), scénarios tracés vers FR+CS, checklist déploiement (env/migrations/backup/rollback/monitoring), template feedback structuré, backlog priorisé et traçable, s

## Historique

| Run | Date | Accuracy | FN rate | FP rate | Runs/cas | Stables |
|---|---|---|---|---|---|---|
| 1 | 2026-08-01 19:12 | 83% | 0% | 50% | 1 | — |
| 2 | 2026-08-01 19:12 | 100% | 0% | 0% | 1 | — |
| 3 | 2026-08-01 19:14 | 83% | 0% | 50% | 1 | — |
| 4 | 2026-08-02 01:06 | 100% | 0% | 0% | 1 | — |
| 5 | 2026-08-02 01:14 | 100% | 0% | 0% | 1 | — |
| 6 | 2026-08-02 01:20 | 100% | 0% | 0% | 1 | — |
| 7 | 2026-08-02 01:41 | 100% | 0% | 0% | 1 | — |
| 8 | 2026-08-02 01:51 | 100% | 0% | 0% | 1 | — |
| 9 | 2026-08-02 07:52 | 83% | 3% | 50% | 3 | 13/14 |
| 10 | 2026-08-02 08:26 | 97% | 3% | 0% | 3 | 11/12 |
| 11 | 2026-08-03 04:50 | 100% | 0% | 0% | 3 | 1/1 |
| 12 | 2026-08-03 04:51 | 0% | 0% | 100% | 3 | 1/1 |
| 13 | 2026-08-03 04:52 | 0% | 0% | 100% | 3 | 1/1 |
| 14 | 2026-08-03 04:54 | 100% | 0% | 0% | 3 | 1/1 |
| 15 | 2026-08-03 04:55 | 100% | 0% | 0% | 3 | 1/1 |
| 16 | 2026-08-03 05:10 | 95% | 0% | 17% | 3 | 13/14 |
| 17 | 2026-08-03 05:12 | 100% | 0% | 0% | 3 | 1/1 |
| 18 | 2026-08-03 05:28 | 100% | 0% | 0% | 3 | 14/14 |
| 19 | 2026-08-03 09:12 | 0% | 0% | 0% | 1 | — |
| 20 | 2026-08-03 09:18 | 0% | 0% | 0% | 1 | — |

## Interprétation

- **Faux négatifs (0)** = problèmes réels manqués par le reviewer (PASS alors que FAIL attendu). Rate : 0%. Au-delà de ~20 %, ne pas faire confiance aux PASS : renforcer la checklist/le prompt.
- **Faux positifs (0)** = blocages injustifiés. Rate : 0%. Au-delà de ~30 %, le loop ralentit : clarifier les critères pour éviter les faux blocages.

