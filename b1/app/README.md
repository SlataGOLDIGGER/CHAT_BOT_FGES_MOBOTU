# b1/app — interface locale

`app.py` est une interface Streamlit sur une seule page. Un bandeau rappelle le principe de l'outil et ses limites. En dessous, la colonne de gauche contient la question puis la réponse sourcée, ou l'abstention avec son motif. La colonne de droite montre les passages fournis au modèle, ceux cités dans la réponse en premier, chacun avec son score, sa référence et le lien vers la fiche. La barre latérale, repliée au départ, donne l'état du serveur local (build, modèle, adaptateur) et l'interrupteur d'activation de l'adaptateur.

Lancement depuis la racine, serveur local déjà démarré :

```bash
streamlit run b1/app/app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --client.toolbarMode minimal
```

Puis ouvrir l'adresse affichée (`http://127.0.0.1:8501`). L'option `--server.address 127.0.0.1` limite l'accès au poste lui-même ; `--server.headless true` supprime la demande d'adresse électronique du premier lancement et l'ouverture automatique du navigateur ; `--browser.gatherUsageStats false` désactive l'envoi de statistiques d'usage à Streamlit.

## Apparence

La page suit le réglage clair ou sombre du système. Le menu de Streamlit, qui permettrait de changer de thème, est masqué par `--client.toolbarMode minimal`. Les fichiers de l'apparence sont rangés à côté de `app.py`, où Streamlit les trouve sans option de lancement supplémentaire.

| Fichier | Rôle |
|---|---|
| `.streamlit/config.toml` | couleurs claires et sombres (palette « Lin & cuivre »), police, arrondis ; active le service des fichiers de `static/` |
| `static/style.css` | retouches légères : bandeau, cartes, bouton, liens, passages cités |
| `static/fonts/` | police Inter servie par l'application elle-même (licence SIL Open Font License 1.1, texte complet dans `LICENSE-Inter-OFL.txt`) |
| `static/illustration-clair.png`, `static/illustration-sombre.png` | illustration du bandeau, une version par thème |

Les règles de `style.css` visent surtout les classes que Streamlit pose à partir des clés des éléments (`st-key-…`). Les quelques sélecteurs internes à Streamlit (`data-testid`) sont à revérifier après une mise à jour.
