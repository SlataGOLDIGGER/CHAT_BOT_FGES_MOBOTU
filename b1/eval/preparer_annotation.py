"""Prépare une feuille d'annotation humaine en aveugle pour comparer deux exécutions (avant / après adaptation).

Usage : python -m b1.eval.preparer_annotation --questions shared/eval/questions_dev.jsonl \
          --a artifacts/b1/runs/dev-base --b artifacts/b1/runs/dev-adapte --sortie artifacts/b1/annotation/dev-v1
Sorties : feuille.csv (à remplir par chaque annotateur) et cle.json (correspondance X/Y, gardée par P4)
"""
import argparse
import csv
import json
import pathlib
import random

COLONNES = ["item", "qid", "question", "reponse_reference", "systeme", "reponse", "passages_cites",
            "exactitude", "appui", "code_erreur", "commentaire"]


def lire(chemin: pathlib.Path) -> dict:
    return {json.loads(l)["qid"]: json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()}


def textes_cites(sortie: dict, passages: dict) -> str:
    if not sortie["analyse"]:
        return ""
    labels = {f"S{n}" for n in sortie["analyse"]["cites"]}
    return "\n---\n".join(f"[{s['label']}] {passages[s['passage_id']][:600]}"
                          for s in sortie["sources"] if s["label"] in labels)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True)
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--graine", type=int, default=2026)
    args = parser.parse_args()
    racine = pathlib.Path(__file__).resolve().parents[2]
    questions = [json.loads(l) for l in pathlib.Path(args.questions).expanduser().read_text(encoding="utf-8").splitlines() if l.strip()]
    execs = {"A": lire(pathlib.Path(args.a) / "sorties.jsonl"), "B": lire(pathlib.Path(args.b) / "sorties.jsonl")}
    config = json.loads((pathlib.Path(args.a) / "execution.json").read_text(encoding="utf-8"))["config_rag"]
    fichier_passages = racine / "shared" / "corpus" / f"passages_{config['strategie']}.jsonl"
    passages = {json.loads(l)["passage_id"]: json.loads(l)["texte"] for l in fichier_passages.read_text(encoding="utf-8").splitlines()}
    hasard = random.Random(args.graine)
    lignes, cle = [], {}
    for q in questions:
        ordre = ["A", "B"]
        hasard.shuffle(ordre)
        for masque, vrai in zip(("X", "Y"), ordre):
            sortie = execs[vrai][q["qid"]]
            item = f"{q['qid']}-{masque}"
            cle[item] = vrai
            lignes.append({"item": item, "qid": q["qid"], "question": q["question"], "reponse_reference": q["reponse_ref"],
                           "systeme": masque, "reponse": sortie["reponse"], "passages_cites": textes_cites(sortie, passages),
                           "exactitude": "", "appui": "", "code_erreur": "", "commentaire": ""})
    hasard.shuffle(lignes)
    dossier = pathlib.Path(args.sortie).expanduser()
    dossier.mkdir(parents=True, exist_ok=True)
    with open(dossier / "feuille.csv", "w", encoding="utf-8-sig", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    (dossier / "cle.json").write_text(json.dumps({"A": args.a, "B": args.b, "items": cle}, indent=2) + "\n", encoding="utf-8")
    print(f"{len(lignes)} lignes à annoter -> {dossier / 'feuille.csv'} ; clé (ne pas diffuser) -> {dossier / 'cle.json'}")


if __name__ == "__main__":
    main()
