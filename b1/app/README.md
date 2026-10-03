# b1/app — interface locale

`app.py` est une interface Streamlit : saisie de la question, réponse sourcée ou abstention (avec son motif), passages fournis au modèle avec leur score, leur référence et le lien vers la fiche, état du serveur local (build, modèle, adaptateur) et interrupteur d'activation de l'adaptateur.

Lancement depuis la racine, serveur local déjà démarré :

```bash
streamlit run b1/app/app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --client.toolbarMode minimal
```

Puis ouvrir l'adresse affichée (`http://127.0.0.1:8501`). L'option `--server.address 127.0.0.1` limite l'accès au poste lui-même ; `--server.headless true` supprime la demande d'adresse électronique du premier lancement et l'ouverture automatique du navigateur ; `--browser.gatherUsageStats false` désactive l'envoi de statistiques d'usage à Streamlit.
