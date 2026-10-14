"""Saisie guidée des questions d'évaluation, avec contrôle immédiat des sections d'or et des citations.

Usage :
  python -m scripts.ajouter_question --ensemble train --auteur P1
  python -m scripts.ajouter_question --ensemble test --auteur P4 --sortie ~/nlp_scelle/questions_test.jsonl
Le test ne peut être écrit qu'en dehors du dépôt.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
EVAL = RACINE / "shared" / "eval"
ABSTENTION = "Je ne trouve pas cette information dans les fiches du corpus."
CITATION = re.compile(r"\[(F\d+-[^\]\s]+)\]")


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    if not chemin.exists():
        return []
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def normaliser(question: str) -> str:
    return re.sub(r"\W+", " ", question.lower()).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ensemble", choices=["train", "dev", "test"], required=True)
    parser.add_argument("--auteur", choices=["P1", "P2", "P3", "P4", "P5"], required=True)
    parser.add_argument("--sortie")
    args = parser.parse_args()

    if args.ensemble == "test":
        if not args.sortie:
            sys.exit("ERREUR : pour le test, indiquez --sortie hors du dépôt (ex. ~/nlp_scelle/questions_test.jsonl)")
        sortie = pathlib.Path(args.sortie).expanduser().resolve()
        if RACINE in sortie.parents:
            sys.exit("ERREUR : le test scellé ne doit jamais être écrit dans le dépôt")
    else:
        sortie = EVAL / f"questions_{args.ensemble}.jsonl"
    sortie.parent.mkdir(parents=True, exist_ok=True)

    familles = json.loads((EVAL / "familles.json").read_text(encoding="utf-8"))
    themes = json.loads((EVAL / "themes_hors_corpus.json").read_text(encoding="utf-8")).get(args.ensemble, [])
    sections = {json.loads(l)["section_id"]: json.loads(l) for l in
                (RACINE / "shared" / "corpus" / "sections.jsonl").read_text(encoding="utf-8").splitlines()}
    autorisees = {s for s, f in familles["sections"].items() if familles["familles"][f]["ensemble"] == args.ensemble}
    textes = {}
    for s in autorisees:
        textes.setdefault(sections[s]["texte"], []).append(s)
    existantes = lire_jsonl(sortie) + lire_jsonl(EVAL / "questions_train.jsonl") + lire_jsonl(EVAL / "questions_dev.jsonl")
    deja = {normaliser(q["question"]) for q in existantes}
    numero = 1 + sum(1 for q in lire_jsonl(sortie) if q["auteur"] == args.auteur)

    print(f"Sections autorisées pour l'ensemble {args.ensemble} :")
    for s in sorted(autorisees):
        print(f"  {s:<16} {' › '.join(sections[s]['chemin'])[:100]}")
    while True:
        question = input("\nQuestion (Entrée vide pour terminer) : ").strip()
        if not question:
            break
        if normaliser(question) in deja:
            print("Refusé : cette question existe déjà.")
            continue
        if input("La réponse figure-t-elle dans le corpus ? [o/n] : ").strip().lower() == "o":
            saisies = [s.strip() for s in input("Sections d'or, séparées par des virgules : ").split(",") if s.strip()]
            hors = [s for s in saisies if s not in autorisees]
            if not saisies or hors:
                print(f"Refusé : sections absentes de l'ensemble {args.ensemble} : {hors or 'aucune saisie'}")
                continue
            sections_or = sorted({d for s in saisies for d in textes[sections[s]["texte"]]})
            reponse = input("Réponse de référence, chaque phrase suivie de [identifiant] : ").strip()
            citees = set(CITATION.findall(reponse))
            if not citees or not citees <= set(sections_or):
                print(f"Refusé : citez au moins une section d'or, et seulement elles ({', '.join(sections_or)})")
                continue
            entree = {"dans_corpus": True, "sections_or": sections_or, "famille": familles["sections"][sections_or[0]],
                      "reponse_ref": reponse}
        else:
            if themes:
                for i, t in enumerate(themes, start=1):
                    print(f"  {i}. {t}")
                choix = input("Numéro du thème hors corpus : ").strip()
                if not choix.isdigit() or not 1 <= int(choix) <= len(themes):
                    print("Refusé : numéro de thème invalide.")
                    continue
                theme = themes[int(choix) - 1]
            else:
                theme = input("Thème hors corpus (texte libre, propre au test) : ").strip()
            entree = {"dans_corpus": False, "sections_or": [], "famille": f"hors/{theme}", "reponse_ref": ABSTENTION}
        qid = f"{args.ensemble}-{args.auteur}-{numero:03d}"
        ligne = {"qid": qid, "ensemble": args.ensemble, "auteur": args.auteur, "question": question, **entree,
                 "date": datetime.date.today().isoformat()}
        with open(sortie, "a", encoding="utf-8", newline="\n") as fichier:
            fichier.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        deja.add(normaliser(question))
        numero += 1
        print(f"Enregistrée : {qid}")


if __name__ == "__main__":
    main()
