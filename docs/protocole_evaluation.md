# Protocole d'évaluation

Ce protocole est fixé avant toute mesure. Toute modification ultérieure est datée dans `decisions.md`, avec sa raison.

## 1. Jeux de questions

| Ensemble | Familles | Questions | Dont hors corpus | Auteurs | Usage |
|---|---|---|---|---|---|
| Entraînement | 37 | 120 | 28 | P1, P2, P3, P5 (30 chacun) | adaptation de l'encodeur (A) et du générateur (B) |
| Développement | 12 | 40 | 8 | P1, P2, P3, P5 (10 chacun) | choix des configurations, seuils, go/no-go, itérations |
| Test scellé | 12 | 40 | 10 | P4 | évaluation finale, une seule fois |

**Familles.** Une famille est une section du corpus ; les cas et situations d'une unité sont rattachés à cette unité, car leurs textes se recoupent. Une famille entière appartient à un seul ensemble ; la répartition est tirée de façon reproductible (graine `nlp-a3-b1-2026`), stratifiée par fiche, selon un motif 60 / 20 / 20 (`shared/eval/familles.json`). Une question ne peut avoir pour sections d'or que des sections de son ensemble.

**Hors corpus.** Les thèmes hors corpus d'entraînement et de développement sont publics (`themes_hors_corpus.json`) et proches du sujet, y compris par homonymie (« stage de sensibilisation à la sécurité routière », « fonctionnaire stagiaire ») ; ceux du test sont choisis par son détenteur et ne sont connus que de lui. La réponse de référence d'une question hors corpus est la phrase d'abstention exacte.

**Consignes de rédaction.**
- Lire la section, la fermer, puis écrire la question avec ses propres mots, comme un élève, un étudiant, un parent ou un tuteur : une question qui recopie la fiche avantage artificiellement la recherche lexicale.
- Une question, un besoin d'information ; pas de question sur une situation personnelle détaillée.
- Pour chaque auteur, parmi ses 23 questions d'entraînement répondables : au moins 5 questions dont la réponse dépend d'un cas (élève ou étudiant, durée, type d'organisme), au moins 3 questions dont la réponse mobilise deux sections, au moins 5 questions sans aucun mot-clé de la section.
- Réponse de référence : trois phrases au plus, chaque phrase suivie de l'identifiant de la section qui la justifie, par exemple `[F32131-1.c2]`.

**Contrôles.** Saisie par `scripts/ajouter_question.py`, qui refuse une section d'un autre ensemble, une question déjà saisie ou une réponse qui ne cite pas ses sections d'or, et ajoute automatiquement les sections de texte identique. Validation par `scripts/valider_questions.py` : champs, identifiants uniques, doublons, étanchéité des familles, citations, forme des questions hors corpus. Relecture croisée par le binôme de chaque auteur, consolidation par P4.

## 2. Test scellé

1. Le détenteur (P4) écrit le test hors du dépôt, sur son poste (`~/nlp_scelle/questions_test.jsonl`), le valide avec `valider_questions --test`, puis le scelle : `scripts/sceller_test.py` écrit `shared/eval/test_scelle.json` (empreinte SHA-256, nombres, date), seul fichier versionné. Une seconde copie est conservée sur un support personnel hors ligne.
2. Le test n'est jamais versionné, jamais déposé sur un service en ligne, jamais montré, et ne sert à aucun réglage : prompts, seuils, découpages, modèles et adaptateurs sont choisis sur le développement.
3. Il est ouvert une seule fois, après le gel des deux configurations : tag `b1-config-gelee` pour le volet B ; pour le volet A, fusion des corrections issues du test utilisateur, après laquelle `a3/src/config.js` et `a3/public/data/` ne changent plus (le tag `site-gele` marque ensuite l'état publié et vérifié). Il est ouvert sur le poste du détenteur. L'empreinte est vérifiée automatiquement (`b1.eval.executer --scelle`) avant l'exécution.
4. Pour le volet A, le détenteur charge le fichier dans le mode évaluation du site déployé : le fichier est lu par le navigateur, sans envoi.
5. Après ouverture, aucune configuration n'est modifiée. Un défaut découvert à ce stade est décrit dans l'analyse ; s'il est corrigé, les deux résultats sont publiés, avant et après correction, et la correction est signalée.
6. Les sorties du test et leurs feuilles d'annotation restent sur le poste du détenteur ; seuls les résultats agrégés sont versionnés.

## 3. Volet A — recherche

**Unité de pertinence.** La section : une question répondable a un ensemble de sections d'or, toutes pertinentes au même degré. Le classement des passages (50 premiers) est converti en classement de sections : une section compte une fois, au rang de son meilleur passage. Cette règle rend comparables les trois découpages.

**Métriques**, calculées sur les questions répondables :
- Recall@k, k = 1, 3, 5, 10 : part des sections d'or présentes parmi les k premières sections ;
- MRR@10 : inverse du rang de la première section d'or, 0 au-delà du rang 10 ;
- nDCG@10 : gain 1 pour une section d'or, remise logarithmique, normalisation par le classement idéal ;
- intervalle de confiance à 95 % par bootstrap percentile sur les questions (2 000 tirages) ; comparaison de deux systèmes par l'écart apparié question par question et son intervalle bootstrap.

Métrique principale : nDCG@10. Métrique d'usage : Recall@5, puisque le site affiche cinq passages.

**Références lexicales.** BM25 (Okapi, paramètres par défaut de `rank-bm25` 0.2.2) et TF-IDF (`scikit-learn` 1.9.1, tf sous-linéaire, cosinus), sur les mêmes passages, avec la même normalisation des questions et des passages (minuscules, accents retirés, mots vides supprimés).

**Grille comparée sur le développement.** Trois découpages × {E5 préentraîné, E5 affiné si disponible} et BM25, TF-IDF sur chaque découpage. Les modèles denses sont mesurés dans le navigateur, avec le mode évaluation du site ; toutes les lignes sont ajoutées à `docs/resultats/A3_recherche.csv`.

**Règles de choix.**
- Découpage de production : meilleur nDCG@10 sur le développement ; si deux découpages sont à moins de 0,01, le plus fin est retenu, car il affiche des passages plus courts.
- Modèle : règle go/no-go de la décision D3.
- Seuil « proximité faible » : valeur sous laquelle tombent au plus 5 % des meilleurs scores des questions répondables du développement ; nous publions la part des questions hors corpus du développement qui passent sous ce seuil. Le seuil n'écarte aucun résultat : il ajoute une mention.

**Test.** Configuration de production, E5 préentraîné, BM25 et TF-IDF, mesurés une fois ; résultats avec intervalles et écarts appariés.

**Limites déclarées.** 30 questions répondables en test : les intervalles sont larges et un écart inférieur à leur demi-largeur n'est pas interprété. La pertinence binaire au niveau de la section ne distingue pas un passage qui contient la réponse d'un passage voisin de la même section.

## 4. Volet B — RAG et adaptation

**Configurations comparées.** Base (adaptateur à l'échelle 0) et adapté (échelle 1), sur un même serveur `llama-server`, avec le même fichier de base, le même contexte, le même prompt, les mêmes passages récupérés (`b1/config/rag.json`) et un décodage glouton. La configuration du serveur et l'état de l'adaptateur sont enregistrés dans `execution.json` de chaque exécution.

**Mesures automatiques** (`b1.eval.score_auto`) :

| Indicateur | Définition |
|---|---|
| Abstention correcte | questions hors corpus auxquelles le système s'abstient / questions hors corpus |
| Faux refus | questions répondables auxquelles le système s'abstient / questions répondables |
| Rappel de récupération | questions répondables dont au moins une section d'or figure dans les extraits fournis |
| Précision des citations | citations valides qui désignent une section d'or / citations valides |
| Citations invalides | réponses qui contiennent au moins une étiquette absente du contexte |
| Réponses non sourcées | réponses converties en abstention faute de citation valide |
| Latence | durée de bout en bout par question (récupération et génération), médiane et 95ᵉ centile |
| Débit | tokens générés par seconde, d'après les mesures du serveur |
| Mémoire | mémoire résidente maximale du processus `llama-server` pendant l'exécution, et mémoire totale du poste |
| Discordances appariées | questions où un seul des deux systèmes s'abstient, dans chaque sens |

**Annotation humaine en aveugle** (`preparer_annotation`, `agreger_annotation`). Pour chaque question, les deux réponses sont présentées sous les étiquettes X et Y tirées au hasard, lignes mélangées ; la clé reste chez P4. Deux annotateurs (P1, P2) notent chaque réponse indépendamment :

| Critère | 2 | 1 | 0 | Autre |
|---|---|---|---|---|
| Exactitude | correcte : contient l'information nécessaire de la réponse de référence, sans erreur | partielle : incomplète, ou condition essentielle omise | incorrecte : erreur ou réponse à une autre question | A : abstention |
| Appui | chaque phrase est appuyée par l'extrait qu'elle cite | une partie des phrases est appuyée | aucune phrase n'est appuyée | NA : abstention |

Chaque réponse partielle, incorrecte ou abstention erronée reçoit un code d'erreur (section 5). Une abstention se note toujours A ; pour une question hors corpus, une réponse se note 0 avec le code A2. L'accord entre annotateurs sur l'exactitude est mesuré par le kappa de Cohen sur les notes initiales ; les désaccords sont ensuite arbitrés par les deux annotateurs ensemble, avant la levée de la clé, dans une feuille de consensus sur laquelle portent les scores et la comparaison.

**Comparaison.** Pour chaque indicateur, valeur de la base, valeur de l'adapté et écart. Pour la comparaison appariée, une question est réussie si la réponse est correcte (question répondable) ou si le système s'abstient (question hors corpus) ; nous publions le nombre de questions où l'adapté réussit et la base échoue, l'inverse, et le test exact du signe sur ces questions discordantes (`agreger_annotation --consensus`). Nous ne concluons pas à un effet de l'adaptation si ce test ne l'établit pas ; nous décrivons alors la tendance observée.

**Règles de choix sur le développement.**
- Découpage du volet B : meilleur rappel de récupération avec le modèle de base ; à moins de 0,02 d'écart, `section`, qui fournit des unités normatives complètes.
- `seuil_score` : plus grand seuil qui ne fait refuser à tort aucune question répondable du développement, diminué de 0,01.
- Adaptateur v2 : entraîné si l'adapté ne fait pas mieux que la base sur l'exactitude correcte ou sur l'abstention correcte, ou si le faux refus augmente de plus de 10 points. La v2 ne change qu'un seul élément, fixé d'avance d'après le code d'erreur le plus fréquent hors récupération : A1 ou faux refus en hausse, part des exemples d'abstention faute de preuve ramenée de 0,5 à 0,25 ; A2, part portée à 0,75 ; codes C, F ou G, trois époques au lieu de deux. Elle remplace la v1 si, sur le développement et avec les mesures automatiques, l'abstention correcte ne baisse pas, le faux refus n'augmente pas de plus de 0,05 et la précision des citations ne baisse pas de plus de 0,02 ; l'exactitude n'est pas réannotée pour cette comparaison, limite déclarée dans le rapport.

**Latence et mémoire.** L'évaluation finale donne les mesures du poste du détenteur du test (8 Go ou plus, sans GPU dédié) ; la machine de démonstration donne des mesures séparées, sur le développement. Sur macOS, la mémoire allouée par Metal peut ne pas figurer dans la mémoire résidente : la valeur affichée par le Moniteur d'activité est relevée en complément.

## 5. Taxonomie des défauts

| Code | Famille | Définition |
|---|---|---|
| R1 | Récupération | aucune section d'or dans les extraits fournis |
| R2 | Récupération | une section d'or présente, mais une autre section ou un cas nécessaire manque |
| G1 | Génération | affirmation absente des extraits (invention) |
| G2 | Génération | condition ignorée ou cas confondu, par exemple une règle des élèves appliquée à un étudiant |
| G3 | Génération | durée, montant, seuil ou date erronés |
| C1 | Citation | phrase sans citation dans une réponse par ailleurs citée |
| C2 | Citation | citation valide dont l'extrait n'appuie pas la phrase |
| C3 | Citation | étiquette absente du contexte |
| A1 | Abstention | refus alors que les extraits contiennent la réponse |
| A2 | Abstention | réponse à une question hors corpus ou dont les extraits ne contiennent pas la réponse |
| F1 | Forme | plus de trois phrases, réponse tronquée, phrase d'abstention non exacte, autre langue |

Les fréquences par code et par système sont publiées dans `docs/resultats/B1_defauts.md`, avec dix cas commentés ; la feuille de route traite les codes les plus fréquents.

## 6. Calendrier des mesures

| Date | Mesure | Ensemble |
|---|---|---|
| 26/10/2026 | modèle de base du volet B, découpage, seuil | développement |
| 28/10/2026 | grille du volet A, choix du découpage | développement |
| 04/11/2026 | go/no-go de l'encodeur affiné | développement |
| 09–12/11/2026 | base et adapté, annotation en aveugle, décision v2 | développement |
| 25/11/2026 | évaluation finale des deux volets | test, une seule fois |
| 27–28/11/2026 | annotation du test, résultats avant/après | test |
