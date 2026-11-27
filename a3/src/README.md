# a3/src — code du site

| Fichier | Rôle |
|---|---|
| `config.js` | configuration unique : modèles à révision figée, stratégies de découpage, combinaison de production, préfixes, nombre de résultats, seuil de pertinence |
| `moteur.js` | fonctions partagées par le navigateur et Node : création de l'extracteur, encodage d'un texte, classement par similarité cosinus, descripteur de la clé d'invalidation |
| `worker.js` | Web Worker : chargement de l'index et du modèle, recherche, modes évaluation et diagnostic |
| `main.js` | interface : périmètre, progression, résultats, états d'erreur, panneau d'évaluation |
| `theme.js` | bouton du bandeau (page de recherche et mentions) : mode clair ou sombre au choix, gardé dans le navigateur, sinon celui du système |
| `style.css` | mise en page responsive, contrastes, focus visible, modes clair et sombre |

Aucun texte du corpus n'est injecté comme HTML : l'affichage passe par `textContent`.
