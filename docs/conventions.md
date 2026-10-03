# Conventions de travail

## Clés de tickets

Le board est le projet Jira `MOBOTU`. La clé d'un ticket est de la forme `MOBOTU-<numéro>` : c'est elle qui va dans les noms de branche, les messages de commit et les titres de pull request. Chaque ticket rappelle en tête de sa description son identifiant interne de planification, qui sert uniquement à retrouver la tâche dans la documentation de travail.

## Branches

Nous suivons un flux simple : une branche principale `main`, toujours déployable, et une branche courte par ticket, créée depuis `main` à jour et supprimée après fusion.

- Nom : `MOBOTU-<numéro>-<mots-clés-en-minuscules>`, par exemple `MOBOTU-33-extraction-sections`.
- Branches de consultation pour l'enseignant : `consultation/mi-parcours`, `consultation/j3`, `consultation/j4`, créées sur le commit du tag de jalon et jamais modifiées ensuite.

## Commits

- Message : `MOBOTU-<numéro> <verbe à l'infinitif> <objet>`, 72 caractères au plus pour la première ligne, par exemple `MOBOTU-33 Extraire les sections et les cas conditionnels`. Un paragraphe facultatif explique le pourquoi.
- Un commit correspond à un changement cohérent et vérifiable ; pas de commit « divers ».
- Poussée au moins à la fin de chaque séance de travail.
- Identité Git : identifiant GitHub et adresse privée fournie par GitHub (`…@users.noreply.github.com`). Aucun nom de personne dans le dépôt, les messages ou les pull requests.

## Pull requests

- Titre : `MOBOTU-<numéro> <titre du ticket>`.
- Description selon le gabarit `.github/pull_request_template.md` : ticket, changements, sortie de la vérification, liste de contrôle.
- Relecture obligatoire par le binôme du responsable ; une approbation au moins avant fusion ; les commentaires sont résolus avant fusion.
- Contrôles automatiques : le contrôle « verifications » (secrets, poids, intégrité du corpus, questions) et la préversion Vercel pour le site.
- Fusion par l'auteur après approbation, méthode « Squash and merge » : un commit par ticket sur `main`, dont l'auteur est celui de la pull request. Suppression de la branche après fusion.

## Tags

- Jalons : `jalon-mi-parcours`, `jalon-j3`, `jalon-j4` (tags annotés sur `main`).
- Étapes figées : `corpus-v2`, `b1-config-gelee`, `site-gele`.

## Fichiers jamais versionnés

Secrets et jetons ; poids de modèles (`.gguf`, `.onnx`, `.safetensors`…) et binaires du moteur ; environnements virtuels et `node_modules/` ; sorties de `artifacts/` ; fichier du test scellé, ses sorties et ses feuilles d'annotation. Le fichier `.gitignore` et le contrôle `python -m scripts.verifier_depot` appliquent ces règles.

## Mode opératoire pas à pas

On ne travaille jamais directement sur `main` : chaque tâche se fait sur sa propre branche, puis passe par une pull request relue avant d'arriver sur `main`.

1. Cloner le dépôt (une seule fois) :

   ```bash
   git clone https://github.com/SlataGOLDIGGER/CHAT_BOT_FGES_MOBOTU.git
   cd CHAT_BOT_FGES_MOBOTU
   ```

2. Se placer sur sa branche.
   - Nouvelle tâche : partir de `main` à jour, puis créer la branche avec le nom indiqué dans la fiche de la tâche (forme `MOBOTU-<numéro>-<mots-clés>`) :

     ```bash
     git switch main
     git pull                                # mettre à jour votre branche main locale avec la version de GitHub
     git switch -c MOBOTU-<numéro>-<mots-clés>
     ```

   - Tâche déjà commencée (la branche existe déjà) :

     ```bash
     git fetch                               # récupérer depuis GitHub les nouveautés (branches, commits), sans toucher à vos fichiers
     git switch MOBOTU-<numéro>-<mots-clés>
     git pull                                # si la branche a déjà été poussée : mettre à jour votre branche locale avec la version de GitHub
     ```

3. Vérifier que vous êtes sur votre branche : `git branch --show-current` doit afficher le nom de votre branche, et non `main`.

4. Faire votre travail, puis valider uniquement vos fichiers, sur votre branche :

   ```bash
   git status                        # vérifier la branche et les fichiers modifiés
   git add <fichier1> <fichier2>     # les fichiers exacts, pas « git add . »
   git commit -m "MOBOTU-<numéro> <Verbe à l'infinitif> <objet>"
   ```

5. Pousser votre branche :
   - la première fois : `git push -u origin MOBOTU-<numéro>-<mots-clés>`
   - les fois suivantes : `git push`

6. Faire relire votre travail, puis le fusionner sur `main` par une pull request.

   Ne fusionnez jamais sur `main` sans relecture, et ne faites jamais de `git merge` ni de `git push` sur `main` depuis votre poste. Une pull request est une **demande** de fusion : elle propose d'ajouter les commits de votre branche dans `main`, mais ne fusionne rien par elle-même. La fusion n'a lieu qu'après la relecture, par un bouton sur le site de GitHub.

   Si vous avez un doute sur votre travail, faites-le contrôler par un agent IA avant de créer la pull request.

   - **Créer la pull request, depuis votre branche** (pas depuis `main`), une fois tous vos commits poussés (étape 5) :

     ```bash
     git branch --show-current               # doit afficher MOBOTU-<numéro>-<mots-clés>, et non main
     git status                              # doit indiquer « nothing to commit » et « up to date with 'origin/MOBOTU-…' »
     gh pr create --web                      # ouvrir dans le navigateur la page de création de la pull request
     ```

     `gh` est l'outil en ligne de commande de GitHub : installez-le, puis lancez `gh auth login` une seule fois pour le relier à votre compte. `gh pr create` prend la branche sur laquelle vous vous trouvez comme branche à fusionner, et `main` comme branche d'arrivée : c'est pour cela qu'il faut être sur votre branche.

     Sans `gh` : sur la page du dépôt GitHub, cliquez sur le bouton **Compare & pull request** qui apparaît après votre `git push`, ou sur **Pull requests** → **New pull request**, puis choisissez `base: main` et `compare: MOBOTU-<numéro>-<mots-clés>`.

   - **Remplir la pull request.** Sur la page qui s'ouvre, vérifiez en haut `base: main ← compare: MOBOTU-<numéro>-<mots-clés>`. Donnez un titre (`MOBOTU-<numéro> <titre de la tâche>`), décrivez ce que vous avez fait, ajoutez dans **Reviewers** (colonne de droite) votre binôme ou au moins une ou deux autres personnes du projet, puis cliquez sur **Create pull request**.

   - **Relecture.** Les relecteurs ouvrent la pull request, lisent les changements dans l'onglet **Files changed**, puis cliquent sur **Review changes** et choisissent **Approve** (approuver) ou **Request changes** (demander des corrections). Pour corriger, restez sur votre branche, modifiez vos fichiers, puis `git add`, `git commit` et `git push` comme aux étapes 4 et 5 : la pull request se met à jour toute seule, inutile d'en créer une autre.

   - **Fusionner, seulement après approbation.** Sur la page de la pull request, cliquez sur **Squash and merge**, puis **Confirm squash and merge**, puis **Delete branch**. Si le bouton affiche **Merge pull request**, choisissez **Squash and merge** avec la flèche à côté. « Squash and merge » regroupe tous les commits de votre branche en un seul commit sur `main`. **Delete branch** supprime la branche sur GitHub, pas sur votre poste.

   - **Après la fusion**, sur votre poste :

     ```bash
     git switch main
     git pull                                # mettre à jour votre branche main locale : elle reçoit le commit que vous venez de fusionner
     git branch -D MOBOTU-<numéro>-<mots-clés>  # supprimer la branche terminée sur votre poste
     ```

     Pour la tâche suivante, recommencez à l'étape 2 avec une nouvelle branche : ne continuez pas à travailler sur une branche déjà fusionnée.
