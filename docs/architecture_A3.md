# Architecture du volet A — recherche sémantique en corpus fermé

## 1. Chaîne du corpus

```text
archive XML officielle ─► fiches retenues (source/, empreintes) ─► sections (chapitres, sous-chapitres, cas, situations)
    ─► passages selon trois découpages (+ chemin de titres) ─► manifeste (empreintes, date, attribution)
    ─► index du site (vecteurs par modèle et par découpage, clé d'invalidation)
```

- **Collecte.** L'archive `vosdroits-latest.zip` (schéma 3.5) du jeu de données « Fiches pratiques et ressources de Service-Public.gouv.fr Particuliers » est téléchargée une fois ; les fiches retenues en sont extraites telles quelles. `collecte.json` conserve la date de collecte, l'empreinte SHA-256 de l'archive et celle de chaque fiche. Aucune page HTML n'est extraite.
- **Extraction.** Chaque fiche est parcourue selon ses unités balisées : `Chapitre`, `SousChapitre`, `Cas` (dans `BlocCas`) et `Situation` (dans `ListeSituations`). Une section contient le texte propre de son unité (paragraphes, listes, tableaux, encadrés « À noter », « Attention », « Exemple »), sans celui des unités imbriquées, qui forment leurs propres sections. Les titres forment le chemin de la section. Les services en ligne, références et définitions de fin de fiche sont exclus. Un tableau et un encadré restent un seul bloc.
- **Cas conditionnels.** Chaque branche d'un `BlocCas` ou d'une `ListeSituations` devient une unité distincte dont le titre (par exemple « Vous êtes stagiaire étudiant ») figure dans le chemin : deux branches ne sont jamais fusionnées. L'extraction vérifie automatiquement que chaque branche du XML est présente dans au moins une section ; toute perte est une erreur bloquante.
- **Découpages comparés.** `section` : une section par passage, scindée par blocs au-delà de 480 tokens ; `fenetre` : fenêtres de 128 tokens avec recouvrement de 32, sans franchir une frontière de section ; `paragraphe` : un passage par bloc, une introduction terminée par « : » et les éléments de liste qui la suivent restant groupés, les blocs très courts rattachés au suivant. Chaque passage est précédé du chemin de titres de sa section (« Fiche › Chapitre › Cas »). Les longueurs sont comptées avec le tokenizer de l'encodeur : aucun passage ne dépasse 512 tokens.
- **Identifiants stables.** Section : fiche et positions (`F32131-1.c2`) ; passage : section, initiale de la stratégie et rang (`F32131-1.c2#p3`). Les fiches étant figées, les identifiants ne varient pas d'une exécution à l'autre.
- **Manifeste.** `manifest.json` : éditeur, jeu de données, adresse et empreinte de l'archive, licence, texte d'attribution, fiches (titre, lien, date de mise à jour, empreinte), version du corpus, version du découpage, empreintes et nombres de lignes des fichiers dérivés. `verifier_corpus.py` contrôle ces empreintes avant toute évaluation.

État du corpus version 2 : 7 fiches, 74 sections ; 75 passages `section`, 113 passages `fenetre`, 256 passages `paragraphe`.

## 2. Modèle

| Élément | Valeur |
|---|---|
| Modèle de production (mi-parcours) | `Xenova/multilingual-e5-small`, révision `761b726dd34fb83930e26aab4e9ac3899aa1fa78`, conversion ONNX de `intfloat/multilingual-e5-small` (licence MIT) |
| Poids chargés | `onnx/model_quantized.onnx` (q8), 113 Mo |
| Vecteurs | 384 dimensions, moyenne des états de sortie pondérée par le masque, normalisation L2 |
| Préfixes | `query: ` pour la question, `passage: ` pour les passages |
| Longueur maximale | 512 tokens |
| Candidat J3 | encodeur affiné par l'équipe, publié dans l'organisation Hugging Face de l'équipe à révision figée |

**Affinage.** Paires question–passage des seules questions d'entraînement ; le passage positif est, parmi les passages des sections d'or, le plus proche selon le modèle de départ. Perte InfoNCE (entropie croisée sur les similarités divisées par une température de 0,05) avec les autres passages du lot comme négatifs ; les lots ne contiennent jamais deux fois la même section, pour éviter les faux négatifs. AdamW, taux 2·10⁻⁵, écrêtage du gradient à 1.

**Conversion et quantification.** Export ONNX par l'exportateur `dynamo` de PyTorch avec axes dynamiques (l'export par traçage fige des longueurs et dégrade la fidélité) ; attention « eager » ; quantification dynamique `MatMul` et `Gather`, par canal, plage réduite, poids QInt8, soit la recette du modèle de référence. Contrôles : cosinus PyTorch / ONNX fp32 supérieur à 0,9999 et PyTorch / ONNX q8 supérieur à 0,998. Seul le fichier quantifié est publié.

**Hébergement des poids.** Hugging Face, révision figée ; jamais dans le dépôt ni sur Vercel. Transformers.js 4.3.0 interroge aussi la branche `main` du dépôt de modèle pour des métadonnées (tailles de fichiers, configuration) ; les poids et le tokenizer sont téléchargés à la révision demandée, ce qui se vérifie dans le stockage du cache du navigateur.

## 3. Architecture navigateur

```text
page (main.js) ──initialiser(modèle, découpage)──► Web Worker (worker.js)
                                                    ├─ index.json (no-cache) : combinaisons, clés, périmètre
                                                    ├─ passages-<découpage>-<empreinte>.json  (cache long)
                                                    ├─ vecteurs-<modèle>-<découpage>-<empreinte>.bin (cache long)
                                                    └─ modèle Hugging Face + moteur WASM (cache du navigateur)
page ◄── perimetre, progression, pret, resultats, erreur, evaluation, diagnostic ── Web Worker
```

- **Web Worker.** Tout le calcul (chargement, encodage, classement) s'exécute hors du fil principal : l'interface reste réactive ; le champ de recherche reste désactivé tant que le moteur n'est pas prêt.
- **Messages.** `initialiser`, `chercher`, `evaluer`, `diagnostic` vers le worker ; `perimetre`, `progression` (index, modèle, octets chargés), `avertissement`, `pret` (durée), `resultats` (durée), `evaluation`, `diagnostic`, `erreur` vers la page.
- **Caches.** Modèle et tokenizer : cache « transformers-cache » du navigateur, clé incluant la révision. Moteur WASM : mis en cache par Transformers.js. Index : fichiers nommés par leur empreinte et servis avec un en-tête de cache long ; `index.json` est servi sans cache.
- **Clé d'invalidation.** Pour chaque combinaison, `index.json` porte l'empreinte SHA-256 d'un descripteur : dépôt, révision et quantification du modèle, découpage, préfixes, agrégation, normalisation, empreinte des passages. Le worker recalcule ce descripteur à partir de sa propre configuration et refuse un index qui ne correspond pas.
- **Classement.** Produit scalaire des vecteurs normalisés (similarité cosinus), cinq meilleurs passages affichés.
- **Mode évaluation** (`?evaluation`, réservé à l'équipe). Un fichier de questions choisi sur le poste est lu par le navigateur sans aucun envoi ; chaque question est encodée par le moteur de production et classée sur 50 passages ; le classement est téléchargé au format JSONL et évalué par `scripts/evaluer_recherche.py`. Nous mesurons ainsi le système réellement déployé.
- **Mode diagnostic** (`?diagnostic=20` ou `?diagnostic=tout`). Recalcule dans le navigateur les vecteurs de passages publiés et mesure leur cosinus avec ceux de l'index, la durée d'encodage et la latence d'une question.

## 4. Spécification UX

- **Périmètre affiché** au-dessus du champ : nombre de fiches et de passages, date de collecte, liste des fiches avec lien et date de mise à jour, thèmes non couverts.
- **Chargement** : message d'état et deux barres de progression (index, modèle), taille téléchargée du modèle ; message « Moteur prêt en x s » ; zone d'état annoncée aux lecteurs d'écran (`aria-live`).
- **Saisie** : champ de recherche étiqueté, 300 caractères au plus, trois exemples cliquables ; question vide refusée avec message.
- **Résultats** : liste ordonnée ; pour chaque passage, la référence (chemin de titres), le score de similarité à trois décimales, le texte du passage, le lien « Lire la fiche complète » ; durée du calcul ; aide « Comment lire le score ? » ; mention « proximité faible » sous un seuil calibré sur le développement.
- **États** : vide (invitation), recherche en cours, erreur de chargement (message et conduite à tenir), cache indisponible (avertissement), index incompatible (erreur explicite).
- **Accessibilité** : langue déclarée, lien d'évitement, titres hiérarchisés, contrastes suffisants, focus visible, navigation complète au clavier, respect de la préférence de réduction des animations, mode sombre.
- **Mobile** : mise en page fluide, champ et bouton qui passent à la ligne, cibles tactiles suffisantes.
- **Transparence** : pied de page indiquant que la question n'est envoyée à aucun serveur, d'où viennent le modèle et le moteur, et l'attribution de la source.

## 5. Mesures prévues

| Mesure | Méthode |
|---|---|
| Taille téléchargée au premier chargement (modèle, moteur, index, page) | onglet Réseau des outils de développement, cache vidé |
| Temps jusqu'à « Moteur prêt », premier chargement et rechargement | message d'état |
| Latence d'une recherche (médiane et 95ᵉ centile sur 20 questions) | durée affichée pour chaque recherche |
| Écart des vecteurs navigateur / index | mode diagnostic, trois navigateurs et un mobile |
| Qualité : Recall@k, MRR@10, nDCG@10 | mode évaluation puis `evaluer_recherche.py`, voir `protocole_evaluation.md` |
| Accessibilité | audit Lighthouse, navigation au clavier |
| Absence d'inférence distante | onglet Réseau : seules les requêtes de fichiers (site, Hugging Face, jsDelivr) apparaissent |

## 6. Déploiement

- Vercel, projet relié au dépôt ; dossier racine `a3` ; construction `npm ci` puis `npm run build` ; sortie `dist` ; Node.js 24 ; branche de production `main` ; une préversion par pull request.
- En-têtes (`a3/vercel.json`) : cache long pour `assets/` et les fichiers d'index à empreinte, pas de cache pour `index.json`, `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`.
- Gel du site le 27/11/2026 (tag `site-gele`), vérification depuis un autre appareil le 28/11/2026.
- Repli : GitHub Pages, construction avec `BASE_PATH=/<nom du dépôt>/`.
