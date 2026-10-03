# scripts — préparation des données et contrôles

Tous les scripts s'exécutent depuis la racine du dépôt, dans l'environnement `.venv-data`, sous la forme `python -m scripts.<nom>`.

| Script | Rôle |
|---|---|
| `verifier_poste.py` | relevé de l'environnement du poste pour la fiche `docs/environnement/` |
| `tester_hf.py` | appel authentifié à Hugging Face (identité du jeton et téléchargement) |
| `collecter_fiches.py` | téléchargement de l'archive officielle et extraction des fiches retenues |
| `extraire_sections.py` | découpage des fiches en sections, contrôle de conservation des cas et situations |
| `decouper_passages.py` | passages selon trois stratégies, longueurs en tokens de l'encodeur |
| `construire_manifeste.py`, `verifier_corpus.py` | manifeste et contrôle d'intégrité du corpus |
| `repartir_familles.py` | familles de questions et répartition entraînement, développement, test |
| `ajouter_question.py`, `valider_questions.py`, `sceller_test.py` | saisie guidée, validation et scellement des questions |
| `classer_lexical.py`, `evaluer_recherche.py` | références BM25 et TF-IDF, métriques de recherche avec intervalles |
| `verifier_depot.py` | contrôle d'hygiène des fichiers suivis (secrets, poids, fichiers interdits) |

Dépendances à versions exactes : `requirements.txt`.
