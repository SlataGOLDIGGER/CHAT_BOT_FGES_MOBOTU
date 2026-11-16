"""Construit les exemples d'adaptation supervisée (prompt, complétion) à partir des questions et du RAG.

Usage : python -m b1.training.construire_sft
Sorties : b1/training/donnees/sft_train.jsonl et sft_dev.jsonl
Les prompts sont produits par la même fonction qu'à l'inférence (b1/rag/prompt.py).
"""
import hashlib
import json
import pathlib
import re

from b1.rag.pipeline import charger_config
from b1.rag.prompt import ABSTENTION, construire_prompt
from b1.rag.recherche import Recherche, lire_jsonl

RACINE = pathlib.Path(__file__).resolve().parents[2]
CITATION = re.compile(r"\[(F\d+-[^\]\s]+)\]")
FIN = "<|im_end|>"


def tirage(identifiant: str) -> float:
    """Nombre pseudo-aléatoire reproductible dans [0, 1[ tiré de l'identifiant."""
    return int(hashlib.sha256(identifiant.encode()).hexdigest()[:8], 16) / 2**32


def meilleur_passage(recherche: Recherche, question: str, section_id: str) -> dict:
    candidats = [(p, s) for p, s in recherche.chercher(question, len(recherche.passages))
                 if p["section_id"] == section_id]
    return candidats[0][0]



def contexte_avec_or(recherche, question, sections_citees, k):
    """Top-k récupéré, complété si besoin pour contenir un passage de chaque section citée."""
    contexte = [p for p, _ in recherche.chercher(question, k)]
    for section in sections_citees:
        if any(p["section_id"] == section for p in contexte):
            continue
        passage = meilleur_passage(recherche, question, section)

        remplacables = [
            i for i, p in enumerate(contexte)
            if p["section_id"] not in sections_citees
        ]
        if remplacables:
            contexte[remplacables[-1]] = passage
        else:
            contexte.append(passage)

    return contexte



def contexte_sans_or(recherche, question, sections_or, k):
    """Les k meilleurs passages qui n'appartiennent à aucune section d'or."""
    return [p for p, _ in recherche.chercher(question, len(recherche.passages))
            if p["section_id"] not in sections_or][:k]


def cible(reponse_ref: str, contexte: list[dict]) -> str:
    """Remplace chaque [section] de la réponse de référence par l'étiquette [Sn] du contexte."""
    def remplacer(m):
        for rang, p in enumerate(contexte, start=1):
            if p["section_id"] == m.group(1):
                return f"[S{rang}]"
        raise ValueError(f"section {m.group(1)} absente du contexte")
    return CITATION.sub(remplacer, reponse_ref)


def exemples(question: dict, recherche: Recherche, k: int) -> list[dict]:
    q = question["question"]
    if not question["dans_corpus"]:
        contexte = [p for p, _ in recherche.chercher(q, k)]
        return [{"id": question["qid"], "type": "abstention_hors_corpus",
                 "prompt": construire_prompt(q, contexte), "completion": ABSTENTION + FIN}]
    citees = list(dict.fromkeys(CITATION.findall(question["reponse_ref"])))
    contexte = contexte_avec_or(recherche, q, citees, k)
    sortie = [{"id": question["qid"], "type": "reponse", "prompt": construire_prompt(q, contexte),
               "completion": cible(question["reponse_ref"], contexte) + FIN}]
    if tirage(question["qid"]) < 0.5:
        sans_or = contexte_sans_or(recherche, q, set(question["sections_or"]), k)
        sortie.append({"id": question["qid"] + "-sans-or", "type": "abstention_contexte",
                       "prompt": construire_prompt(q, sans_or), "completion": ABSTENTION + FIN})
    return sortie


def main() -> None:
    config = charger_config()
    recherche = Recherche(config["strategie"])
    dossier = RACINE / "b1" / "training" / "donnees"
    dossier.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev"):
        questions = lire_jsonl(RACINE / "shared" / "eval" / f"questions_{split}.jsonl")
        lignes = [e for q in questions for e in exemples(q, recherche, config["k"])]
        with open(dossier / f"sft_{split}.jsonl", "w", encoding="utf-8", newline="\n") as sortie:
            for ligne in lignes:
                sortie.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        types = {t: sum(1 for l in lignes if l["type"] == t) for t in
                 ("reponse", "abstention_hors_corpus", "abstention_contexte")}
        print(f"{split} : {len(lignes)} exemples {types} -> b1/training/donnees/sft_{split}.jsonl")


if __name__ == "__main__":
    main()