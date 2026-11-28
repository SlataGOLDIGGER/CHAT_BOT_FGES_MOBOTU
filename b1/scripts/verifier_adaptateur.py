"""Preuve technique du chargement de l'adaptateur.

Usage :
  1. serveur lancé avec --adaptateur : python -m b1.scripts.verifier_adaptateur
     -> adaptateurs listés par le serveur, sorties à l'échelle 0 et à l'échelle 1 sur un même prompt
  2. serveur relancé sans adaptateur : python -m b1.scripts.verifier_adaptateur --sans
     -> la sortie doit être identique, au caractère près, à celle de l'échelle 0
Sortie : artifacts/b1/preuve_adaptateur.json
"""

import argparse
import hashlib
import json
import pathlib
import sys
import time

from b1.rag.client_llm import etat_serveur, generer
from b1.rag.prompt import construire_prompt

RACINE = pathlib.Path(__file__).resolve().parents[2]
SORTIE = RACINE / "artifacts" / "b1" / "preuve_adaptateur.json"
QUESTION = "Quelle est la durée maximale d'un stage dans une même entreprise ?"
EXTRAIT = {
    "texte": "Stage › Durée maximale\nLa durée du stage est de 6 mois maximum par organisme d'accueil "
    "et par année d'enseignement."
}


def ecrire(preuve: dict) -> None:
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(preuve, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(preuve, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sans", action="store_true", help="serveur relancé sans adaptateur"
    )
    args = parser.parse_args()
    prompt = construire_prompt(QUESTION, [EXTRAIT])
    etat = etat_serveur()

    if args.sans:
        if etat["adaptateurs"]:
            sys.exit(
                "ERREUR : relancer le serveur sans --adaptateur pour cette seconde étape"
            )
        if not SORTIE.exists():
            sys.exit(
                "ERREUR : exécuter d'abord la première étape, serveur lancé avec l'adaptateur"
            )
        preuve = json.loads(SORTIE.read_text(encoding="utf-8"))
        preuve["serveur_sans_adaptateur"] = etat
        preuve["sortie_sans_adaptateur"] = generer(prompt)["texte"]
        preuve["echelle_0_identique_sans_adaptateur"] = (
            preuve["sortie_sans_adaptateur"] == preuve["sortie_echelle_0"]
        )
        ecrire(preuve)
        if not preuve["echelle_0_identique_sans_adaptateur"]:
            sys.exit(
                "ERREUR : l'échelle 0 ne reproduit pas le modèle de base ; la comparaison avant/après n'est pas valide"
            )
        return

    if not etat["adaptateurs"]:
        sys.exit(
            "ERREUR : le serveur n'a chargé aucun adaptateur (relancer avec --adaptateur)"
        )
    chemin = pathlib.Path(etat["adaptateurs"][0]["path"])
    sans = generer(prompt, echelle_lora=0.0)["texte"]
    avec = generer(prompt, echelle_lora=1.0)["texte"]
    ecrire(
        {
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "serveur": etat,
            "sha256_adaptateur": hashlib.sha256(chemin.read_bytes()).hexdigest()
            if chemin.exists()
            else None,
            "sortie_echelle_0": sans,
            "sortie_echelle_1": avec,
            "sorties_differentes": sans != avec,
        }
    )
    if sans == avec:
        sys.exit(
            "ATTENTION : sorties identiques ; l'adaptateur n'a pas d'effet visible sur ce prompt"
        )


if __name__ == "__main__":
    main()
