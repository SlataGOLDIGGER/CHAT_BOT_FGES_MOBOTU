"""Valide les fichiers de questions : format, identifiants, étanchéité des familles, citations, part hors corpus.

Usage : python -m scripts.valider_questions                 (train et dev du dépôt)
        python -m scripts.valider_questions --test CHEMIN    (P4 uniquement, ajoute le test scellé)
"""
import argparse
import collections
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
EVAL = RACINE / "shared" / "eval"
CHAMPS = {"qid", "ensemble", "auteur", "question", "dans_corpus", "sections_or", "famille", "reponse_ref", "date"}
ABSTENTION = "Je ne trouve pas cette information dans les fiches du corpus."
CITATION = re.compile(r"\[(F\d+-[^\]\s]+)\]")


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test")
    args = parser.parse_args()
    familles = json.loads((EVAL / "familles.json").read_text(encoding="utf-8"))
    fichiers = {"train": EVAL / "questions_train.jsonl", "dev": EVAL / "questions_dev.jsonl"}
    if args.test:
        fichiers["test"] = pathlib.Path(args.test).expanduser()
    erreurs, vues, textes = [], set(), {}
    for ensemble, chemin in fichiers.items():
        questions = lire_jsonl(chemin) if chemin.exists() else []
        for q in questions:
            ou = f"{chemin.name} {q.get('qid')}"
            if set(q) != CHAMPS:
                erreurs.append(f"{ou} : champs {sorted(set(q) ^ CHAMPS)}")
                continue
            if q["qid"] in vues:
                erreurs.append(f"{ou} : identifiant en double")
            vues.add(q["qid"])
            if q["ensemble"] != ensemble:
                erreurs.append(f"{ou} : ensemble {q['ensemble']} dans le fichier {ensemble}")
            cle = re.sub(r"\W+", " ", q["question"].lower()).strip()
            if cle in textes:
                erreurs.append(f"{ou} : même question que {textes[cle]}")
            textes[cle] = q["qid"]
            if q["dans_corpus"]:
                for s in q["sections_or"]:
                    f = familles["sections"].get(s)
                    if f is None or familles["familles"][f]["ensemble"] != ensemble:
                        erreurs.append(f"{ou} : section {s} hors de l'ensemble {ensemble}")
                citees = set(CITATION.findall(q["reponse_ref"]))
                if not citees or not citees <= set(q["sections_or"]):
                    erreurs.append(f"{ou} : citations {sorted(citees)} incompatibles avec les sections d'or")
            elif q["reponse_ref"] != ABSTENTION or q["sections_or"]:
                erreurs.append(f"{ou} : question hors corpus mal formée")
        if questions:
            hors = sum(not q["dans_corpus"] for q in questions)
            auteurs = collections.Counter(q["auteur"] for q in questions)
            nb_familles = len({q["famille"] for q in questions if q["dans_corpus"]})
            print(f"{ensemble} : {len(questions)} questions, {hors} hors corpus ({hors / len(questions):.0%}), "
                  f"{nb_familles} familles couvertes, auteurs {dict(sorted(auteurs.items()))}")
    for e in erreurs:
        print("ERREUR :", e)
    if erreurs:
        sys.exit(1)
    print("Questions conformes.")


if __name__ == "__main__":
    main()
