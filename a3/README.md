# a3 — site du volet A (recherche sémantique)

Site statique construit avec Vite. L'inférence se fait dans le navigateur du visiteur : un Web Worker charge l'encodeur E5 quantifié avec Transformers.js, encode la question et la compare aux vecteurs des passages publiés avec le site.

| Élément | Rôle |
|---|---|
| `index.html` | structure de la page : périmètre, champ de recherche, états, résultats, pied de page |
| `src/` | interface, Web Worker et fonctions de recherche communes |
| `scripts/` | construction de l'index statique à partir du corpus |
| `public/data/` | index publié (généré par `npm run index`, versionné car servi par le site) |
| `training/` | affinage de l'encodeur par l'équipe, export ONNX et quantification (exécuté sur Kaggle) |
| `package.json`, `package-lock.json` | dépendances à versions exactes, installées par `npm ci` |
| `vite.config.js` | configuration de construction |
| `vercel.json` | construction et en-têtes HTTP sur Vercel |

Commandes (dans ce dossier) : `npm ci`, `npm run index`, `npm run dev`, `npm run build`, `npm run preview`.

Modes réservés à l'équipe : `?diagnostic` compare les vecteurs calculés par le navigateur à ceux de l'index ; `?evaluation` classe un fichier de questions dans le navigateur et télécharge le classement ; `?modele=…&strategie=…` sélectionne une autre combinaison publiée.
