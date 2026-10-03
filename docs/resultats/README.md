# docs/resultats — mesures et résultats

Chaque fichier est produit par un ticket et relu par son binôme. Les chiffres proviennent des sorties des scripts, jamais d'une saisie à la main ; chaque tableau indique la date, le commit, la machine et l'ensemble de questions.

| Fichier | Contenu |
|---|---|
| `A3_faisabilite.md` | essai de faisabilité : une phrase encodée dans un Web Worker, dimension, norme, temps de chargement et d'encodage |
| `A3_recherche.csv` | journal des mesures de recherche : une ligne par combinaison et par ensemble (ajoutée par `evaluer_recherche --journal`) |
| `A3_recherche.md` | comparaison des découpages et des références lexicales, décision go/no-go, résultats du test |
| `A3_performances.md` | taille téléchargée, temps de chargement, latence, écart des vecteurs, par navigateur et sur mobile |
| `A3_test_utilisateurs.md` | protocole, tâches, observations, corrections du parcours |
| `A3_verification_gel.md` | vérification du site gelé depuis un autre appareil |
| `B1_entrainement.md` | micro-essai, entraînements, pertes, durée, mémoire GPU, conversion, transfert vers llama.cpp |
| `B1_preuve_adaptateur.md` | preuve du chargement de l'adaptateur et de l'identité de la configuration de base |
| `B1_evaluation.md` | références du modèle de base, développement, test : avant/après, annotation, accord |
| `B1_machine_demo.md` | latence et mémoire sur la machine de démonstration |
| `B1_defauts.md` | fréquences des codes d'erreur, dix cas commentés |

Les sorties détaillées (classements, réponses) restent dans `artifacts/`, hors du dépôt ; celles du test restent sur le poste de son détenteur.
