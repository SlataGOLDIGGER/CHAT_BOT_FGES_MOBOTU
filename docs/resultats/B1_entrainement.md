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
