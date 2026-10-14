"""Répartit les familles de questions entre entraînement, développement et test, de façon reproductible.

Famille = une section ; les branches conditionnelles (cas, situations) sont rattachées à leur unité parente,
car elles partagent souvent du texte. Une famille entière appartient à un seul ensemble.
Usage : python -m scripts.repartir_familles
Sortie : shared/eval/familles.json
"""
import collections
import hashlib
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[1]
GRAINE = "nlp-a3-b1-2026"
MOTIF = ["train", "train", "dev", "train", "test"]  # 60 % / 20 % / 20 % des familles


def famille(section_id: str) -> str:
    fiche, codes = section_id.split("-", 1)
    garde = []
    for code in codes.split("."):
        if code[0] in "cs":
            break
        garde.append(code)
    return f"{fiche}-{'.'.join(garde) if garde else '0'}"


def main() -> None:
    lignes = (RACINE / "shared" / "corpus" / "sections.jsonl").read_text(encoding="utf-8").splitlines()
    sections = [json.loads(l)["section_id"] for l in lignes]
    familles: dict[str, list[str]] = collections.defaultdict(list)
    for s in sections:
        familles[famille(s)].append(s)
    # Stratification par fiche : le motif se poursuit d'une fiche à l'autre, chaque fiche reçoit ~60/20/20.
    repartition, rang = {}, 0
    for fiche in sorted({f.split("-")[0] for f in familles}):
        propres = sorted((f for f in familles if f.split("-")[0] == fiche),
                         key=lambda f: hashlib.sha256(f"{GRAINE}:{f}".encode()).hexdigest())
        for f in propres:
            repartition[f] = MOTIF[rang % len(MOTIF)]
            rang += 1
    sortie = {
        "graine": GRAINE,
        "regle": "famille = section ; cas et situations rattachés à leur unité parente",
        "familles": {f: {"ensemble": repartition[f], "sections": familles[f]} for f in sorted(familles)},
        "sections": {s: famille(s) for s in sections},
    }
    chemin = RACINE / "shared" / "eval" / "familles.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compte = collections.Counter(repartition.values())
    par_fiche = collections.Counter((f.split("-")[0], e) for f, e in repartition.items())
    print(f"{len(familles)} familles : {dict(compte)}")
    for fiche in sorted({f.split('-')[0] for f in familles}):
        print(f"  {fiche} : " + ", ".join(f"{e} {par_fiche[(fiche, e)]}" for e in ("train", "dev", "test")))


if __name__ == "__main__":
    main()
