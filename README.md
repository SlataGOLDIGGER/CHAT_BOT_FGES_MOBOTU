# NLP A3-B1 — recherche sémantique et assistant sourcé sur les stages

Projet du module NLP 2 (M2 Data & IA, FGES). Deux applications de traitement du langage sur un même corpus : sept fiches Service-Public consacrées aux stages des élèves et des étudiants en France.

| Volet | Cas d'usage | Régime technique | Où |
|---|---|---|---|
| A | A3 — Recherche sémantique en corpus fermé | site statique, inférence dans le navigateur (Transformers.js), aucune génération | `a3/` |
| B | B1 — Assistant réglementaire sourcé | application locale, modèle open-weights adapté (QLoRA), architecture RAG, citations et abstention | `b1/` |

Le corpus, les questions d'évaluation et les scripts de préparation sont communs aux deux volets (`shared/`, `scripts/`).

## Installation

Prérequis figés : Git, Python 3.12.13 (environnements créés avec `uv`), Node.js 24 LTS. L'environnement réel de chaque poste est consigné dans `docs/environnement/`, à partir du modèle `MODELE.md`.

```bash
git clone <adresse du dépôt> nlp-a3-b1
cd nlp-a3-b1
uv venv --python 3.12.13 .venv-data
uv venv --python 3.12.13 .venv-b1
```

Environnement de préparation des données (macOS et Linux ; sous Windows, `.venv-data\Scripts\Activate.ps1`) :

```bash
source .venv-data/bin/activate
uv pip install --only-binary :all: -r scripts/requirements.txt
```

Environnement du volet B :

```bash
source .venv-b1/bin/activate
uv pip install --only-binary :all: -r b1/requirements.txt
```

Site du volet A :

```bash
cd a3
npm ci
```

## Lancement

**Volet A** (dossier `a3/`) : `npm run dev` ouvre le site en local ; `npm run build` produit le site statique dans `a3/dist/` ; `npm run index` reconstruit l'index des passages après toute modification du corpus ou du modèle. Le site publié est construit par Vercel à chaque fusion sur `main`.

**Volet B** (racine du dépôt, environnement `.venv-b1`) :

```bash
python -m b1.scripts.installer_llama        # une fois : moteur llama.cpp figé
python -m b1.scripts.telecharger_modeles    # une fois : modèles à révision figée, empreintes vérifiées
python -m b1.scripts.lancer_serveur         # terminal 1, laissé ouvert
streamlit run b1/app/app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --client.toolbarMode minimal   # terminal 2, puis ouvrir http://127.0.0.1:8501
```

Toutes les commandes Python s'exécutent depuis la racine du dépôt sous la forme `python -m paquet.module`.

## Organisation du dépôt

```text
a3/          site du volet A (Vite, Web Worker, index statique) et affinage de l'encodeur
b1/          application locale du volet B (RAG, interface, évaluation, adaptation)
shared/      corpus versionné avec manifeste, questions d'entraînement et de développement
scripts/     préparation et contrôle des données, évaluation de la recherche
docs/        cadrage, décisions, conventions, architectures, protocole, résultats
artifacts/   sorties calculées, non suivies par Git
```

## Sources et licence du corpus

Source : Service-Public.gouv.fr, Direction de l'information légale et administrative (DILA), jeu de données « Fiches pratiques et ressources de Service-Public.gouv.fr Particuliers », réutilisé sous Licence Ouverte / Open Licence 2.0. La date de collecte et les empreintes figurent dans `shared/corpus/manifest.json`. Les modèles utilisés gardent leur propre licence (MIT pour l'encodeur E5, Apache-2.0 pour Qwen3-4B-Instruct-2507).

## Documentation

`docs/cadrage.md` (périmètre, hypothèses, risques, critères de réussite, rôles), `docs/decisions.md` (arbitrages datés), `docs/conventions.md` (branches, commits, pull requests), `docs/architecture_A3.md`, `docs/architecture_B1.md`, `docs/protocole_evaluation.md`, `docs/resultats/`.
