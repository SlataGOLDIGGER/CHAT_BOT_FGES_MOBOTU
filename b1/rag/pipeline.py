"""Chaîne RAG complète du volet B : récupération, génération locale, contrôle des citations, abstention."""

import json
import pathlib
import time

from b1.rag.citations import analyser
from b1.rag.client_llm import generer
from b1.rag.prompt import ABSTENTION, construire_prompt
from b1.rag.recherche import Recherche

RACINE = pathlib.Path(__file__).resolve().parents[2]


def charger_config() -> dict:
    return json.loads(
        (RACINE / "b1" / "config" / "rag.json").read_text(encoding="utf-8")
    )


def repondre(
    question: str, recherche: Recherche, config: dict, echelle_lora: float | None = None
) -> dict:
    debut = time.perf_counter()
    resultats = recherche.chercher(question, config["k"])
    sources = [
        {
            "label": f"S{rang}",
            "passage_id": p["passage_id"],
            "section_id": p["section_id"],
            "score": round(score, 4),
            "reference": p["reference"],
            "url": p["url"],
            "texte": p["texte"],
        }
        for rang, (p, score) in enumerate(resultats, start=1)
    ]
    sortie = {
        "question": question,
        "sources": sources,
        "score_max": sources[0]["score"],
        "brut": None,
        "analyse": None,
        "generation": None,
    }
    if sources[0]["score"] < config["seuil_score"]:
        sortie.update(reponse=ABSTENTION, abstention=True, motif="score_insuffisant")
    else:
        generation = generer(
            construire_prompt(question, [p for p, _ in resultats]), echelle_lora
        )
        analyse = analyser(generation["texte"], len(sources))
        sortie.update(brut=generation["texte"], analyse=analyse, generation=generation)
        if analyse["abstention"]:
            sortie.update(reponse=ABSTENTION, abstention=True, motif="modele")
        elif not analyse["cites"]:
            sortie.update(
                reponse=ABSTENTION, abstention=True, motif="reponse_non_sourcee"
            )
        else:
            sortie.update(reponse=generation["texte"], abstention=False, motif=None)
    sortie["duree_s"] = round(time.perf_counter() - debut, 3)
    return sortie
