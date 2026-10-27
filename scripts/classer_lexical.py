"""Références lexicales (BM25 et TF-IDF) : classement des passages pour chaque question.

Usage : python -m scripts.classer_lexical --methode bm25 --strategie paragraphe \
          --questions shared/eval/questions_dev.jsonl --sortie artifacts/a3/classements/bm25-paragraphe-dev.jsonl
"""
import argparse
import json
import pathlib
import re
import unicodedata

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

RACINE = pathlib.Path(__file__).resolve().parents[1]
MOTS_VIDES = set("""a au aux avec ce ces cet cette d dans de des du elle en est et etre il ils je l la le les leur
lui mais me meme mes n ne ni nos notre nous on ou par pas pour qu que qui s sa se ses si son sont sur ta te tes
toi ton tu un une vos votre vous y""".split())


def jetons(texte: str) -> list[str]:
    """Minuscules, accents retirés, mots vides supprimés : la même normalisation pour questions et passages."""
    sans_accents = unicodedata.normalize("NFKD", texte.lower()).encode("ascii", "ignore").decode()
    return [m for m in re.findall(r"[a-z0-9]+", sans_accents) if m not in MOTS_VIDES]


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--methode", choices=["bm25", "tfidf"], required=True)
    parser.add_argument("--strategie", choices=["section", "fenetre", "paragraphe"], required=True)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--profondeur", type=int, default=50)
    args = parser.parse_args()

    passages = lire_jsonl(RACINE / "shared" / "corpus" / f"passages_{args.strategie}.jsonl")
    questions = lire_jsonl(pathlib.Path(args.questions).expanduser())
    documents = [jetons(p["texte"]) for p in passages]
    if args.methode == "bm25":
        modele = BM25Okapi(documents)
        scores = [modele.get_scores(jetons(q["question"])) for q in questions]
    else:
        vectoriseur = TfidfVectorizer(analyzer=lambda x: x, sublinear_tf=True)
        matrice = vectoriseur.fit_transform(documents)
        requetes = vectoriseur.transform([jetons(q["question"]) for q in questions])
        scores = list((requetes @ matrice.T).toarray())
    sortie = pathlib.Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    combinaison = f"{args.methode}/{args.strategie}"
    with open(sortie, "w", encoding="utf-8", newline="\n") as fichier:
        for q, s in zip(questions, scores):
            ordre = np.argsort(-np.asarray(s), kind="stable")[: args.profondeur]
            classement = [{"passage_id": passages[i]["passage_id"], "section_id": passages[i]["section_id"],
                           "score": float(s[i])} for i in ordre]
            fichier.write(json.dumps({"qid": q["qid"], "combinaison": combinaison, "classement": classement},
                                     ensure_ascii=False) + "\n")
    print(f"{len(questions)} questions classées ({combinaison}) -> {sortie}")


if __name__ == "__main__":
    main()
