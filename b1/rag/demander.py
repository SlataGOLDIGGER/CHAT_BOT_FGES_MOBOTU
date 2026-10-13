"""Pose une question au RAG depuis le terminal.

Usage : python -m b1.rag.demander "Quelle est la durée maximale d'un stage ?"
Prérequis : le serveur tourne dans un autre terminal (python -m b1.scripts.lancer_serveur).
"""

import sys

from b1.rag.pipeline import charger_config, repondre
from b1.rag.recherche import Recherche


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Usage : python -m b1.rag.demander "votre question"')
    config = charger_config()
    resultat = repondre(sys.argv[1], Recherche(config["strategie"]), config)
    print(f"\nRéponse ({resultat['duree_s']} s) :\n{resultat['reponse']}\n")
    if resultat["abstention"]:
        print(f"Abstention, motif : {resultat['motif']}")
        if resultat["brut"]:
            print(f"Texte brut du modèle : {resultat['brut']}")
    print("Sources fournies au modèle :")
    for s in resultat["sources"]:
        cite = (
            "citée"
            if resultat["analyse"]
            and int(s["label"][1:]) in resultat["analyse"]["cites"]
            else "     "
        )
        print(
            f"  [{s['label']}] {cite} score {s['score']:.3f}  {s['reference']}\n        {s['url']}"
        )


if __name__ == "__main__":
    main()
