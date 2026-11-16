# Décisions et arbitrages

Chaque entrée est datée. Une décision qui modifie un point déclaré au J2 est annoncée à l'enseignant ; son statut passe à « validée » lorsque sa réponse est reçue. Les abandons de fonctionnalités sont consignés ici au même titre que les choix.

| # | Date | Sujet | Statut |
|---|---|---|---|
| D1 | 25/09/2026 | Corpus étendu à 7 fiches, collecte depuis le jeu de données XML officiel | annoncée, validation attendue |
| D2 | 25/09/2026 | Hébergement du volet A sur Vercel, dépôt public | annoncée, validation attendue |
| D3 | 25/09/2026 | Encodeur du volet A : préentraîné, puis affiné candidat avec règle go/no-go | annoncée, validation attendue |
| D4 | 25/09/2026 | Chaîne portable du volet B : llama.cpp, GGUF, QLoRA sur GPU distant gratuit | annoncée, validation attendue |
| D5 | 25/09/2026 | Board Jira, liaison GitHub, accès de l'enseignant | annoncée |
| D6 | 25/09/2026 | Index du volet A calculé à la construction | annoncée |
| D7 | 25/09/2026 | Récupération du volet B par ONNX Runtime | annoncée |
| D8 | 25/09/2026 | Répartition du volet B entre les cinq rôles | annoncée |
| D9 | 25/09/2026 | Journal d'usage de l'IA tenu dans le classeur partagé | annoncée |
| D10 | 16/11/2026 | Découpage et seuil du volet B | appliquée |
| D11 | 26/10/2026 | Découpage de production du volet A | appliquée |
| D14 | 15/11/2026 | Correction de l'étanchéité des familles de questions | appliquée localement, à annoncer |

## D1 — Corpus : sept fiches, collecte XML officielle

**Contexte.** Les trois fiches déclarées au J2 (F16734, F32131, F637) donnent 39 sections et 35 familles de questions : c'est peu pour séparer entraînement, développement et test, et pour départager une référence lexicale et la recherche dense.

**Options.** Conserver les trois fiches ; étendre aux fiches Service-Public liées ; ajouter les articles L124-1 à L124-20 et D124-1 à D124-13 du Code de l'éducation ; changer de corpus.

**Décision.** Nous avons retenu l'extension à quatre fiches référencées par F16734 et relevant du même régime : F1882, F13879, F34857, F13881. Le corpus compte 74 sections et 61 familles. La collecte passe par l'archive XML publiée par la DILA sur data.gouv.fr, et non par l'extraction de pages HTML : les chapitres, sous-chapitres, cas et situations y sont balisés. Le Code de l'éducation est classé en extension : il demanderait un second mode de collecte et doublerait l'annotation, une même règle figurant à la fois dans une fiche et dans un article.

**Écartées, réservées aux questions hors corpus.** F33375 (prime d'activité), F17312 (titre de séjour d'un stagiaire étranger), F382 et F384 (stages à l'étranger), fiches sur le fonctionnaire stagiaire et F14208 (stage de sensibilisation à la sécurité routière), ces deux dernières par homonymie.

**Conséquence.** Gel du corpus v2 le 09/10/2026, avant la rédaction des questions.

## D2 — Hébergement du volet A sur Vercel

**Contexte.** Le J2 retenait GitHub Pages ; le contrôle du J2 portait sur un projet Vercel relié au dépôt.

**Décision.** Site publié sur Vercel (plan gratuit, usage non commercial), branche de production `main`, dossier racine `a3`, fichiers statiques uniquement. Dépôt public. Les poids du modèle restent sur Hugging Face, à révision figée ; le moteur ONNX Runtime Web est chargé depuis jsDelivr ; Vercel ne sert que la page, le code et l'index. GitHub Pages reste un repli documenté (variable `BASE_PATH` de la configuration Vite).

**Conséquence.** Les adresses de préversion ne contiennent que des identifiants neutres ; les commentaires automatiques de Vercel sur les pull requests sont désactivés.

## D3 — Encodeur du volet A

**Contexte.** Le sujet valorise un modèle entraîné par l'équipe ; le J2 partait d'un encodeur préentraîné.

**Décision.** À la mi-parcours, `Xenova/multilingual-e5-small` quantifié q8, à révision figée. Pour J3, un encodeur affiné par l'équipe : apprentissage contrastif sur les paires question–passage d'entraînement, avec négatifs pris dans le lot ; export ONNX et quantification q8 selon la même recette que le modèle de référence. L'export du modèle préentraîné par la même chaîne sert de point de comparaison.

**Règle go/no-go, sur le jeu de développement, dans le navigateur.** Le modèle affiné remplace le modèle préentraîné si (1) son nDCG@10 dépasse celui de l'export préentraîné d'au moins 0,03 avec une borne basse positive de l'intervalle bootstrap à 95 % de l'écart apparié, (2) son Recall@5 ne baisse pas de plus de 0,02, (3) le diagnostic navigateur donne un cosinus minimal d'au moins 0,99. Un encodeur entraîné from scratch reste une extension.

## D4 — Chaîne portable du volet B

**Contexte.** Le J2 déclarait MLX-LM et une exécution réservée à Apple Silicon.

**Décision.** Inférence par llama.cpp (build `b11146`, binaires officiels pour Windows, Linux et macOS) ; générateur `Qwen3-4B-Instruct-2507` inchangé, au format GGUF Q4_K_M (2,5 Go) ; adaptation QLoRA (NF4, rang 16, sept projections) avec PEFT sur un GPU gratuit accessible depuis un navigateur ; conversion de l'adaptateur en GGUF par le convertisseur du même build ; chargement local. Le Mac de l'équipe n'est qu'un accélérateur (Metal) et la machine de démonstration.

**Identité avant/après.** Un seul serveur charge l'adaptateur ; chaque requête fixe son échelle à 0 (base) ou 1 (adapté). Tout le reste est identique : binaire, fichier de base, contexte, prompt, passages, décodage glouton.

**Évaluation finale.** Sur le poste du détenteur du test, quel que soit son système.

## D5 — Board Jira

Projet Jira `NLP`, colonnes « À préciser », « Prêt », « En cours », « À vérifier », « Terminé ». Les clés des tickets figurent dans les noms de branche, les messages de commit et les titres de pull request, ce qui relie Jira et GitHub. Le plan gratuit ne proposant pas de lecture seule, l'enseignant se voit proposer un compte membre ; des captures datées du board sont fournies à chaque jalon.

## D6 — Index du volet A calculé à la construction

**Contexte.** Le J2 prévoyait de calculer les vecteurs des passages dans le navigateur à la première visite, avec un cache IndexedDB.

**Mesure.** Sur un poste récent, l'encodage des 256 passages dans le navigateur prend environ 16 s ; sur un mobile, la durée serait nettement supérieure. Les vecteurs calculés sous Node avec le même modèle et la même bibliothèque diffèrent légèrement de ceux du navigateur (cosinus moyen 0,997).

**Décision.** L'index est calculé à la construction avec Transformers.js et publié en fichiers statiques nommés par leur empreinte ; une clé d'invalidation (modèle, révision, quantification, préfixes, agrégation, normalisation, découpage, empreinte des passages) est vérifiée par le navigateur. La question reste encodée dans le navigateur. Pour mesurer le système réellement déployé, l'évaluation de la recherche s'exécute dans le navigateur (mode évaluation) ; le mode diagnostic mesure l'écart entre vecteurs.

## D7 — Récupération du volet B par ONNX Runtime

**Contexte.** Le J2 prévoyait sentence-transformers, donc PyTorch, dont les versions récentes ne fournissent plus de roue pour les Mac Intel.

**Décision.** Le volet B encode avec ONNX Runtime 1.23.2 le même fichier q8 que le site, un texte à la fois (avec la quantification dynamique, un vecteur dépend de la composition du lot). L'index du volet B reste distinct de celui du site.

## D8 — Répartition du volet B

**Contexte.** Le J2 confiait l'entraînement et les mesures du volet B au seul propriétaire de la machine cible.

**Décision.** Le volet B est réparti entre les cinq rôles ; la part de P3 est de 21 % de sa charge estimée, dont 4 % liés à la machine de démonstration (mesures sur cette machine et démonstration).

## D9 — Journal d'usage de l'IA

Le journal d'usage de l'IA est tenu dans le classeur de suivi partagé avec l'enseignant, et non dans `docs/` comme annoncé au J2.

## D10 — Découpage et seuil du volet B (16/11/2026)

Mesures sur le développement corrigé par D14 (40 questions : 32 répondables, 8 hors corpus), modèle de base, k = 5, poste de P4 : rappel de récupération section 0.844 ; fenetre 0.906 ; paragraphe 0.906.
Règle (protocole, section 4) : meilleur rappel de récupération ; à moins de 0,02 de section, section est gardé. Seuil : plus bas des meilleurs scores des questions répondables, moins 0,01.
Décision : découpage fenetre ; seuil_score = 0.8403 (questions hors corpus écartées par le seuil : 0 sur 8). fenetre et paragraphe sont à égalité sur le rappel ; la commande de la fiche NLP-59 parcourt section, fenetre, paragraphe et retient le premier maximum, soit fenetre, qui a aussi le plus faible faux refus (0.062 contre 0.094).
Le seuil n'écarte aucune question hors corpus (meilleur score hors corpus : 0.875, au-dessus du seuil) : les scores de l'encodeur sont resserrés et l'abstention repose sur le modèle, qui s'abstient sur les 8 questions hors corpus.
Historique : une première mesure du 15/11 (poste de P1, #38) portait sur 30 questions de développement, avant la fusion des questions de P5 et la correction D14 ; ses chiffres sont remplacés. Le découpage et le seuil retenus sont inchangés.
Conséquence : b1/config/rag.json ; ces réglages servent à la construction des données d'adaptation (NLP-60) et restent fixes jusqu'au gel (NLP-71).

## D11 — Découpage de production du volet A (26/10/2026)

Mesures sur le développement (32 questions répondables), dans le navigateur, E5 préentraîné : nDCG@10 section 0.6543 ; fenetre 0.7973 ; paragraphe 0.7783.

Meilleure référence lexicale sur ce découpage : TF-IDF/fenetre (nDCG@10 0.7216).

Règle (protocole, section 3) : meilleur nDCG@10 ; à moins de 0,01, le découpage le plus fin.

Décision : découpage fenetre.

Conséquence : PRODUCTION = { modele: 'pre', strategie: 'fenetre' } dans a3/src/config.js ; l'encodeur affiné est jugé sur ce découpage (D12).

## D14 — Étanchéité des familles de questions (15/11/2026)

**Constat.** Le tirage déterministe séparait des règles identiques ou quasi identiques de F1882 entre entraînement, développement et test. `valider_questions` ne contrôlait que l'appartenance des identifiants de section, donc pouvait afficher « Questions conformes » malgré cette fuite. Une famille de développement était également absente du champ `famille` des questions alors que sa section figurait déjà dans leurs sections d'or.

**Options.** Garder le tirage et publier des scores avec et sans les questions touchées aurait laissé un test partiellement contaminé. Redistribuer toutes les familles aurait demandé davantage de réécriture et changé les quotas par fiche. P4 retient une correction ciblée du tirage et la reprise des questions affectées.

**Décision appliquée localement.** Regrouper dans un seul ensemble les textes identiques et les trois quasi-doublons vérifiés ; conserver 37 / 12 / 12 familles et les comptes par fiche. Les affectations modifiées sont explicites et reproductibles dans `scripts/repartir_familles.py`. Le validateur contrôle désormais les groupes équivalents et la cohérence du champ `famille`. P4 a réécrit 32 lignes train/dev avec assistance IA ; le champ `auteur` continue de désigner le rôle propriétaire initial, et le bilan donne la provenance réelle des révisions. Les questions de test touchées ont été réécrites hors dépôt et sont attribuées à P4. Le scellement exige la validation complète des trois jeux.

**Conséquences.** Le bilan MOBOTU-45 est corrigé localement ; les mesures de développement obtenues avec l'ancien partage ne sont pas comparables aux nouvelles mesures. Si un modèle a été entraîné sur l'ancien jeu, l'entraînement doit repartir du modèle de base après correction des questions ; réutiliser l'ancien point de contrôle contaminerait le test. Cette correction est à annoncer à l'enseignant selon la règle d'en-tête du présent registre ; son statut passera à « validée » après sa réponse.

## Autres ajustements de forme

Les fiches d'environnement annoncées sous les noms `docs/environment.md` et `docs/environment-b1.md` sont remplacées par une fiche par rôle dans `docs/environnement/`. Les risques figurent dans `docs/cadrage.md` et leur suivi dans le classeur. Le verrou de dépendances du volet B s'appelle `b1/requirements.txt`.
