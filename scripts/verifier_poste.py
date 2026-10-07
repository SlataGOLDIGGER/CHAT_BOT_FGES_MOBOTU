"""Relève l'environnement du poste pour remplir la fiche docs/environnement/<rôle>.md.

Usage : python -m scripts.verifier_poste
"""
import platform
import shutil
import subprocess
import sys


def version(commande: list[str]) -> str:
    if shutil.which(commande[0]) is None:
        return "ABSENT"
    try:
        sortie = subprocess.run(commande, capture_output=True, text=True, timeout=20)
        return (sortie.stdout or sortie.stderr).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError) as erreur:
        return f"ERREUR ({erreur})"


def memoire_go() -> str:
    try:
        import psutil
        return f"{psutil.virtual_memory().total / 2**30:.1f} Go"
    except ImportError:
        return "non mesurée (psutil absent de cet environnement)"


def main() -> None:
    lignes = {
        "Système": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "Architecture": platform.machine(),
        "Processeur": platform.processor() or "non renseigné par le système",
        "Mémoire": memoire_go(),
        "Python (environnement actif)": sys.version.split()[0],
        "Git": version(["git", "--version"]),
        "Node.js": version(["node", "--version"]),
        "npm": version(["npm.cmd" if platform.system() == "Windows" else "npm", "--version"]),
        "VS Code": version(["code.cmd" if platform.system() == "Windows" else "code", "--version"]),
    }
    for cle, valeur in lignes.items():
        print(f"| {cle} | {valeur} |")


if __name__ == "__main__":
    main()
