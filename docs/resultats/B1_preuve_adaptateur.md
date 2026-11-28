# Preuve du chargement de l'adaptateur

Date : 28/11/2026 · commit : e3c2b04 (branche MOBOTU-65-adaptateur-v1) · poste : P5 (macOS, Apple A18 Pro, 8 Go) · serveur : llama.cpp b11146-7fe450e19, Qwen3-4B-Instruct-2507 Q4_K_M, contexte 4096
Adaptateur : adaptateur-v1.gguf, SHA-256 30fe55f0d7763879bd4ba61780c5f84f7973a3154322e1d530d7352f78d27a8d (identique à b1/config/models.lock.json : oui)
Commandes : python -m b1.scripts.verifier_adaptateur, puis, serveur relancé sans adaptateur, python -m b1.scripts.verifier_adaptateur --sans

Question posée : "Quelle est la durée maximale d'un stage dans une même entreprise ?", avec un seul extrait qui contient la réponse (6 mois par organisme d'accueil et par année d'enseignement).

| Contrôle | Résultat |
|---|---|
| Adaptateurs listés par le serveur (GET /lora-adapters) | id 0, b1/models/adaptateur-v1.gguf, échelle 1,0 |
| Sortie à l'échelle 0 | "La durée maximale d'un stage est de 6 mois par organisme d'accueil et par année d'enseignement. Cette limite s'applique à chaque entreprise d'accueil. [S1]" |
| Sortie à l'échelle 1 | "Je ne trouve pas cette information dans les fiches du corpus." |
| Sorties différentes (l'adaptateur agit) | oui |
| Sortie du serveur sans adaptateur | "La durée maximale d'un stage est de 6 mois par organisme d'accueil et par année d'enseignement. Cette limite s'applique à chaque entreprise d'accueil. [S1]" |
| Échelle 0 identique au serveur sans adaptateur (base inchangée) | oui |

Conclusion : l'adaptateur est chargé et actif ; l'échelle 0 reproduit le modèle de base, ce qui valide la comparaison avant/après dans un même processus (décision D4).

Remarque : sur cette question, l'adaptateur s'abstient alors que l'extrait contient la réponse, ce qui correspond à un faux refus (code A1 du protocole). Une seule question ne permet pas de conclure, mais c'est un point à surveiller dans l'évaluation sur le développement (MOBOTU-67) et dans la décision d'itération D13 : la part d'exemples d'abstention dans les données d'adaptation est la piste prévue si les faux refus augmentent.
