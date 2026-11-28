# MOBOTU-105 — Documenter l'outil novateur « llama.cpp »

## Nature

llama.cpp est un moteur d'inférence en C/C++ pour modèles de langage au format GGUF, exécutable localement sans GPU dédié ni service distant. Dans le projet, il est installé via un build figé (`python -m b1.scripts.installer_llama`) qui télécharge l'archive officielle correspondant à la plateforme du poste, vérifie son empreinte, puis l'extrait dans `b1/runtime/` (non versionné). Le serveur HTTP `llama-server` expose ensuite le modèle sur `127.0.0.1`, avec ou sans adaptateur LoRA chargé (`python -m b1.scripts.lancer_serveur`).

Version utilisée dans le projet : build b11146, commit 7fe450e19 (plateforme windows-x64).

## Qualités

- **Portabilité locale sans dépendance réseau** : aucune inférence distante, répond directement au critère de non-livraison du cadrage (« aucun appel à un service d'inférence distant »).
- **Quantification GGUF** : le modèle Qwen3-4B-Instruct-2507-Q4_K_M (quantification Q4_K Medium) tient en mémoire sur un poste de 8 Go sans GPU, conforme à l'hypothèse 3 du cadrage (3,9 à 4,5 Go estimés).
- **Chargement d'adaptateur à l'échelle contrôlable** : le script `verifier_adaptateur.py` (MOBOTU-66) prouve le chargement en comparant les sorties à l'échelle 0 (identique au serveur sans adaptateur) et à l'échelle 1.
- **Empreintes vérifiées de bout en bout** : archive du moteur, modèle GGUF, encodeur et adaptateur sont tous vérifiés par empreinte avant usage (`models.lock.json`).

## Défauts et limites observés

- **Débit de génération instable sur poste partagé** : 10,9 tokens/s mesurés le 18/10, contre environ 21 tokens/s mesurés sur le même poste le 07/10 lors de la mise au point initiale (NLP-16) — écart non expliqué avec certitude (poste sur secteur, mode d'alimentation « Utilisation normale », plusieurs applications ouvertes), consigné tel quel sans correction appliquée.
- **Conflit de port fréquent** : le port 8080 par défaut est souvent déjà occupé par un autre service local, nécessitant systématiquement `--port 8081` ou équivalent.
- **Téléchargement de modèles parfois bloqué** : le protocole Xet de Hugging Face (`hf_xet`) s'est interrompu deux fois sans erreur vers 1 Go reçu ; contournement par `HF_HUB_DISABLE_XET=1` (téléchargement HTTP classique).
- **Pas de garantie de portabilité binaire automatique** : chaque plateforme (Windows/Linux/macOS) nécessite son propre binaire figé et sa propre vérification d'empreinte (MOBOTU-72, CI de portabilité dédiée).

## Usage dans le projet

Chaîne complète : installation du moteur → téléchargement des modèles et de l'adaptateur → lancement du serveur → génération d'essai → vérification technique de l'adaptateur → évaluation comparée base/adapté sur le jeu de développement puis sur le test scellé.

## Temps d'appropriation

Installation et première génération locale réussie en une session (poste P4, relevé du 18/10/2026), après une réinstallation complète depuis zéro (`git clean -fdX b1/runtime b1/models`) pour valider la reproductibilité de la procédure.

## Échecs ou limites rencontrés

Aucun échec bloquant de l'outil lui-même : les incidents rencontrés (port occupé, téléchargement interrompu, débit instable) ont tous été contournés sans modification du moteur, et consignés tels quels dans `docs/environnement/P4.md` plutôt que corrigés silencieusement, conformément à la règle de traçabilité du projet.
