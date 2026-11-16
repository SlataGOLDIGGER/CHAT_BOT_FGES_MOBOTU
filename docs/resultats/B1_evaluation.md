## Choix du découpage et du seuil (développement, modèle de base, 15/11/2026, commit 62, poste de P1)

| Découpage | Rappel de récupération | Abstention correcte | Faux refus |
|---|---|---|---|
| section |0.708|1.0|0.125|
| fenetre |0.833|1.0|0.125|
| paragraphe |0.708|1.0|0.125|

Découpage retenu : fenetre (règle : meilleur rappel ; section si écart < 0,02).
Seuil : score maximal le plus bas d'une question répondable = 0.708 ; seuil_score = 0.8403 ; questions hors corpus écartées par le seuil : 0 sur 8.

## Référence du modèle de base (développement)

| Indicateur | Valeur |
|---|---|
| Abstention correcte (8 hors corpus) |1.0|
| Faux refus (32 répondables) |0.125|
| Rappel de récupération |0.833|
| Précision des citations |0.742|
| Réponses avec citation invalide |0|
| Réponses converties en abstention (non sourcées) |0|
| Latence p50 / p95 (s) |47.74/71.94|
| Débit (tokens/s) |4.8|
| Mémoire maximale du serveur (Mo) | |