"""Agrège les feuilles d'annotation : exactitude et appui par système, accord entre annotateurs (kappa de Cohen),
comparaison appariée base / adapté (test exact du signe).

Usage : python -m b1.eval.agreger_annotation --cle artifacts/b1/annotation/dev-v1/cle.json \
          artifacts/b1/annotation/dev-v1/feuille_P1.csv artifacts/b1/annotation/dev-v1/feuille_P2.csv \
          [--consensus artifacts/b1/annotation/dev-v1/feuille_consensus.csv]
Grille : exactitude 2 = correcte, 1 = partielle, 0 = incorrecte, A = abstention ;
         appui 2 = entièrement appuyée, 1 = partiellement, 0 = non appuyée, NA = abstention.
Le kappa porte sur les deux premières feuilles (notes initiales) ; les scores et la comparaison appariée
portent sur la feuille de consensus si elle est fournie, sinon sur toutes les feuilles.
"""
import argparse
import collections
import csv
import json
import math
import pathlib

import numpy as np

ABSTENTION = "Je ne trouve pas cette information dans les fiches du corpus."


def lire_feuille(chemin: pathlib.Path) -> dict:
    with open(chemin, encoding="utf-8-sig", newline="") as fichier:
        return {l["item"]: l for l in csv.DictReader(fichier, delimiter=";")}


def kappa(a: list[str], b: list[str]) -> float:
    etiquettes = sorted(set(a) | set(b))
    n = len(a)
    accord = sum(x == y for x, y in zip(a, b)) / n
    hasard = sum((a.count(e) / n) * (b.count(e) / n) for e in etiquettes)
    return (accord - hasard) / (1 - hasard) if hasard < 1 else 1.0


def test_signe(ameliorees: int, degradees: int) -> float:
    """Probabilité bilatérale d'un écart au moins aussi grand si l'adaptation n'avait aucun effet."""
    n = ameliorees + degradees
    if n == 0:
        return 1.0
    k = min(ameliorees, degradees)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def part(notes: np.ndarray, note: int) -> str:
    return f"{np.mean(notes == note):.1%}" if len(notes) else "—"


def reussite(ligne: dict) -> bool:
    """Question répondable : réponse correcte ; question hors corpus : abstention."""
    note = ligne["exactitude"].strip()
    return note == "A" if ligne["reponse_reference"].strip() == ABSTENTION else note == "2"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cle", required=True)
    parser.add_argument("--consensus")
    parser.add_argument("feuilles", nargs="+")
    args = parser.parse_args()
    cle = json.loads(pathlib.Path(args.cle).read_text(encoding="utf-8"))
    feuilles = {pathlib.Path(f).stem: lire_feuille(pathlib.Path(f)) for f in args.feuilles}
    notees = {"consensus": lire_feuille(pathlib.Path(args.consensus))} if args.consensus else feuilles
    incompletes = [(nom, i) for nom, f in {**feuilles, **notees}.items() for i, l in f.items()
                   if not l["exactitude"].strip()]
    if incompletes:
        raise SystemExit(f"ERREUR : {len(incompletes)} lignes sans exactitude, par exemple {incompletes[:3]}")

    par_systeme = {s: {"exactitude": [], "appui": [], "abstentions": 0, "codes": collections.Counter()} for s in "AB"}
    for feuille in notees.values():
        for item, ligne in feuille.items():
            d = par_systeme[cle["items"][item]]
            if ligne["exactitude"].strip() == "A":
                d["abstentions"] += 1
            else:
                d["exactitude"].append(int(ligne["exactitude"]))
            if ligne["appui"].strip() not in ("", "NA"):
                d["appui"].append(int(ligne["appui"]))
            if ligne["code_erreur"].strip():
                d["codes"][ligne["code_erreur"].strip()] += 1
    for systeme, d in par_systeme.items():
        ex = np.array(d["exactitude"])
        print(f"Système {systeme} ({cle[systeme]}) : {len(ex)} réponses notées, correctes {part(ex, 2)}, "
              f"partielles {part(ex, 1)}, incorrectes {part(ex, 0)}, abstentions {d['abstentions']}, "
              f"appui moyen {np.mean(d['appui']) if d['appui'] else float('nan'):.2f} / 2 ; erreurs {dict(d['codes'])}")

    noms = list(feuilles)
    if len(noms) >= 2:
        communs = sorted(set(feuilles[noms[0]]) & set(feuilles[noms[1]]))
        a = [feuilles[noms[0]][i]["exactitude"].strip() for i in communs]
        b = [feuilles[noms[1]][i]["exactitude"].strip() for i in communs]
        desaccords = [i for i, x, y in zip(communs, a, b) if x != y]
        print(f"Accord {noms[0]} / {noms[1]} sur l'exactitude : kappa {kappa(a, b):.2f} ; "
              f"{len(desaccords)} désaccords à arbitrer : {desaccords[:10]}")

    if args.consensus:
        succes = collections.defaultdict(dict)
        for item, ligne in notees["consensus"].items():
            succes[ligne["qid"]][cle["items"][item]] = reussite(ligne)
        ameliorees = sum(1 for s in succes.values() if s.get("B") and not s.get("A"))
        degradees = sum(1 for s in succes.values() if s.get("A") and not s.get("B"))
        print(f"Comparaison appariée sur {len(succes)} questions (réussite = réponse correcte, ou abstention "
              f"hors corpus) : B mieux que A sur {ameliorees}, moins bien sur {degradees} ; "
              f"test exact du signe p = {test_signe(ameliorees, degradees):.3f}")


if __name__ == "__main__":
    main()
