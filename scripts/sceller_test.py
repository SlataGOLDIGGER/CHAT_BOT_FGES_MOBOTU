"""Scelle le jeu de test : calcule son empreinte SHA-256, seule information versionnée.

Usage (P4 uniquement) : python -m scripts.sceller_test --test ~/nlp_scelle/questions_test.jsonl
Sortie : shared/eval/test_scelle.json
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", required=True)
    args = parser.parse_args()
    chemin = pathlib.Path(args.test).expanduser().resolve()
    if RACINE in chemin.parents:
        sys.exit("ERREUR : le fichier de test se trouve dans le dépôt ; déplacez-le avant de sceller")
    validation = subprocess.run(
        [sys.executable, "-m", "scripts.valider_questions", "--test", str(chemin)],
        cwd=RACINE, check=False,
    )
    if validation.returncode:
        sys.exit("ERREUR : questions non conformes ; scellement annulé")
    lignes = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
    hors = sum(not q["dans_corpus"] for q in lignes)
    couvertes = {q["famille"] for q in lignes if q["dans_corpus"]}
    if len(lignes) != 40 or hors != 10 or len(couvertes) != 12:
        sys.exit("ERREUR : le test doit contenir 40 questions, dont 10 hors corpus et 12 familles répondables")
    scelle = {
        "sha256": hashlib.sha256(chemin.read_bytes()).hexdigest(),
        "questions": len(lignes),
        "hors_corpus": hors,
        "familles": len(couvertes),
        "date_scellement": datetime.date.today().isoformat(),
        "detenteur": "P4",
    }
    (RACINE / "shared" / "eval" / "test_scelle.json").write_text(
        json.dumps(scelle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(scelle, ensure_ascii=False, indent=2))
    print("Versionnez uniquement shared/eval/test_scelle.json ; le fichier de test reste sur ce poste.")


if __name__ == "__main__":
    main()
