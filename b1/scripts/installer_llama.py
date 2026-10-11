"""Télécharge et installe le moteur llama.cpp (build figé) adapté au système du poste.

Usage : python -m b1.scripts.installer_llama
        python -m b1.scripts.installer_llama --plateforme windows-arm64   (Windows ARM avec un Python x64 émulé)
Résultat : b1/runtime/llama-b11146/ contenant llama-server (llama-server.exe sous Windows)
"""
import argparse
import hashlib
import io
import json
import pathlib
import platform
import subprocess
import sys
import tarfile
import zipfile

import requests

RACINE = pathlib.Path(__file__).resolve().parents[2]
VERROU = json.loads((RACINE / "b1" / "config" / "models.lock.json").read_text(encoding="utf-8"))


def plateforme() -> str:
    systeme, machine = platform.system(), platform.machine().lower()
    arm = machine in ("arm64", "aarch64")
    if systeme == "Darwin":
        return "macos-arm64" if arm else "macos-x64"
    if systeme == "Windows":
        return "windows-arm64" if arm else "windows-x64"
    if systeme == "Linux":
        return "linux-arm64" if arm else "linux-x64"
    sys.exit(f"ERREUR : système non prévu ({systeme} {machine})")


def main() -> None:
    llama = VERROU["llama_cpp"]
    parser = argparse.ArgumentParser()
    parser.add_argument("--plateforme", choices=sorted(llama["archives"]),
                        help="impose l'archive, par exemple quand Python est émulé")
    args = parser.parse_args()
    cible = args.plateforme or plateforme()
    archive = llama["archives"][cible]
    url = f"https://github.com/ggml-org/llama.cpp/releases/download/{llama['version']}/{archive['fichier']}"
    print(f"Plateforme détectée : {cible}\nTéléchargement de {url}")
    donnees = requests.get(url, timeout=300).content
    empreinte = hashlib.sha256(donnees).hexdigest()
    if empreinte != archive["sha256"]:
        sys.exit(f"ERREUR : empreinte inattendue {empreinte} (attendu {archive['sha256']})")
    dossier = RACINE / "b1" / "runtime" / f"llama-{llama['version']}"
    dossier.mkdir(parents=True, exist_ok=True)
    if archive["fichier"].endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(donnees)) as zf:
            zf.extractall(dossier)
    else:
        with tarfile.open(fileobj=io.BytesIO(donnees), mode="r:gz") as tf:
            tf.extractall(dossier, filter="data")
    nom = "llama-server.exe" if cible.startswith("windows") else "llama-server"
    serveurs = sorted(dossier.rglob(nom))
    if not serveurs:
        sys.exit(f"ERREUR : {nom} introuvable dans {dossier}")
    serveur = serveurs[0]
    if not cible.startswith("windows"):
        serveur.chmod(0o755)
    (dossier / "chemin_serveur.txt").write_text(str(serveur.relative_to(RACINE)), encoding="utf-8")
    version = subprocess.run([str(serveur), "--version"], capture_output=True, text=True)
    print((version.stdout + version.stderr).strip())
    print(f"Moteur installé : {serveur.relative_to(RACINE)}")


if __name__ == "__main__":
    main()