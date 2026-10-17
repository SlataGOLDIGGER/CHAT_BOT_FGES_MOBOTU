"""Interface locale du volet B (Streamlit) : question, réponse sourcée ou abstention, sources consultables.

Lancement (serveur llama.cpp déjà lancé dans un autre terminal) :
  streamlit run b1/app/app.py --server.address 127.0.0.1 --server.headless true \
    --browser.gatherUsageStats false --client.toolbarMode minimal
"""
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))  # Streamlit exécute ce fichier comme un script : on rend le dépôt importable.

import requests  # noqa: E402
import streamlit as st  # noqa: E402

from b1.rag.client_llm import etat_serveur  # noqa: E402
from b1.rag.pipeline import charger_config, repondre  # noqa: E402
from b1.rag.recherche import Recherche  # noqa: E402

st.set_page_config(page_title="Assistant stages — réponses sourcées", layout="wide")


@st.cache_resource
def moteur(strategie: str) -> Recherche:
    return Recherche(strategie)


config = charger_config()
st.title("Assistant stages : réponses sourcées")
st.caption("Réponses générées localement à partir des seules fiches Service-Public du corpus. "
           "Chaque phrase cite sa source ; sans source suffisante, l'assistant s'abstient.")

try:
    serveur = etat_serveur()
except requests.ConnectionError:
    st.error("Le serveur local n'est pas lancé. Dans un autre terminal : python -m b1.scripts.lancer_serveur")
    st.stop()

with st.sidebar:
    st.subheader("Configuration chargée")
    st.write(f"Moteur : llama.cpp {serveur['build']}")
    st.write(f"Modèle : {pathlib.Path(serveur['modele']).name} ({serveur['quantification']})")
    st.write(f"Récupération : {config['strategie']}, {config['k']} passages")
    echelle = None
    if serveur["adaptateurs"]:
        active = st.toggle("Adaptateur activé", value=True)
        echelle = 1.0 if active else 0.0
        st.write(f"Adaptateur : {pathlib.Path(serveur['adaptateurs'][0]['path']).name}")
    else:
        st.write("Adaptateur : aucun (modèle de base)")
    st.info("Outil expérimental : il ne remplace ni la fiche officielle ni un conseil personnalisé.")

question = st.text_area("Votre question sur les stages", max_chars=300,
                        placeholder="Ex. : mon stage de trois mois doit-il être payé ?")
if st.button("Répondre", type="primary", disabled=not question.strip()):
    with st.spinner("Recherche des passages et génération locale…"):
        resultat = repondre(question.strip(), moteur(config["strategie"]), config, echelle)
    if resultat["abstention"]:
        st.warning(resultat["reponse"])
        st.caption(f"Motif de l'abstention : {resultat['motif']}")
    else:
        st.success(resultat["reponse"])
    cites = set(resultat["analyse"]["cites"]) if resultat["analyse"] else set()
    st.caption(f"Temps total : {resultat['duree_s']} s")
    st.subheader("Passages fournis au modèle")
    for source in resultat["sources"]:
        marque = "cité" if int(source["label"][1:]) in cites else "non cité"
        with st.expander(f"[{source['label']}] {marque} · score {source['score']:.3f} · {source['reference']}"):
            st.write(source["texte"].split("\n", 1)[-1])
            st.markdown(f"[Lire la fiche complète]({source['url']})")