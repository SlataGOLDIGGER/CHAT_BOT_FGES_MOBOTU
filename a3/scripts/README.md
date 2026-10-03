# a3/scripts — construction de l'index statique

`construire-index.mjs` lit `shared/corpus/passages_*.jsonl`, `sections.jsonl` et `manifest.json`, encode chaque passage avec le même code et le même modèle que le navigateur (un passage à la fois), puis écrit dans `a3/public/data/` :

- `index.json` : combinaisons disponibles, clés d'invalidation, périmètre, attribution ;
- `passages-<stratégie>-<empreinte>.json` : textes affichés, références et liens ;
- `vecteurs-<modèle>-<stratégie>-<empreinte>.bin` : vecteurs Float32 normalisés.

Commande : `npm run index` depuis `a3/`.
