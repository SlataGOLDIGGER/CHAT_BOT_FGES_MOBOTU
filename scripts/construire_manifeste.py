"""Écrit shared/corpus/manifest.json : source, licence, attribution, dates et empreintes de tous les fichiers.

Usage : python -m scripts.construire_manifeste
"""
import hashlib
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = RACINE / "shared" / "corpus"
DERIVES = ["sections.jsonl", "passages_section.jsonl", "passages_fenetre.jsonl", "passages_paragraphe.jsonl"]
VERSION_DECOUPAGE = "1"


def sha256_fichier(chemin: pathlib.Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def main() -> None:
    config = json.loads((CORPUS / "fiches.json").read_text(encoding="utf-8"))
    collecte = json.loads((CORPUS / "source" / "collecte.json").read_text(encoding="utf-8"))
    sections = [json.loads(l) for l in (CORPUS / "sections.jsonl").read_text(encoding="utf-8").splitlines()]
    fiches = []
    for fiche_id in config["fiches"]:
        propres = [s for s in sections if s["fiche_id"] == fiche_id]
        fiches.append({
            "fiche_id": fiche_id, "titre": propres[0]["fiche_titre"], "url": propres[0]["url"],
            "date_maj": propres[0]["date_maj"], "sha256_xml": collecte["fiches"][fiche_id]["sha256"],
            "sections": len(propres),
        })
    liste = ", ".join(config["fiches"])
    manifeste = {
        "version_corpus": config["version_corpus"],
        "date_collecte": collecte["date_collecte"],
        "source": {
            "editeur": "Direction de l'information légale et administrative (DILA)",
            "jeu_de_donnees": "Fiches pratiques et ressources de Service-Public.gouv.fr Particuliers",
            "page": "https://www.data.gouv.fr/datasets/fiches-pratiques-et-ressources-de-service-public-gouv-fr-particuliers",
            "url_archive": collecte["url_archive"],
            "sha256_archive": collecte["sha256_archive"],
        },
        "licence": {"nom": "Licence Ouverte / Open Licence version 2.0 (Etalab)",
                    "url": "https://github.com/etalab/licence-ouverte/blob/master/LO.md"},
        "attribution": (f"Source : Service-Public.gouv.fr, Direction de l'information légale et administrative "
                        f"(DILA), fiches {liste}, données collectées le {collecte['date_collecte']}, "
                        f"réutilisées sous Licence Ouverte 2.0."),
        "fiches": fiches,
        "version_decoupage": VERSION_DECOUPAGE,
        "fichiers": {nom: {"sha256": sha256_fichier(CORPUS / nom),
                           "lignes": len((CORPUS / nom).read_text(encoding="utf-8").splitlines())}
                     for nom in DERIVES},
    }
    (CORPUS / "manifest.json").write_text(json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    print(f"Manifeste écrit : {len(fiches)} fiches, {len(sections)} sections, collecte du {collecte['date_collecte']}")


if __name__ == "__main__":
    main()