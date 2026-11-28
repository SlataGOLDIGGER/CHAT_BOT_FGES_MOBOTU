"""Interface locale du volet B (Streamlit) : question, réponse sourcée ou abstention, sources consultables.

Lancement (serveur llama.cpp déjà lancé dans un autre terminal) :
  streamlit run b1/app/app.py --server.address 127.0.0.1 --server.headless true \
    --browser.gatherUsageStats false --client.toolbarMode minimal

Le thème (couleurs claires et sombres, police) est dans b1/app/.streamlit/config.toml ;
les retouches CSS, les polices et l'illustration du bandeau sont dans b1/app/static/.
"""
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))  # Streamlit exécute ce fichier comme un script : on rend le dépôt importable.

import requests  # noqa: E402
import streamlit as st  # noqa: E402

from b1.rag.citations import MOTIF  # noqa: E402
from b1.rag.client_llm import etat_serveur  # noqa: E402
from b1.rag.pipeline import charger_config, repondre  # noqa: E402
from b1.rag.recherche import Recherche  # noqa: E402

DOSSIER = pathlib.Path(__file__).resolve().parent
MOTIFS = {
    "score_insuffisant": "aucun passage n'est assez proche de la question",
    "modele": "le modèle a jugé que les passages ne permettent pas de répondre",
    "reponse_non_sourcee": "la réponse produite ne citait aucun passage, elle a été écartée",
}

st.set_page_config(page_title="Assistant stages — réponses sourcées", layout="wide",
                   initial_sidebar_state="collapsed")
st.html(DOSSIER / "static" / "style.css")


@st.cache_resource
def moteur(strategie: str) -> Recherche:
    return Recherche(strategie)


def nombre_fr(valeur: float, decimales: int) -> str:
    """Nombre écrit avec une virgule : 1.267 donne « 1,27 » avec deux décimales."""
    return f"{valeur:.{decimales}f}".replace(".", ",")


def secondes(valeur: float) -> str:
    """Durée lisible : deux décimales, trois sous 0,1 s (abstention décidée avant toute génération)."""
    return f"{nombre_fr(valeur, 2 if valeur >= 0.1 else 3)} s"


def pluriel(n: int, mot: str) -> str:
    return mot + ("s" if n > 1 else "")


def echapper(texte: str) -> str:
    """Neutralise les caractères Markdown d'un titre avant de l'insérer dans un libellé."""
    return re.sub(r"([\\`*_\[\]<>#|~$])", r"\\\1", texte)


def badges(texte: str, nb_passages: int) -> str:
    """Remplace [S2] par un badge couleur accent, seulement pour les passages fournis (S1…Sk)."""
    def remplacer(m: re.Match) -> str:
        return f" :orange-badge[S{m.group(1)}]" if 1 <= int(m.group(1)) <= nb_passages else m.group(0)
    return MOTIF.sub(remplacer, texte)


def libelle(source: dict) -> str:
    """`S1` **Fiche** › *Section › Sous-section* ; la section peut être absente."""
    fiche, *chemin = source["reference"].split(" › ")
    titre = f"`{source['label']}` **{echapper(fiche)}**"
    return f"{titre} › *{echapper(' › '.join(chemin))}*" if chemin else titre


def afficher_passage(source: dict, ouvert: bool, cle: str) -> None:
    with st.expander(libelle(source), expanded=ouvert, key=cle):
        st.write(source["texte"].split("\n", 1)[-1])
        st.markdown(f":gray[Score de similarité : {nombre_fr(source['score'], 3)}]")
        st.markdown(f"[Lire la fiche sur service-public.fr]({source['url']})")


config = charger_config()

# Bandeau : couleurs et illustration suivent le thème actif (clair si le navigateur ne l'a pas encore indiqué).
sombre = st.context.theme.type == "dark"
st.html(f"""
<div class="as-bandeau{' as-bandeau-sombre' if sombre else ''}">
  <div class="as-bandeau-texte">
    <h1>Assistant stages&nbsp;: réponses sourcées</h1>
    <p>Réponses générées localement à partir des seules fiches Service-Public du corpus.
      Chaque phrase cite sa source&nbsp;; sans source suffisante, l'assistant s'abstient.</p>
    <p class="as-bandeau-avertissement">Outil expérimental&nbsp;: il ne remplace ni la fiche officielle
      ni un conseil personnalisé.</p>
  </div>
  <img src="app/static/illustration-{'sombre' if sombre else 'clair'}.png" alt="">
</div>
""")

try:
    serveur = etat_serveur()
except requests.ConnectionError:
    st.error("Le serveur local n'est pas lancé. Dans un autre terminal : python -m b1.scripts.lancer_serveur")
    st.stop()

with st.sidebar:
    st.subheader("Détails techniques", anchor=False)
    st.markdown(f":gray[Moteur]  \nllama.cpp {serveur['build']}")
    st.markdown(f":gray[Modèle]  \n{pathlib.Path(serveur['modele']).name} ({serveur['quantification']})")
    st.markdown(f":gray[Récupération]  \n{config['strategie']}, {config['k']} passages")
    echelle = None
    if serveur["adaptateurs"]:
        active = st.toggle("Adaptateur activé", value=True)
        echelle = 1.0 if active else 0.0
        st.markdown(f":gray[Adaptateur]  \n{pathlib.Path(serveur['adaptateurs'][0]['path']).name}")
    else:
        st.markdown(":gray[Adaptateur]  \naucun (modèle de base)")
    details = st.container()  # durée exacte et motif de la dernière réponse, remplis plus bas

col_question, col_sources = st.columns(2, gap="large")

with col_question:
    with st.container(border=True, key="question"):
        c_texte, c_bouton = st.columns([2, 1], vertical_alignment="bottom")
        question = c_texte.text_area("Votre question sur les stages", max_chars=300, height=74,
                                     placeholder="Ex. : mon stage de trois mois doit-il être payé ?")
        envoyer = c_bouton.button("Répondre", type="primary", key="repondre", width="stretch",
                                  icon=":material/arrow_forward:", icon_position="right",
                                  disabled=not question.strip())
    resultat = None
    if envoyer:
        with st.spinner("Recherche des passages et génération locale…"):
            resultat = repondre(question.strip(), moteur(config["strategie"]), config, echelle)

if resultat is not None:
    sources = resultat["sources"]
    cites = set(resultat["analyse"]["cites"]) if resultat["analyse"] else set()
    sources_citees = [s for s in sources if int(s["label"][1:]) in cites]
    sources_lues = [s for s in sources if int(s["label"][1:]) not in cites]
    duree = f"{secondes(resultat['duree_s'])} à partir de {len(sources)} passages."
    details.markdown(f":gray[Dernière réponse]  \n{nombre_fr(resultat['duree_s'], 3)} s")

with col_question:
    if resultat is None:
        with st.container(border=True, key="attente"):
            st.markdown(":gray[:material/forum:] **La réponse s'affichera ici**")
            st.markdown(":gray[Chaque phrase renverra au passage qui la justifie, par exemple] :orange-badge[S1]")
            st.markdown(":gray[Sans source suffisante, l'assistant le dira.]")
    elif resultat["abstention"]:
        with st.container(border=True, key="abstention"):
            st.markdown(":gray[:material/search_off:] **Pas de réponse sourcée**")
            st.markdown(resultat["reponse"])
            st.markdown(f":gray[Motif : {MOTIFS.get(resultat['motif'], resultat['motif'])}.]")
            st.markdown(":gray[Vous pouvez reformuler la question, ou chercher directement sur] "
                        "[service-public.fr](https://www.service-public.fr/)")
            st.caption(f"Traitée en {duree}")
        details.markdown(f":gray[Motif de l'abstention]  \n`{resultat['motif']}`")
    else:
        with st.container(border=True, key="reponse"):
            n = len(sources_citees)
            st.markdown(f":orange[:material/forum:] **Réponse** · "
                        f":gray[{n} {pluriel(n, 'source')} {pluriel(n, 'citée')}]")
            st.markdown(badges(resultat["reponse"], len(sources)))
            st.caption(f"Générée en {duree}")

with col_sources:
    st.subheader("Sources consultées", anchor=False)
    if resultat is None:
        with st.container(border=True, key="attente_sources"):
            st.markdown(":gray[Les passages lus par l'assistant s'afficheront ici, "
                        "ceux cités dans la réponse en premier.]")
    else:
        if resultat["abstention"]:
            st.markdown(f":gray[{len(sources)} passages lus par l'assistant, sans réponse sourcée.]")
        else:
            n = len(sources_citees)
            st.markdown(f":gray[{len(sources)} passages lus par l'assistant ; "
                        f"{n} {pluriel(n, 'cité')} dans la réponse.]")
        if sources_citees:
            groupe = pluriel(len(sources_citees), "Cité")
            groupe += " par le modèle" if resultat["abstention"] else " dans la réponse"
            st.markdown(f":orange[**{groupe}**]")
            for source in sources_citees:
                afficher_passage(source, True, f"cite_{source['label']}")
        if sources_lues:
            st.markdown(":gray[**Lus, non cités**]")
            for source in sources_lues:
                afficher_passage(source, False, f"lu_{source['label']}")
