# Recherche du volet A : mesures et décisions

Protocole : docs/protocole_evaluation.md, section 3. Journal complet : A3_recherche.csv (une ligne par système et par ensemble).

## Choix du découpage (développement, 32 questions répondables, 26/10/2026, commit e84a4bd, navigateur Google Chrome 128.0.6586.0)

| Système | Découpage | R@1 | R@5 | MRR@10 | nDCG@10 | IC95 nDCG@10 |
|---|---|---|---|---|---|---|
| E5 préentraîné (navigateur) | section | 0.5312 | 0.6875 | 0.6168 | 0.6543 | [0.4422, 0.8559] |
| E5 préentraîné (navigateur) | fenetre | 0.6250 | 0.8438 | 0.8042 | 0.7973 | [0.6289, 0.9356] |
| E5 préentraîné (navigateur) | paragraphe | 0.5625 | 0.8438 | 0.7667 | 0.7783 | [0.6128, 0.9145] |
| BM25 | section | 0.4062 | 0.7812 | 0.5917 | 0.6772 | [0.5313, 0.8191] |
| BM25 | fenetre | 0.4375 | 0.8125 | 0.6340 | 0.7010 | [0.5457, 0.8449] |
| BM25 | paragraphe | 0.4062 | 0.7500 | 0.6163 | 0.6731 | [0.4953, 0.8400] |
| TF-IDF | section | 0.3750 | 0.7500 | 0.5601 | 0.6530 | [0.4972, 0.8050] |
| TF-IDF | fenetre | 0.4688 | 0.8438 | 0.6464 | 0.7216 | [0.5689, 0.8603] |
| TF-IDF | paragraphe | 0.3438 | 0.8125 | 0.6007 | 0.6814 | [0.5316, 0.8243] |



Écart apparié nDCG@10, E5 moins BM25 sur le découpage retenu : non calculable à partir des moyennes agrégées ; IC95 non calculable ; E5 meilleur sur un nombre indéterminé de questions, moins bon sur un nombre indéterminé.

Règle : meilleur nDCG@10 d'E5 ; à moins de 0,01, le découpage le plus fin.

Décision : découpage **fenêtre** (docs/decisions.md, D11).

Lecture : E5 obtient le meilleur nDCG@10 avec le découpage fenêtre (0,7973 ; IC95 [0,6289 ; 0,9356]), contre 0,7010 pour BM25 (IC95 [0,5457 ; 0,8449]). Les intervalles se chevauchent : la supériorité statistique d'E5 n'est donc pas établie. L'écart moyen non apparié est de +0,0963. Les questions sur lesquelles BM25 fait mieux ne peuvent pas être identifiées sans les résultats individuels par question.