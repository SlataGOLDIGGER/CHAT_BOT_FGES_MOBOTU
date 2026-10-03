# a3/training — encodeur affiné par l'équipe

`affiner_e5.py` affine `intfloat/multilingual-e5-small` par apprentissage contrastif sur les paires question–passage de l'ensemble d'entraînement (négatifs pris dans le lot), puis exporte le modèle en ONNX et le quantifie en q8 avec la même recette que le modèle de référence (`MatMul` et `Gather`, par canal, QInt8). Avec `--epoques 0`, il exporte le modèle préentraîné par la même chaîne, pour isoler l'effet de l'entraînement de celui de l'export.

Exécution prévue dans un notebook Kaggle sur CPU ; dépendances dans `requirements-kaggle.txt`. Les modèles produits sont publiés dans l'organisation Hugging Face de l'équipe et ne sont jamais versionnés.
