# b1/scripts — moteur local et preuves de fonctionnement

| Script | Rôle |
|---|---|
| `installer_llama.py` | télécharge l'archive llama.cpp du build figé adaptée au système, vérifie son empreinte, l'extrait dans `b1/runtime/` |
| `telecharger_modeles.py` | télécharge le générateur GGUF, l'encodeur et l'adaptateur publié à leur révision figée, vérifie les empreintes |
| `lancer_serveur.py` | lance `llama-server` sur `127.0.0.1` avec la configuration figée, avec ou sans adaptateur |
| `generer_essai.py` | première génération : preuve de fonctionnement sur le poste |
| `verifier_adaptateur.py` | preuve technique du chargement de l'adaptateur (sorties aux échelles 0 et 1) |
