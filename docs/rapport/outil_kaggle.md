# Outil novateur : Kaggle

## Nature

Kaggle est une plateforme de notebooks hébergés qu'on utilise depuis un navigateur. Elle donne accès gratuitement à un GPU, un Tesla T4 de 16 Go dans notre cas, dans la limite d'un quota. Nous nous en sommes servis pour les deux calculs du projet qui ne devaient dépendre d'aucun poste de l'équipe : l'affinage de l'encodeur du volet A (notebook nlp-a3b1-e5) et l'adaptation QLoRA du générateur du volet B (notebook nlp-a3b1-qlora).

## Qualités constatées

Il n'y a rien à installer. Le même notebook tourne quel que soit l'ordinateur du membre qui le lance, donc l'entraînement ne dépend d'aucune machine de l'équipe (architecture_B1.md, section 1). L'environnement est le même pour tous : nous gardons le PyTorch de l'image Kaggle pour le GPU et nous figeons le reste des versions dans b1/training/requirements-kaggle.txt (Transformers 5.17.0, PEFT 0.21.0, bitsandbytes 0.50.2). Le jeton Hugging Face est rangé dans les Secrets du notebook et jamais dans le code, si bien qu'il ne peut pas se retrouver dans le dépôt. Le T4 a largement suffi : le micro-essai du 24/11 n'a utilisé que 7,37 Go de mémoire GPU, ce qui a permis de garder 3 072 tokens par exemple, et l'entraînement complet de l'adaptateur v1, le 28/11, a pris 19 minutes (B1_entrainement.md).

## Défauts et conditions d'échec constatés

L'image logicielle de Kaggle impose ses propres versions, qui peuvent entrer en conflit avec les nôtres. Le 16/11, pour l'affinage de l'encodeur sur CPU, la bibliothèque torchvision 0.26.0 de l'image, prévue pour PyTorch 2.11.0, empêchait Transformers de charger l'encodeur avec PyTorch 2.14.0. Nous l'avons désinstallée après la première cellule du notebook (pull request #43). Ce notebook a aussi dû être exécuté deux fois, et seules les révisions de la seconde exécution, celle du 16/11, sont utilisées. Le T4 ne gère pas le format bf16, donc notre script calcule en fp16 (architecture_B1.md, section 5).

D'autres limites tiennent au compte et à la session. Le GPU et l'accès à Internet du notebook ne s'activent qu'après la vérification du compte par téléphone. Il faut aussi composer avec le quota hebdomadaire de GPU et la durée limitée des sessions. Enfin, les fichiers écrits dans /kaggle/working disparaissent avec la session : il faut les télécharger ou les publier avant qu'elle se ferme. Nos parades ont été le micro-essai, que le cadrage prévoyait contre ce risque (cadrage.md, risque R6), un entraînement complet court et la publication de chaque modèle à révision figée dans l'organisation Hugging Face de l'équipe (pull request #43, b1/config/models.lock.json).

## Retour d'expérience

Kaggle a servi à trois calculs : l'affinage de l'encodeur le 16/11 (92 paires question-passage, 3 époques, perte moyenne de 1,2332 à 0,2905), le micro-essai QLoRA le 24/11 et l'entraînement de l'adaptateur v1 le 28/11. Le micro-essai a réussi sans aucune des corrections de secours prévues (pull request #46), et la perte de développement de l'adaptateur est passée de 1,8534 à 0,4011 en deux époques (B1_entrainement.md). L'encodeur affiné n'a pas été mis en production : son nDCG@10 était meilleur (0,912 contre 0,832), mais la borne basse de l'intervalle de l'écart était négative et son cosinus minimal dans le navigateur, 0,9768, restait sous 0,99 (decisions.md, D12). Kaggle a fourni le calcul, pas la garantie d'un meilleur modèle. Le temps d'appropriation est resté court : 5 h saisies sur MOBOTU-64, script et micro-essai compris, et 3 h sur MOBOTU-52 (export Jira du 28/11).

Par rapport au J2, le changement est net. Le J2 annonçait MLX-LM, réservé aux Mac à puce Apple, et confiait l'entraînement au seul propriétaire de cette machine (decisions.md, D4 et D8). Nous l'avons abandonné pour une chaîne portable, et le Mac ne sert plus que de machine de démonstration. Colab restait un repli (cadrage.md, risque R6) que notre script prévoit (b1/training/entrainer_qlora.py), mais nous n'en avons pas eu besoin.
