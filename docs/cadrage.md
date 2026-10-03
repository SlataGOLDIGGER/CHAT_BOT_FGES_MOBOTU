# Cadrage du projet

## Objet

Deux applications de traitement du langage sur un corpus normatif commun, les fiches Service-Public consacrées aux stages des élèves et des étudiants en France :

- **volet A, cas A3 — recherche sémantique en corpus fermé** : un site public qui retrouve les passages pertinents pour une question en langage naturel, calcul effectué dans le navigateur, sans génération de texte ;
- **volet B, cas B1 — assistant réglementaire sourcé** : une application locale qui répond en citant systématiquement ses sources et s'abstient lorsque le corpus ne contient pas l'information, avec un modèle open-weights adapté par l'équipe.

Le partage du corpus n'est pas imposé : nous l'avons retenu pour produire une seule fois le corpus et les questions, et pour comparer directement un modèle léger maîtrisé (A) et un modèle emprunté puis adapté (B).

## Périmètre

**Livré**

- Volet A : site statique à URL fixe sur Vercel ; périmètre interrogeable affiché ; pour chaque question, cinq passages classés avec leur score de similarité, la référence de leur section et le lien vers la fiche complète ; modèle téléchargé une fois puis mis en cache ; mode évaluation et mode diagnostic réservés à l'équipe.
- Volet B : application locale Streamlit ; RAG complet ; citations `[S1]…[S5]` contrôlées automatiquement ; abstention explicite ; adaptateur QLoRA entraîné par l'équipe et chargé localement ; comparaison avant/après sur un test scellé ; caractérisation des défauts ; feuille de route.
- Commun : corpus versionné de 7 fiches (74 sections) avec manifeste et empreintes ; 200 questions réparties en familles étanches entre entraînement, développement et test ; protocole d'évaluation écrit.
- Conduite : dépôt Git, board Jira, classeur de suivi et journal d'usage de l'IA partagés, rapport, supports de pitch et de présentation, vidéos de démonstration.

**Non livré (déclaré)**

- aucune génération de texte dans le volet A ;
- aucun appel à un service d'inférence distant ni à une API payante, dans aucun volet ;
- aucun corpus fourni par le visiteur ;
- pas de règlement interne d'établissement, pas de traitement d'une situation personnelle, pas d'offres de stage, pas de stages à l'étranger, pas de statut de fonctionnaire stagiaire ;
- pas de fonctionnement entièrement hors ligne du site ;
- extensions traitées seulement après l'attendu : WebGPU, recherche hybride, Code de l'éducation, encodeur entraîné from scratch, accélération MLX sur Mac.

## Hypothèses

| # | Hypothèse | Risque associé |
|---|---|---|
| 1 | Les fiches restent réutilisables avec attribution ; le corpus figé au 09/10/2026 reste la référence du projet | R3 |
| 2 | Le premier téléchargement du modèle du volet A (environ 115 Mo) reste acceptable pour un visiteur | R1 |
| 3 | Un poste de 8 Go de mémoire sans GPU exécute le volet B (estimation : 3,9 à 4,5 Go) | R5 |
| 4 | Un GPU gratuit accessible depuis un navigateur suffit pour l'adaptation QLoRA | R6 |
| 5 | Le corpus fournit assez de familles indépendantes : 61 familles, pour 120 questions d'entraînement, 40 de développement et 40 de test, dont environ un quart hors corpus | R4 |
| 6 | Le plan gratuit de Vercel reste disponible et permet la collaboration sur un dépôt public | R9 |

## Risques

| # | Risque | Effet | Action prévue | Rôle |
|---|---|---|---|---|
| R1 | Premier téléchargement trop lourd ou trop lent | abandon du visiteur | taille mesurée et affichée, progression séparée pour l'index et le modèle, message explicite | P2 |
| R2 | Cache du navigateur indisponible (navigation privée) | retéléchargement à chaque visite | détection et message, bouton d'effacement du cache | P2 |
| R3 | Extraction incomplète, cas conditionnels perdus ou fusionnés | règles fausses restituées | contrôle automatique des cas et situations, relecture à deux section par section | P1, P4 |
| R4 | Ensembles de développement et de test petits | conclusions fragiles | intervalles bootstrap publiés, limites déclarées, pas de reformulations artificielles | P4 |
| R5 | Mémoire insuffisante sur un poste | évaluation impossible sur ce poste | contexte réduit, puis quantification plus légère, décision tracée | P4 |
| R6 | Quota ou vérification du compte GPU gratuit | adaptation retardée | deux comptes vérifiés dès la première semaine, repli Colab, micro-essai précoce | P3, P5 |
| R7 | Contamination du test | résultats non défendables | familles étanches, test scellé chez un seul détenteur, aucun réglage sur le test | P4 |
| R8 | Citation inventée ou réponse non sourcée | perte de traçabilité | contrôle automatique des citations, conversion en abstention | P3 |
| R9 | Évolution des conditions d'hébergement gratuit | site non livrable | repli GitHub Pages documenté, URL vérifiée dix jours avant la soutenance | P5 |
| R10 | Indisponibilité d'un membre | jalon manqué | domaine secondaire et binôme pour chaque domaine, fiches de tâches autonomes | P5 |
| R11 | Service tiers bloqué le jour de la soutenance (Hugging Face, jsDelivr) | démonstration A impossible | cache préchauffé, partage de connexion, vidéo de secours | P2 |

L'état de chaque risque est suivi dans l'onglet « Risques » du classeur de suivi.

## Critères de réussite

- **Volet A** : URL publique fonctionnelle, vérifiée depuis un autre appareil au plus tard dix jours avant la soutenance ; les quatre sorties demandées (passage, score, référence de section, lien) ; résultats sur le test comparés à BM25 et TF-IDF ; aucune requête d'inférence distante (vérifiée dans l'onglet Réseau).
- **Volet B** : adaptateur chargé et vérifié techniquement ; comparaison base / adapté sur le test scellé à configuration identique ; exactitude, validité et appui des citations, abstention correcte, faux refus, latence et mémoire mesurés ; défauts caractérisés ; feuille de route rédigée ; chaîne vérifiée sous Windows, Linux et macOS.
- **Conduite** : tickets créés avant la réalisation ; historique Git cohérent avec la répartition ; journal d'usage de l'IA tenu au fil du travail ; chaque membre capable d'expliquer n'importe quelle partie du code.

## Rôles

| Rôle | Domaine principal | Domaine secondaire | Binôme de relecture |
|---|---|---|---|
| P1 | Corpus : collecte, extraction, découpage, manifeste | Données d'adaptation du volet B, supports de présentation | P4 |
| P2 | Volet A : interface, Web Worker, index, exécution navigateur | Interface locale du volet B, déploiement | P5 |
| P3 | Volet B : RAG, script d'adaptation, gel de la configuration, machine de démonstration | Volet A : encodeur affiné, mesures, test utilisateur | P2 |
| P4 | Jeu de questions, protocole et banc d'évaluation, test scellé | Corpus (relectures), chaîne locale du volet B | P1 |
| P5 | Coordination, Git, Jira, intégration continue, rapport | Volet B : entraînement sur GPU distant, adaptateur, portabilité | P3 |

Le volet B est réparti entre les cinq rôles (P1 20 %, P2 13 %, P3 21 %, P4 28 %, P5 18 % de sa charge estimée). Chaque réunion hebdomadaire comprend une mini-démonstration présentée par un membre qui n'a pas écrit la partie montrée. La correspondance entre rôles et membres est tenue dans le classeur de suivi partagé avec l'enseignant.

## Jalons et échéances internes

| Jalon | Date | Échéance interne |
|---|---|---|
| Mi-parcours (contrôle sur pièces) | dimanche 18/10/2026 | jeudi 15/10/2026 |
| J3 | lundi 16/11/2026 | vendredi 13/11/2026 |
| Gel du site du volet A | — | vendredi 27/11/2026, vérifié depuis un autre appareil le samedi 28/11/2026 |
| Rapport V1 | strictement avant J4 | jeudi 03/12/2026 |
| J4, soutenance | lundi 07/12/2026 | vendredi 04/12/2026 |
