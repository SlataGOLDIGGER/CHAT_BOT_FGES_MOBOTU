"""Exécute la chaîne RAG sur un fichier de questions et enregistre sorties, durées, mémoire et configuration.

Usage (serveur lancé dans un autre terminal) :
  python -m b1.eval.executer --questions shared/eval/questions_dev.jsonl --echelle 0 --nom dev-base
  python -m b1.eval.executer --questions shared/eval/questions_dev.jsonl --echelle 1 --nom dev-adapte
Test scellé (P4 uniquement) : ajouter --scelle et une --sortie hors du dépôt.
"""
import argparse
import hashlib
import json
import pathlib
import platform
import sys
import time

import psutil

from b1.rag.client_llm import etat_serveur
from b1.rag.pipeline import charger_config, repondre
from b1.rag.recherche import Recherche, lire_jsonl

RACINE = pathlib.Path(__file__).resolve().parents[2]


def memoire_serveur_mo() -> float | None:
    etat = RACINE / "artifacts" / "b1" / "serveur.json"
    if not etat.exists():
        return None
    try:
        return psutil.Process(json.loads(etat.read_text(encoding="utf-8"))["pid"]).memory_info().rss / 2**20
    except psutil.Error:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True)
    parser.add_argument("--echelle", type=float, choices=[0.0, 1.0], help="échelle de l'adaptateur (absent : aucun)")
    parser.add_argument("--nom", required=True)
    parser.add_argument("--sortie", help="dossier de sortie (défaut : artifacts/b1/runs/<nom>)")
    parser.add_argument("--limite", type=int, default=0, help="n'exécuter que les N premières questions")
    parser.add_argument("--scelle", action="store_true", help="vérifier l'empreinte du test scellé avant exécution")
    args = parser.parse_args()

    chemin = pathlib.Path(args.questions).expanduser().resolve()
    empreinte = hashlib.sha256(chemin.read_bytes()).hexdigest()
    if args.scelle:
        attendu = json.loads((RACINE / "shared" / "eval" / "test_scelle.json").read_text(encoding="utf-8"))["sha256"]
        if empreinte != attendu:
            sys.exit("ERREUR : l'empreinte du fichier ne correspond pas au test scellé")
        print("Empreinte du test scellé vérifiée.")
    questions = lire_jsonl(chemin)[: args.limite or None]
    serveur = etat_serveur()
    if args.echelle is not None and not serveur["adaptateurs"]:
        sys.exit("ERREUR : --echelle demandée mais aucun adaptateur n'est chargé par le serveur")

    config = charger_config()
    recherche = Recherche(config["strategie"])
    sortie = pathlib.Path(args.sortie).expanduser() if args.sortie else RACINE / "artifacts" / "b1" / "runs" / args.nom
    sortie.mkdir(parents=True, exist_ok=True)
    debut, pic = time.time(), 0.0
    with open(sortie / "sorties.jsonl", "w", encoding="utf-8", newline="\n") as fichier:
        for i, q in enumerate(questions, start=1):
            resultat = repondre(q["question"], recherche, config, args.echelle)
            resultat.update(qid=q["qid"], dans_corpus=q["dans_corpus"], sections_or=q["sections_or"])
            for source in resultat["sources"]:
                source.pop("texte")
            fichier.write(json.dumps(resultat, ensure_ascii=False) + "\n")
            pic = max(pic, memoire_serveur_mo() or 0.0)
            print(f"{i}/{len(questions)} {q['qid']} : {'abstention' if resultat['abstention'] else 'réponse'} "
                  f"({resultat['duree_s']} s)")
    execution = {
        "nom": args.nom, "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "echelle_lora": args.echelle,
        "questions": {"fichier": chemin.name, "sha256": empreinte, "nombre": len(questions)},
        "config_rag": config, "serveur": serveur, "memoire_max_serveur_mo": round(pic, 1),
        "memoire_totale_machine_go": round(psutil.virtual_memory().total / 2**30, 1),
        "machine": {"systeme": platform.platform(), "processeur": platform.processor() or platform.machine(),
                    "coeurs_logiques": psutil.cpu_count()},
        "duree_totale_s": round(time.time() - debut, 1),
    }
    (sortie / "execution.json").write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Terminé en {execution['duree_totale_s']} s -> {sortie}")


if __name__ == "__main__":
    main()
