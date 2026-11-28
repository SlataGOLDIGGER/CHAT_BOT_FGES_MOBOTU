# Évaluation du volet B

Protocole : docs/protocole_evaluation.md, section 4. Chaque tableau indique la date, le commit, le poste et l'ensemble.

## Choix du découpage et du seuil (développement, modèle de base, 16/11/2026, commit ef4f26d, poste de P4)

Développement corrigé par D14 : 40 questions, dont 32 répondables et 8 hors corpus.

| Découpage | Rappel de récupération | Abstention correcte | Faux refus |
|---|---|---|---|
| section | 0.844 | 1.0 | 0.094 |
| fenetre | 0.906 | 1.0 | 0.062 |
| paragraphe | 0.906 | 1.0 | 0.094 |

Découpage retenu : fenetre (règle : meilleur rappel ; section si écart < 0,02 ; fenetre et paragraphe à égalité, la commande de la fiche retient le premier maximum, voir D10).
Seuil : score maximal le plus bas d'une question répondable = 0.8503 ; seuil_score = 0.8403 ; questions hors corpus écartées par le seuil : 0 sur 8.

## Référence du modèle de base (développement)

| Indicateur | Valeur |
|---|---|
| Abstention correcte (8 hors corpus) | 1.0 |
| Faux refus (32 répondables) | 0.062 |
| Rappel de récupération | 0.906 |
| Précision des citations | 0.756 |
| Réponses avec citation invalide | 0 |
| Réponses converties en abstention (non sourcées) | 0 |
| Latence p50 / p95 (s) | 9.35 / 13.53 |
| Débit (tokens/s) | 21.6 |
| Mémoire maximale du serveur (Mo) | 8035.4 |

Une première mesure du 15/11 (poste de P1, #38) portait sur 30 questions de développement, avant la fusion des questions de P5 et la correction D14 ; elle est remplacée par celle-ci.

## Comparaison base / adapté v1 (développement, 28/11/2026, poste de P4)

Deux exécutions appariées sur les mêmes 40 questions de développement (32 répondables, 8 hors corpus), serveur unique avec l'adaptateur v1 chargé, échelle 0 (base) et échelle 1 (adapté).

| Indicateur | Base (échelle 0) | Adapté v1 (échelle 1) |
|---|---|---|
| Abstention correcte (8 hors corpus) | 1.0 | 1.0 |
| Faux refus (32 répondables) | 0.062 | **0.312** |
| Rappel de récupération | 0.906 | 0.906 |
| Précision des citations | 0.756 | 0.913 |
| Réponses avec citation invalide | 0 | 0 |
| Réponses converties en abstention (non sourcées) | 0 | 0 |
| Latence p50 / p95 (s) | 12.55 / 18.61 | 11.63 / 15.48 |
| Débit (tokens/s) | 19.3 | 17.2 |

Discordances : 8 refus nouveaux sur des questions répondables côté adapté (0 corrigé, 0 perdu/gagné côté hors corpus).

Lecture : l'adaptateur v1 améliore nettement la précision des citations (+0.157) mais introduit un refus de répondre sur 8 questions répondables supplémentaires (faux refus multiplié par 5), sans gain sur le rappel de récupération ni la latence. Exécutions : `artifacts/b1/runs/dev-base`, `artifacts/b1/runs/dev-adapte` (hors dépôt). Feuille d'annotation en aveugle préparée pour P1/P2 : `artifacts/b1/annotation/dev-v1/feuille.csv` (clé de correspondance gardée par P4).

## Évaluation finale sur le test scellé (28/11/2026, poste de P4)

Empreinte du test scellé vérifiée avant exécution (sha256 `b82a4dcf…`, conforme à `shared/eval/test_scelle.json`). Deux exécutions appariées sur les 40 questions de test (30 répondables, 10 hors corpus), même serveur avec l'adaptateur v1 chargé, échelle 0 (base) et échelle 1 (adapté).

| Indicateur | Base (échelle 0) | Adapté v1 (échelle 1) |
|---|---|---|
| Abstention correcte (10 hors corpus) | 1.0 | 1.0 |
| Faux refus (30 répondables) | 0.0 | 0.033 |
| Rappel de récupération | 1.0 | 1.0 |
| Précision des citations | 0.837 | 0.966 |
| Réponses avec citation invalide | 0 | 0 |
| Réponses converties en abstention (non sourcées) | 0 | 0 |
| Latence p50 / p95 (s) | 14.0 / 19.81 | 12.99 / 15.46 |
| Débit (tokens/s) | 17.1 | 16.6 |

Discordances : 1 refus nouveau sur une question répondable côté adapté (0 corrigé, 0 perdu/gagné côté hors corpus).

Lecture : sur le test, l'adaptateur v1 confirme le gain de précision des citations observé sur le développement (+0.129) avec un coût en faux refus très inférieur à celui mesuré sur le dev (1 cas contre 8 sur 32 répondables) ; le rappel de récupération et l'abstention restent parfaits dans les deux configurations. Exécutions : `C:\Users\prode\nlp_scelle\runs\test-base`, `C:\Users\prode\nlp_scelle\runs\test-adapte` (hors dépôt, poste de P4, détenteur du test scellé).
