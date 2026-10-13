"""Vérifie l'intégrité du corpus versionné : empreintes, identifiants, couverture des sections, longueurs.

Usage : python -m scripts.verifier_corpus      (code de sortie 1 en cas d'anomalie)
"""
import hashlib
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = RACINE / "shared" / "corpus"


def sha256_fichier(chemin: pathlib.Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    anomalies = []
    manifeste = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    for fiche in manifeste["fiches"]:
        xml = CORPUS / "source" / f"{fiche['fiche_id']}.xml"
        if not xml.exists() or sha256_fichier(xml) != fiche["sha256_xml"]:
            anomalies.append(f"{xml.name} absent ou modifié depuis la collecte")
    for nom, attendu in manifeste["fichiers"].items():
        if sha256_fichier(CORPUS / nom) != attendu["sha256"]:
            anomalies.append(f"{nom} modifié sans reconstruction du manifeste")
    sections = lire_jsonl(CORPUS / "sections.jsonl")
    ids = {s["section_id"] for s in sections}
    if len(ids) != len(sections):
        anomalies.append("identifiants de section en double")
    for strategie in ("section", "fenetre", "paragraphe"):
        passages = lire_jsonl(CORPUS / f"passages_{strategie}.jsonl")
        couvertes = {p["section_id"] for p in passages}
        if couvertes != ids:
            anomalies.append(f"{strategie} : {len(ids - couvertes)} sections sans passage")
        if len({p["passage_id"] for p in passages}) != len(passages):
            anomalies.append(f"{strategie} : identifiants de passage en double")
        if max(p["n_tokens"] for p in passages) > 512:
            anomalies.append(f"{strategie} : passage de plus de 512 tokens")
    if "Licence Ouverte" not in manifeste["licence"]["nom"] or not manifeste["attribution"]:
        anomalies.append("licence ou attribution manquante")
    for anomalie in anomalies:
        print("ANOMALIE :", anomalie)
    if anomalies:
        sys.exit(1)
    print(f"Corpus conforme : {len(manifeste['fiches'])} fiches, {len(sections)} sections, "
          f"version {manifeste['version_corpus']}, découpage {manifeste['version_decoupage']}")


if __name__ == "__main__":
    main()