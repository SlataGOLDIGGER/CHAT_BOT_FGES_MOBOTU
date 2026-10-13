"""Contrôle automatique des citations et détection de l'abstention."""

import re

from b1.rag.prompt import ABSTENTION

MOTIF = re.compile(r"\[S(\d+)\]")


def normaliser(texte: str) -> str:
    return re.sub(r"\s+", " ", texte).strip().rstrip(".").lower()


def est_abstention(texte: str) -> bool:
    return normaliser(ABSTENTION) in normaliser(texte)


def analyser(texte: str, nb_passages: int) -> dict:
    """Numéros cités, citations valides (présentes dans le contexte fourni) et invalides."""
    cites = [int(n) for n in MOTIF.findall(texte)]
    valides = sorted({n for n in cites if 1 <= n <= nb_passages})
    invalides = sorted({n for n in cites if not 1 <= n <= nb_passages})
    phrases = [p for p in re.split(r"(?<=[.!?])\s+", texte.strip()) if p]
    sans_citation = [p for p in phrases if not MOTIF.search(p)]
    return {
        "cites": valides,
        "invalides": invalides,
        "phrases": len(phrases),
        "phrases_sans_citation": len(sans_citation),
        "abstention": est_abstention(texte),
    }
