"""Métriques de recherche au niveau des sections : Recall@k, MRR@10, nDCG@10, avec intervalles bootstrap.

Usage :
  python -m scripts.evaluer_recherche --questions shared/eval/questions_dev.jsonl --classement FICHIER.jsonl
  ... --comparer AUTRE.jsonl       (différence appariée de nDCG@10, intervalle bootstrap à 95 %)
  ... --journal docs/resultats/A3_recherche.csv   (ajoute une ligne de résultats versionnable)
"""
import argparse
import csv
import datetime
import json
import math
import pathlib

import numpy as np

KS = (1, 3, 5, 10)
TIRAGES = 2000


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def sections_classees(classement: list[dict]) -> list[str]:
    """Plusieurs passages d'une même section comptent une fois, au rang de leur meilleur passage."""
    vues, ordre = set(), []
    for element in classement:
        if element["section_id"] not in vues:
            vues.add(element["section_id"])
            ordre.append(element["section_id"])
    return ordre


def mesures_question(ordre: list[str], pertinentes: set[str]) -> dict:
    resultat = {f"R@{k}": len(pertinentes & set(ordre[:k])) / len(pertinentes) for k in KS}
    rang = next((i + 1 for i, s in enumerate(ordre[:10]) if s in pertinentes), None)
    resultat["MRR@10"] = 1 / rang if rang else 0.0
    gain = sum(1 / math.log2(i + 2) for i, s in enumerate(ordre[:10]) if s in pertinentes)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(pertinentes), 10)))
    resultat["nDCG@10"] = gain / ideal
    return resultat


def par_question(questions: list[dict], classements: dict) -> dict:
    return {q["qid"]: mesures_question(sections_classees(classements[q["qid"]]), set(q["sections_or"]))
            for q in questions if q["dans_corpus"]}


def intervalle(valeurs: np.ndarray, graine: int = 0) -> tuple[float, float]:
    tirages = np.random.default_rng(graine).choice(valeurs, size=(TIRAGES, len(valeurs)), replace=True).mean(axis=1)
    return float(np.percentile(tirages, 2.5)), float(np.percentile(tirages, 97.5))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True)
    parser.add_argument("--classement", required=True)
    parser.add_argument("--comparer")
    parser.add_argument("--journal")
    args = parser.parse_args()

    questions = lire_jsonl(pathlib.Path(args.questions).expanduser())
    lignes = lire_jsonl(pathlib.Path(args.classement))
    classements = {l["qid"]: l["classement"] for l in lignes}
    manquantes = [q["qid"] for q in questions if q["qid"] not in classements]
    if manquantes:
        raise SystemExit(f"ERREUR : {len(manquantes)} questions sans classement, par exemple {manquantes[:3]}")
    detail = par_question(questions, classements)
    moyennes = {m: float(np.mean([d[m] for d in detail.values()])) for m in next(iter(detail.values()))}
    bas, haut = intervalle(np.array([d["nDCG@10"] for d in detail.values()]))
    combinaison = lignes[0]["combinaison"]
    print(f"{combinaison} sur {len(detail)} questions répondables :")
    print(" | ".join(f"{m} {v:.3f}" for m, v in moyennes.items()) + f" | IC95 nDCG@10 [{bas:.3f} ; {haut:.3f}]")

    if args.comparer:
        autres = {l["qid"]: l["classement"] for l in lire_jsonl(pathlib.Path(args.comparer))}
        detail_b = par_question(questions, autres)
        ecarts = np.array([detail_b[q]["nDCG@10"] - detail[q]["nDCG@10"] for q in detail])
        b_bas, b_haut = intervalle(ecarts)
        print(f"Écart apparié nDCG@10 ({args.comparer} moins {args.classement}) : {ecarts.mean():+.3f} "
              f"[{b_bas:+.3f} ; {b_haut:+.3f}] ; meilleur sur {int((ecarts > 0).sum())} questions, "
              f"moins bon sur {int((ecarts < 0).sum())}")

    if args.journal:
        journal = pathlib.Path(args.journal)
        nouveau = not journal.exists()
        journal.parent.mkdir(parents=True, exist_ok=True)
        with open(journal, "a", encoding="utf-8", newline="") as fichier:
            ecrivain = csv.writer(fichier)
            if nouveau:
                ecrivain.writerow(["date", "combinaison", "questions", "n", *moyennes.keys(), "ic95_ndcg_bas",
                                   "ic95_ndcg_haut"])
            ecrivain.writerow([datetime.date.today().isoformat(), combinaison, pathlib.Path(args.questions).name,
                               len(detail), *(f"{v:.4f}" for v in moyennes.values()), f"{bas:.4f}", f"{haut:.4f}"])
        print(f"Ligne ajoutée à {journal}")


if __name__ == "__main__":
    main()
