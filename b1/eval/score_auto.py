"""Métriques automatiques d'une exécution du volet B, et comparaison appariée de deux exécutions.

Usage :
  python -m b1.eval.score_auto artifacts/b1/runs/dev-base
  python -m b1.eval.score_auto artifacts/b1/runs/dev-base --comparer artifacts/b1/runs/dev-adapte
"""
import argparse
import json
import pathlib

import numpy as np


def lire(dossier: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in (dossier / "sorties.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def indicateurs(sorties: list[dict]) -> dict:
    repondables = [s for s in sorties if s["dans_corpus"]]
    hors = [s for s in sorties if not s["dans_corpus"]]
    repondues = [s for s in repondables if not s["abstention"]]
    cites, appuyes, invalides = 0, 0, 0
    for s in repondues:
        par_label = {src["label"]: src["section_id"] for src in s["sources"]}
        for numero in s["analyse"]["cites"]:
            cites += 1
            appuyes += par_label[f"S{numero}"] in s["sections_or"]
        invalides += bool(s["analyse"]["invalides"])
    durees = np.array([s["duree_s"] for s in sorties])
    vitesses = [s["generation"]["tokens_generes"] / (s["generation"]["ms_generation"] / 1000)
                for s in sorties if s["generation"] and s["generation"]["ms_generation"]]
    return {
        "questions": len(sorties), "repondables": len(repondables), "hors_corpus": len(hors),
        "abstention_correcte": round(sum(s["abstention"] for s in hors) / max(len(hors), 1), 3),
        "faux_refus": round(sum(s["abstention"] for s in repondables) / max(len(repondables), 1), 3),
        "rappel_recuperation": round(sum(any(src["section_id"] in s["sections_or"] for src in s["sources"])
                                         for s in repondables) / max(len(repondables), 1), 3),
        "precision_citations": round(appuyes / cites, 3) if cites else None,
        "reponses_avec_citation_invalide": invalides,
        "converties_non_sourcees": sum(s["motif"] == "reponse_non_sourcee" for s in sorties),
        "latence_p50_s": round(float(np.percentile(durees, 50)), 2),
        "latence_p95_s": round(float(np.percentile(durees, 95)), 2),
        "tokens_par_s": round(float(np.mean(vitesses)), 1) if vitesses else None,
    }


def discordances(a: list[dict], b: list[dict]) -> dict:
    """Comptes appariés question par question (base de la comparaison avant/après)."""
    paires = {s["qid"]: s for s in a}
    hors_ab = hors_ba = refus_ab = refus_ba = 0
    for s in b:
        r = paires[s["qid"]]
        if not s["dans_corpus"]:
            hors_ab += r["abstention"] and not s["abstention"]
            hors_ba += s["abstention"] and not r["abstention"]
        else:
            refus_ab += r["abstention"] and not s["abstention"]
            refus_ba += s["abstention"] and not r["abstention"]
    return {"hors_corpus_abstention_perdue": hors_ab, "hors_corpus_abstention_gagnee": hors_ba,
            "repondables_refus_corrige": refus_ab, "repondables_refus_nouveau": refus_ba}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("execution")
    parser.add_argument("--comparer")
    args = parser.parse_args()
    a = lire(pathlib.Path(args.execution))
    resultat = {"execution": args.execution, "indicateurs": indicateurs(a)}
    if args.comparer:
        b = lire(pathlib.Path(args.comparer))
        if sorted(s["qid"] for s in a) != sorted(s["qid"] for s in b):
            raise SystemExit("ERREUR : les deux exécutions ne portent pas sur les mêmes questions")
        resultat.update(comparee=args.comparer, indicateurs_comparee=indicateurs(b), discordances=discordances(a, b))
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    (pathlib.Path(args.execution) / "score_auto.json").write_text(
        json.dumps(resultat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
