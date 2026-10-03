# b1/rag — chaîne RAG

| Module | Rôle |
|---|---|
| `encodeur.py` | encodeur E5 exécuté par ONNX Runtime, un texte à la fois, préfixes `query:` et `passage:` |
| `recherche.py` | index des passages (mis en cache dans `artifacts/b1/index/`), classement par similarité cosinus |
| `prompt.py` | consigne système, numérotation des extraits `[S1]…[Sk]`, gabarit ChatML de Qwen ; même fonction à l'entraînement et à l'inférence |
| `client_llm.py` | appels HTTP au serveur local `llama-server` (génération, état, adaptateurs, échelle de l'adaptateur par requête) |
| `citations.py` | extraction et validation des citations, détection de la phrase d'abstention |
| `pipeline.py` | récupération, seuil de score, génération, contrôle des citations, abstention |
| `demander.py` | question posée depuis le terminal |
