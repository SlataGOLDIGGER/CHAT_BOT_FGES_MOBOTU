# Architecture du volet B — assistant réglementaire sourcé

## 1. Chaîne portable

| Étape | Choix | Figé par |
|---|---|---|
| Moteur d'inférence | llama.cpp, `llama-server` du build `b11146` (commit `7fe450e1`), binaires officiels : macOS arm64 et x64, Windows x64 et arm64, Linux x64 et arm64 ; accélération Metal automatique sur Mac, CPU ailleurs | empreinte SHA-256 de chaque archive dans `b1/config/models.lock.json` |
| Générateur | `Qwen3-4B-Instruct-2507` (licence Apache-2.0), GGUF Q4_K_M du dépôt `unsloth/Qwen3-4B-Instruct-2507-GGUF`, révision `a06e946b…`, 2 497 281 120 octets | empreinte SHA-256 vérifiée après téléchargement |
| Base d'entraînement | `Qwen/Qwen3-4B-Instruct-2507`, révision `cdbee75f…` ; ses poids n'ont pas changé depuis leur publication, antérieure au fichier GGUF | `models.lock.json` |
| Encodeur de récupération | `Xenova/multilingual-e5-small` q8, exécuté par ONNX Runtime 1.23.2, un texte à la fois | `models.lock.json`, `b1/requirements.txt` |
| Interface | Streamlit 1.64.0, accessible uniquement depuis le poste (`127.0.0.1`) | `b1/requirements.txt` |
| Adaptation | QLoRA avec PEFT 0.21.0, Transformers 5.17.0, bitsandbytes 0.50.2, sur GPU gratuit accessible depuis un navigateur (Kaggle) | `b1/training/requirements-kaggle.txt` |
| Conversion | `convert_lora_to_gguf.py` de llama.cpp au tag `b11146` | tag du dépôt llama.cpp |

Aucune étape n'exige un système particulier : l'installation, l'inférence, le RAG, la préparation des données, l'évaluation et l'interface s'exécutent sous Windows, Linux et macOS ; l'entraînement s'exécute sur Kaggle, depuis un navigateur. Une exécution automatique sur les trois systèmes (workflow `b1-portabilite`) en apporte la preuve.

**Accès au serveur local.** `llama-server` n'écoute que sur `127.0.0.1` et accepte par défaut les requêtes de n'importe quelle origine web : une page ouverte dans le navigateur du poste pourrait l'interroger. `lancer_serveur` tire donc une clé d'accès aléatoire à chaque lancement, la transmet au serveur par variable d'environnement (elle n'apparaît pas dans la ligne de commande) et l'enregistre dans `artifacts/b1/serveur.json`, hors du dépôt, où le client la lit. Seul `/health` reste accessible sans clé.

## 2. Configuration minimale et machine de démonstration

- **Minimale** : 8 Go de mémoire, processeur 64 bits, 4 Go d'espace disque libre, sans GPU ; Python 3.12 ; navigateur récent.
- **Machine de démonstration** : ordinateur portable Apple Silicon, 24 Go de mémoire unifiée, utilisé pour la démonstration et la mesure de la latence ; il n'intervient ni dans l'entraînement ni dans l'évaluation finale.

## 3. Estimation mémoire à l'inférence

| Poste | Valeur | Nature |
|---|---|---|
| Poids Q4_K_M | 2,50 Go | taille du fichier |
| Cache clé-valeur, 4 096 tokens | 576 Mio | 2 × 36 couches × 8 têtes clé-valeur × 128 × 2 octets par token |
| Tampons de calcul | 0,3 à 0,5 Go | estimation |
| Adaptateur LoRA f16 | 66 Mo | 33 millions de paramètres |
| Encodeur et ONNX Runtime | 0,3 Go | estimation |
| Python et Streamlit | 0,3 à 0,5 Go | estimation |
| Total | 3,9 à 4,5 Go | estimation, remplacée par les mesures de `docs/resultats/` |

Si la mémoire manque, nous réduisons d'abord le contexte, puis nous passons à une quantification plus légère du même dépôt, et nous consignons la décision.

## 4. RAG

**Récupération.** Les passages de la stratégie choisie sur le développement sont encodés une fois (index mis en cache dans `artifacts/b1/index/`, clé dérivée de l'empreinte des passages et de la révision de l'encodeur) ; la question est encodée avec le préfixe `query: ` ; les `k` = 5 passages les plus proches au sens du cosinus sont retenus. Stratégie par défaut : `section`, qui fournit au modèle des unités normatives complètes.

**Gabarit de prompt.** Format ChatML de Qwen, écrit par notre code (et non par le gabarit embarqué dans le GGUF), identique à l'entraînement et à l'inférence :

```text
<|im_start|>system
Tu es un assistant qui répond en français à des questions sur les stages, uniquement à partir des extraits fournis.
Règles :
1. N'utilise que les informations présentes dans les extraits.
2. Termine chaque phrase de ta réponse par la référence de l'extrait qui la justifie, entre crochets, par exemple [S2].
3. Si les extraits ne permettent pas de répondre, réponds exactement : Je ne trouve pas cette information dans les fiches du corpus.
4. Réponds en trois phrases au plus.<|im_end|>
<|im_start|>user
Extraits :
[S1] <chemin de titres>
<texte du passage>

[S2] …

Question : <question><|im_end|>
<|im_start|>assistant
```

**Décodage.** Glouton : `temperature` 0, `top_k` 1, `seed` 42, 256 tokens au plus, arrêt sur `<|im_end|>`, `cache_prompt` désactivé pour que chaque requête soit calculée à l'identique.

**Format de citation.** `[Sn]`, où `n` est le rang du passage dans le contexte fourni ; l'application relie chaque étiquette à la section, à sa référence et au lien de la fiche.

**Politique d'abstention.**
1. Si le meilleur score de récupération est inférieur au seuil `seuil_score` de `b1/config/rag.json`, calibré sur le développement, le système s'abstient sans appeler le modèle.
2. Si le modèle produit la phrase d'abstention, le système s'abstient.
3. Si la réponse ne contient aucune citation valide, elle est remplacée par la phrase d'abstention (« réponse non sourcée »), le texte brut étant conservé pour l'évaluation.

**Contrôle automatique des citations.** Chaque étiquette citée doit exister dans le contexte fourni ; les étiquettes invalides, les phrases sans citation et la part des citations qui pointent vers une section d'or sont comptées pour l'évaluation.

## 5. Adaptation

**Objectif.** Apprendre au modèle à utiliser les extraits, à citer chaque phrase et à s'abstenir, non à mémoriser des réponses.

**Données** (`b1/training/construire_sft.py`), construites à partir des seules questions d'entraînement et de développement, avec le même prompt qu'à l'inférence :
- *réponse* : contexte récupéré, complété au besoin par le meilleur passage de chaque section citée ; cible = réponse de référence dont les citations de sections sont converties en étiquettes `[Sn]` ;
- *abstention hors corpus* : question hors corpus, contexte récupéré ; cible = phrase d'abstention ;
- *abstention faute de preuve* : pour la moitié des questions répondables (tirage reproductible), contexte privé de toute section d'or ; cible = phrase d'abstention.

**Hyperparamètres.** QLoRA : poids de base en NF4 avec double quantification, calcul en fp16 (les GPU T4 et P100 ne gèrent pas le bf16) ; LoRA de rang 16, α = 32, dropout 0,05, sur les projections `q`, `k`, `v`, `o`, `gate`, `up`, `down` de toutes les couches ; AdamW, taux 2·10⁻⁴, échauffement de 10 % puis décroissance linéaire ; 2 époques ; accumulation de 8 exemples ; longueur maximale 3 072 tokens ; écrêtage du gradient à 1 ; graine 42. La perte ne porte que sur la complétion : les tokens du prompt sont masqués.

**Micro-essai.** 20 pas d'optimisation : perte finie et décroissante, adaptateur enregistré, mémoire GPU maximale relevée.

**Entraînement, conversion, publication.** Entraînement complet sur Kaggle ; perte de développement à chaque époque ; conversion en GGUF f16 ; publication dans l'organisation Hugging Face de l'équipe ; référence et empreinte dans `models.lock.json`.

**Preuve du chargement de l'adaptateur.** `GET /lora-adapters` du serveur liste l'adaptateur et son échelle ; `verifier_adaptateur.py` compare les sorties aux échelles 0 et 1 sur un même prompt, et l'identité entre l'échelle 0 et un serveur sans adaptateur est vérifiée.

**Transfert entre entraînement et inférence.** L'adaptateur est appris sur une base NF4 et appliqué à une base Q4_K_M ; l'accord entre les sorties de PEFT et de llama.cpp sur 20 prompts du développement (abstention, présence de citations) mesure l'effet de cette différence. Sous 80 % d'accord, la base Q8_0 du même dépôt (4,3 Go) est essayée sur les postes de 16 Go, et la décision est consignée dans `decisions.md`.

## 6. Démonstration et vidéo de secours

- Démonstration en direct sur la machine de démonstration : serveur lancé à l'avance, interface ouverte, trois questions préparées (une réponse sourcée, une question conditionnelle, une question hors corpus), activation puis désactivation de l'adaptateur.
- Vidéo de secours de 4 minutes au plus, enregistrée avant la soutenance avec la configuration gelée, lien testé par un autre membre.
