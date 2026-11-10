"""Contrôle d'hygiène des fichiers suivis par Git : secrets, poids de modèles, fichiers volumineux, test scellé.

Usage : python -m scripts.verifier_depot     (code de sortie 1 si un fichier pose problème)
"""

import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
EXTENSIONS_INTERDITES = {
    ".gguf",
    ".onnx",
    ".safetensors",
    ".pt",
    ".pth",
    ".ckpt",
    ".npy",
    ".zip",
    ".env",
}
AUTORISES_BIN = re.compile(r"^a3/public/data/vecteurs-[\w-]+\.bin$")
TAILLE_MAX = 5 * 2**20
SECRETS = [
    re.compile(p)
    for p in (
        r"hf_[A-Za-z0-9]{30,}",
        r"ghp_[A-Za-z0-9]{30,}",
        r"github_pat_[A-Za-z0-9_]{30,}",
        r"sk-[A-Za-z0-9]{30,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    )
]
NOMS_INTERDITS = re.compile(
    r"(questions_test|feuille_test|cle_test|\.venv|node_modules/)"
)
# Consignes pour assistants IA et documents privés du plan : jamais dans le dépôt
NOMS_PRIVES = re.compile(
    r"(\.prompt\.md$|\.agent\.md$|\.instructions\.md$|(^|/)AGENTS\.md$|(^|/)CLAUDE\.md$|"
    r"copilot-instructions\.md$|^\.github/prompts/|plan_equipe/|(^|/)roles\.md$)"
)


def main() -> None:
    fichiers = subprocess.run(
        ["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    problemes = []
    for nom in fichiers:
        chemin = RACINE / nom
        if not chemin.is_file():
            continue
        if chemin.suffix in EXTENSIONS_INTERDITES or (
            chemin.suffix == ".bin" and not AUTORISES_BIN.match(nom)
        ):
            problemes.append(f"{nom} : type de fichier à ne pas versionner")
        if NOMS_INTERDITS.search(nom):
            problemes.append(f"{nom} : fichier qui ne doit jamais être versionné")
        if NOMS_PRIVES.search(nom):
            problemes.append(
                f"{nom} : document privé ou consigne d'assistant, hors du dépôt"
            )
        if chemin.stat().st_size > TAILLE_MAX:
            problemes.append(f"{nom} : plus de 5 Mo")
        if chemin.suffix in {".bin", ".png", ".jpg", ".pdf", ".xml"}:
            continue
        contenu = chemin.read_text(encoding="utf-8", errors="ignore")
        for motif in SECRETS:
            if motif.search(contenu):
                problemes.append(
                    f"{nom} : ressemble à un secret ({motif.pattern[:12]}…)"
                )
    for p in problemes:
        print("PROBLÈME :", p)
    if problemes:
        sys.exit(1)
    print(
        f"{len(fichiers)} fichiers suivis vérifiés : aucun secret, poids ou fichier interdit."
    )


if __name__ == "__main__":
    main()
