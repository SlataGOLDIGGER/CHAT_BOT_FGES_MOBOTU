# Fiche d'environnement — <rôle>

Copier ce modèle sous le nom `docs/environnement/<rôle>.md` (par exemple `P3.md`), puis remplacer chaque `…` par la sortie des commandes indiquées, sans la modifier. Aucun nom de personne, aucun nom de machine, aucun jeton.

Date du relevé : …

## Poste

Sortie de `python -m scripts.verifier_poste`, dans l'environnement `.venv-data` activé :

| Élément | Valeur |
|---|---|
| Système | … |
| Architecture | … |
| Processeur | … |
| Mémoire | … |
| Python (environnement actif) | … |
| Git | … |
| Node.js | … |
| npm | … |
| VS Code | … |

| Élément | Commande | Valeur |
|---|---|---|
| uv | `uv --version` | … |
| GitHub CLI | `gh --version` (première ligne) | … |
| Espace disque libre | explorateur de fichiers ou `df -h .` | … |

## Accès

| Contrôle | Résultat attendu | Résultat |
|---|---|---|
| `gh auth status` | connecté à github.com, protocole https | … |
| `git config user.email` | adresse `…@users.noreply.github.com` | … |
| `python -m scripts.tester_hf` | « Appel whoami réussi », rôle du jeton `read` ou `fineGrained`, téléchargement réussi | … |

## Volet A (site en local)

| Contrôle | Résultat |
|---|---|
| `npm ci` dans `a3/` : dépendances installées sans erreur | … |
| `npm run build` : fichier `a3/dist/index.html` produit | … |
| `npm run dev` : la page s'affiche à l'adresse locale indiquée | … |
| Navigateur et version | … |

## Première génération locale (volet B)

À remplir dans une seconde pull request, après la fusion de la chaîne locale du volet B.

| Contrôle | Résultat |
|---|---|
| `python -m b1.scripts.installer_llama` : plateforme détectée, empreinte vérifiée | … |
| `python -m b1.scripts.telecharger_modeles` : empreintes vérifiées | … |
| `python -m b1.scripts.lancer_serveur` : message « Serveur prêt » | … |

Sortie de `python -m b1.scripts.generer_essai` :

| Élément | Valeur |
|---|---|
| Build llama.cpp | … |
| Modèle | … |
| Question | … |
| Réponse | … |
| Vitesse de génération | … |

Mémoire utilisée par `llama-server` pendant la génération (Gestionnaire des tâches, Moniteur d'activité ou `top`) : …

## Écarts et problèmes rencontrés

| Problème | Cause | Solution appliquée |
|---|---|---|
| … | … | … |
