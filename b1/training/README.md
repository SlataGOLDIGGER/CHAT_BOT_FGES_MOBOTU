# b1/training — adaptation du générateur

| Élément | Rôle |
|---|---|
| `construire_sft.py` | exemples d'adaptation supervisée construits avec le même prompt qu'à l'inférence : réponses citées, abstentions hors corpus, abstentions quand les passages d'or sont retirés du contexte |
| `donnees/` | exemples d'entraînement et de développement (versionnés ; aucune question du test) |
| `entrainer_qlora.py` | adaptation QLoRA (NF4, calcul fp16) avec masquage du prompt, écrêtage du gradient, perte de développement par époque |
| `requirements-kaggle.txt` | versions installées dans le notebook Kaggle |

L'entraînement s'exécute sur un GPU gratuit accessible depuis un navigateur (Kaggle). L'adaptateur est converti en GGUF par le convertisseur de llama.cpp du build figé, publié dans l'organisation Hugging Face de l'équipe, puis référencé avec son empreinte dans `b1/config/models.lock.json`.
