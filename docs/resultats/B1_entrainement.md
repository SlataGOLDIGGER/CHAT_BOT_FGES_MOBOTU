# Entraînement de l'adaptateur du volet B

Données : b1/training/donnees/sft_train.jsonl (164 exemples) et sft_dev.jsonl (58 exemples), empreintes dans entrainement.json.
Base : Qwen/Qwen3-4B-Instruct-2507, révision cdbee75f17c01a7cc42f958dc650907174af0554, quantifiée en NF4 (double quantification), calcul fp16.
LoRA : rang 16, α 32, dropout 0,05, projections q, k, v, o, gate, up, down ; AdamW 2·10⁻⁴, échauffement 10 %, lot effectif 8.

## Micro-essai (MOBOTU-64, 24/11/2026)

Environnement : Kaggle, GPU Tesla T4 ; PyTorch 2.11.0+cu130 ; Transformers 5.17.0 ; PEFT 0.21.0 ; bitsandbytes 0.50.2 ; commit 5977097 (branche MOBOTU-64-script-qlora).
Commande : python -m b1.training.entrainer_qlora --sortie /kaggle/working/micro --micro 20

| Mesure | Valeur |
|---|---|
| Paramètres entraînés (part) | 33 030 144 sur 4 055 498 240 (0,81 %) |
| Perte d'entraînement, moyenne des 5 premiers pas | 0,8158 |
| Perte d'entraînement, moyenne des 5 derniers pas | 0,3507 |
| Perte de développement avant / après | 1,8534 / 0,4251 |
| Mémoire GPU maximale | 7,37 Go |
| Durée des 20 pas | 520 s (580 s avec le calcul de la perte de développement finale) |
| generer_peft sur l'adaptateur du micro-essai | 20 réponses produites |

Conclusion : micro-essai réussi. Les 20 pertes sont finies et la moyenne des 5 derniers pas est bien plus basse que celle des 5 premiers. La perte varie beaucoup d'un pas à l'autre (de 0,09 à 0,66 sur la fin), ce qui est normal avec un lot effectif de 8 exemples. La perte de développement passe de 1,85 à 0,43. Avec 7,4 Go au maximum, on reste loin des 16 Go du T4, donc la longueur maximale de 3 072 tokens peut être gardée pour l'entraînement complet. Aucune des corrections prévues n'a été nécessaire.

## Entraînement v1 (MOBOTU-65, 28/11/2026)

Environnement : Kaggle, GPU Tesla T4 ; commit des données et des scripts : 5faad1e ; commande : python -m b1.training.entrainer_qlora --sortie /kaggle/working/adaptateur-v1

| Mesure | Valeur |
|---|---|
| Exemples d'entraînement / de développement | 164 / 58 |
| Pas d'optimisation | 42 (2 époques) |
| Perte de développement : initiale / époque 1 / époque 2 | 1,8534 / 0,4142 / 0,4011 |
| Durée de l'entraînement | 19 min (1 150 s) |
| Mémoire GPU maximale | 7,37 Go |
| Conversion | convert_lora_to_gguf.py, llama.cpp b11146, f16 ; 66,1 Mo |
| Publication | fges-nlp-a3b1/qwen3-4b-stages-lora, révision c97bf3bfa8ef0cd29bfecdfd5a1faea507c791ac, SHA-256 30fe55f0d7763879bd4ba61780c5f84f7973a3154322e1d530d7352f78d27a8d |
| Réponses PEFT de contrôle | b1/training/donnees/peft_dev20.jsonl (20 prompts du développement) |

Lecture : presque tout le gain arrive pendant la première époque (la perte de développement passe de 1,85 à 0,41), la deuxième n'apporte plus qu'un petit mieux (0,40). La perte de développement continue de baisser légèrement, donc pas de signe de surapprentissage sur 2 époques. La perte d'entraînement reste irrégulière d'un pas à l'autre (de 0,06 à 0,43 sur la deuxième époque), comme pendant le micro-essai. Le journal complet, avec la perte de chaque pas, est publié avec l'adaptateur (peft-v1/entrainement.json).

Vérification sur le poste P5 (macOS, Apple A18 Pro, 8 Go) : python -m b1.scripts.telecharger_modeles se termine par "OK : b1/models/adaptateur-v1.gguf" (empreinte vérifiée) et python -m b1.scripts.lancer_serveur --adaptateur b1/models/adaptateur-v1.gguf affiche "Serveur prêt sur http://127.0.0.1:8080 en 23 s".
