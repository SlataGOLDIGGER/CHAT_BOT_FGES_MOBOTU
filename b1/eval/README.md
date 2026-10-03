# b1/eval — évaluation du volet B

| Module | Rôle |
|---|---|
| `executer.py` | exécute la chaîne sur un fichier de questions, à une échelle d'adaptateur donnée ; enregistre sorties, durées, mémoire du serveur et configuration réellement chargée |
| `score_auto.py` | abstention correcte, faux refus, rappel de la récupération, précision des citations, latences, vitesse ; comparaison appariée de deux exécutions |
| `preparer_annotation.py` | feuille d'annotation humaine en aveugle (systèmes masqués X et Y, ordre aléatoire) et clé de correspondance |
| `agreger_annotation.py` | exactitude et appui par système, accord entre annotateurs (kappa de Cohen), désaccords à arbitrer |

Les sorties vont dans `artifacts/b1/runs/` (non versionné) ; les résultats agrégés sont reportés dans `docs/resultats/`. Les exécutions sur le test scellé sont écrites hors du dépôt.
