# b1 — application locale du volet B (assistant réglementaire sourcé)

Le système répond en français aux questions sur les stages à partir des seuls passages récupérés dans le corpus, cite chaque source sous la forme `[S1]`, `[S2]`…, et s'abstient lorsque les passages ne contiennent pas l'information. Tout s'exécute sur le poste : aucune API d'inférence distante.

| Dossier | Rôle |
|---|---|
| `config/` | révisions figées des modèles et du moteur (`models.lock.json`), réglages du RAG (`rag.json`) |
| `scripts/` | installation du moteur llama.cpp, téléchargement vérifié des modèles, lancement du serveur local, preuves de fonctionnement |
| `rag/` | récupération, gabarit de prompt, client du serveur local, contrôle des citations, chaîne complète |
| `app/` | interface Streamlit |
| `eval/` | exécution sur un jeu de questions, métriques automatiques, annotation humaine en aveugle |
| `training/` | données d'adaptation supervisée et script QLoRA exécuté sur GPU distant gratuit |
| `models/`, `runtime/` | poids et binaires téléchargés, jamais versionnés |

La chaîne est identique sous Windows, Linux et macOS ; sur Mac, llama.cpp utilise automatiquement le GPU par Metal. L'architecture est décrite dans `docs/architecture_B1.md`.
