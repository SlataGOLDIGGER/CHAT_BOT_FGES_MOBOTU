# b1/config — configuration figée

| Fichier | Contenu |
|---|---|
| `models.lock.json` | build de llama.cpp et empreinte SHA-256 de chaque archive par système ; générateur GGUF (dépôt, révision, fichier, empreinte, taille, licence, base Hugging Face d'entraînement) ; encodeur (dépôt, révision, fichier) ; adaptateur publié (dépôt, révision, fichier, empreinte) ou `null` |
| `rag.json` | stratégie de découpage, nombre de passages fournis au modèle, seuil de score sous lequel le système s'abstient sans appeler le modèle |

Toute modification de ces fichiers passe par un ticket et une pull request, puis par une nouvelle validation sur le jeu de développement.
