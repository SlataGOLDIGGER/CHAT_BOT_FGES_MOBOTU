"""Télécharge le jeu de données Service-Public et extrait les fiches retenues.

Usage : python -m scripts.collecter_fiches [--archive CHEMIN_ZIP]
"""
import argparse
import datetime
import hashlib
import io
import json
import pathlib
import sys
import zipfile

import requests

RACINE = pathlib.Path(__file__).resolve().parents[1]
CONFIG = RACINE / "shared" / "corpus" / "fiches.json"
SOURCE = RACINE / "shared" / "corpus" / "source"


def sha256(donnees: bytes) -> str:
    return hashlib.sha256(donnees).hexdigest()


def lire_archive(config: dict, chemin_local: str | None) -> bytes:
    if chemin_local:
        print(f"Lecture de l'archive locale {chemin_local}")
        return pathlib.Path(chemin_local).read_bytes()
    url = config["jeu_de_donnees"]
    print(f"Téléchargement de {url} (environ 25 Mo)")
    reponse = requests.get(url, timeout=300)
    reponse.raise_for_status()
    return reponse.content


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", help="archive zip déjà téléchargée (facultatif)")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    archive = lire_archive(config, args.archive)
    SOURCE.mkdir(parents=True, exist_ok=True)

    fiches = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        noms = set(zf.namelist())
        for fiche_id in config["fiches"]:
            nom = f"{fiche_id}.xml"
            if nom not in noms:
                sys.exit(f"ERREUR : {nom} est absent de l'archive")
            donnees = zf.read(nom)
            (SOURCE / nom).write_bytes(donnees)
            fiches[fiche_id] = {"fichier": f"source/{nom}", "sha256": sha256(donnees), "octets": len(donnees)}
            print(f"{fiche_id} : {len(donnees)} octets extraits")

    collecte = {
        "date_collecte": datetime.date.today().isoformat(),
        "url_archive": config["jeu_de_donnees"],
        "sha256_archive": sha256(archive),
        "octets_archive": len(archive),
        "fiches": fiches,
    }
    (SOURCE / "collecte.json").write_text(
        json.dumps(collecte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(fiches)} fiches extraites dans shared/corpus/source/")


if __name__ == "__main__":
    main()