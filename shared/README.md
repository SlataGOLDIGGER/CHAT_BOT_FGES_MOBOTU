# shared — données communes aux deux volets

| Dossier | Contenu |
|---|---|
| `corpus/` | fiches sources figées, sections, passages selon trois découpages, manifeste avec empreintes, date de collecte et attribution |
| `eval/` | familles de questions et leur répartition, questions d'entraînement et de développement, empreinte du test scellé |

Les deux volets partagent les textes, les identifiants et les questions, mais pas les vecteurs : le site calcule les siens avec Transformers.js, le volet B avec ONNX Runtime.
