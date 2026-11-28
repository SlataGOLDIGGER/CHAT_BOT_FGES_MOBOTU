# MOBOTU-100 — Retour d'expérience individuel P4

## 1. Contexte et rôle

Rôle P4 dans le projet NLP A3-B1 (recherche sémantique en corpus fermé + assistant réglementaire sourcé). Domaine principal : jeu de questions, protocole et banc d'évaluation, test scellé. Domaine secondaire : relecture du corpus, chaîne locale du volet B. Détenteur unique du test scellé (MOBOTU-44, 16/11/2026) et propriétaire du dépôt GitHub.

Jalons tenus : environnement de poste consigné (MOBOTU-25, 14/10), chaîne locale B1 figée (MOBOTU-19, 12/10), première génération locale documentée (MOBOTU-30, 19/10), familles de questions réparties (MOBOTU-39, 14/10), banc d'évaluation B1 construit (MOBOTU-61, 14/11), go/no-go de l'encodeur affiné tranché (MOBOTU-53, 21/11).

## 2. Difficultés techniques rencontrées

- **Contamination des familles de questions (D14, 15/11/2026)** : le tirage déterministe séparait des règles identiques ou quasi identiques entre entraînement, développement et test, sans que le validateur le détecte. Correction ciblée : regroupement des textes identiques et des trois quasi-doublons vérifiés, réécriture de 32 lignes train/dev, réécriture hors dépôt des questions de test touchées. Conséquence directe : les mesures de développement obtenues avec l'ancien partage ne sont plus comparables aux nouvelles.
- **Encodage et fin de ligne de `docs/decisions.md`** : fichier en Latin-1/CP1252 (non UTF-8) et en LF pur malgré des CRLF comptés ailleurs — cause d'un échec silencieux lors de l'insertion de la décision D12, corrigé par une conversion d'encodage avant insertion.
- **Go/no-go de l'encodeur affiné (D12, 21/11)** : décision NO-GO malgré un écart de nDCG@10 favorable (+0,080), parce que la borne basse de l'intervalle de confiance passe sous zéro (−0,013) et que le cosinus minimal du modèle affiné (0,9768) reste sous le seuil D3 (0,99). Décision tranchée malgré la tentation de garder le modèle affiné sur le seul critère de score moyen.

## 3. Apprentissages

- Un validateur qui ne contrôle que l'appartenance d'identifiants de section peut laisser passer une contamination sémantique : la robustesse d'un jeu de test scellé dépend autant du protocole de tirage que du contrôle a posteriori.
- Un écart de performance favorable ne suffit pas à une décision de mise en production : la largeur de l'intervalle de confiance et un deuxième critère indépendant (cosinus minimal navigateur/index) peuvent, à eux seuls, renverser une décision.
- Les problèmes d'encodage de fichiers texte (Latin-1 vs UTF-8, CRLF vs LF) restent une source d'échecs silencieux qu'un simple diff Git ne révèle pas toujours.

## 4. Collaboration d'équipe

Relecteur attitré : P1 (binôme de relecture). Échanges notables : clarification technique de `construire_sft.py` (PR #44, MOBOTU-63) sur deux points bloquants (sections quasi-identiques non couvertes par les équivalences proches), commentaire d'explication publié avant validation. Décision de garder le test scellé chez un seul détenteur (P4) pour limiter le risque de contamination (R7 du cadrage).

## 5. Perspective critique sur le projet

Le partage d'un corpus unique entre les volets A et B a permis de produire une seule fois les questions et de comparer un modèle léger maîtrisé à un modèle emprunté puis adapté, mais il a aussi concentré le risque de contamination sur un seul jeu de données partagé par deux équipes de mesure différentes. Le protocole d'intervalle de confiance appliqué systématiquement aux décisions go/no-go (D12) a évité une mise en production prématurée de l'encodeur affiné ; ce garde-fou mériterait d'être documenté comme pratique à reconduire dès le cadrage initial d'un prochain projet, plutôt que découvert après une première contamination.
