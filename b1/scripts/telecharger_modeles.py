"""Télécharge le générateur GGUF, l'encodeur et, s'il est publié, l'adaptateur, à leurs révisions figées.

Usage : python -m b1.scripts.telecharger_modeles
Résultat : b1/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf (2,5 Go), empreintes vérifiées
"""
import hashlib
import json
import pathlib
import sys

from huggingface_hub import hf_hub_download

RACINE = pathlib.Path(__file__).resolve().parents[2]
VERROU = json.loads((RACINE / "b1" / "config" / "models.lock.json").read_text(encoding="utf-8"))
DOSSIER = RACINE / "b1" / "models"


def sha256_fichier(chemin: pathlib.Path) -> str:
    empreinte = hashlib.sha256()
    with open(chemin, "rb") as fichier:
        for bloc in iter(lambda: fichier.read(1 << 20), b""):
            empreinte.update(bloc)
    return empreinte.hexdigest()


def recuperer(entree: dict) -> pathlib.Path:
    chemin = pathlib.Path(hf_hub_download(entree["depot"], entree["fichier"],
                                          revision=entree["revision"], local_dir=DOSSIER))
    print(f"Vérification de l'empreinte de {chemin.name}…")
    obtenue = sha256_fichier(chemin)
    if obtenue != entree["sha256"]:
        sys.exit(f"ERREUR : empreinte {obtenue} différente de l'empreinte attendue {entree['sha256']}")
    print(f"OK : {chemin.relative_to(RACINE)}")
    return chemin


def main() -> None:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    recuperer(VERROU["generateur"])
    encodeur = VERROU["encodeur"]
    for nom in ("tokenizer.json", encodeur["fichier"]):
        hf_hub_download(encodeur["depot"], nom, revision=encodeur["revision"])
    print(f"OK : encodeur {encodeur['depot']} (cache Hugging Face)")
    if VERROU.get("adaptateur"):
        recuperer(VERROU["adaptateur"])
    else:
        print("Aucun adaptateur publié pour l'instant (models.lock.json : \"adaptateur\": null).")


if __name__ == "__main__":
    main()