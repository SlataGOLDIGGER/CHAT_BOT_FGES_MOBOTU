"""Scelle le jeu de test : calcule son empreinte SHA-256, seule information versionnée.

Usage (P4 uniquement) : python -m scripts.sceller_test --test ~/nlp_scelle/questions_test.jsonl
Sortie : shared/eval/test_scelle.json
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", required=True)
    args = parser.parse_args()
    chemin = pathlib.Path(args.test).expanduser().resolve()
    if RACINE in chemin.parents:
        sys.exit("ERREUR : le fichier de test se trouve dans le dépôt ; déplacez-le avant de sceller")
    lignes = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
    scelle = {
        "sha256": hashlib.sha256(chemin.read_bytes()).hexdigest(),
        "questions": len(lignes),
        "hors_corpus": sum(not q["dans_corpus"] for q in lignes),
        "familles": len({q["famille"] for q in lignes}),
        "date_scellement": datetime.date.today().isoformat(),
        "detenteur": "P4",
    }
    (RACINE / "shared" / "eval" / "test_scelle.json").write_text(
        json.dumps(scelle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(scelle, ensure_ascii=False, indent=2))
    print("Versionnez uniquement shared/eval/test_scelle.json ; le fichier de test reste sur ce poste.")


if __name__ == "__main__":
    main()
