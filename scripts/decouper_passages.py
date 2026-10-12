"""Construit les passages du corpus selon trois stratégies de découpage.

Usage : python -m scripts.decouper_passages
Entrée : shared/corpus/sections.jsonl
Sorties : shared/corpus/passages_section.jsonl, passages_fenetre.jsonl, passages_paragraphe.jsonl
"""
import json
import pathlib
import sys

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = RACINE / "shared" / "corpus"
MODELE = "Xenova/multilingual-e5-small"
REVISION = "761b726dd34fb83930e26aab4e9ac3899aa1fa78"
VERSION_DECOUPAGE = "1"
LIMITE = 480          # tokens par passage, préfixe « passage: » et entête compris (le modèle accepte 512)
FENETRE, PAS = 128, 96  # stratégie « fenetre » : 128 tokens de contenu, recouvrement de 32
COURT = 12            # stratégie « paragraphe » : un bloc plus court est rattaché au suivant


def charger_tokenizer() -> Tokenizer:
    chemin = hf_hub_download(MODELE, "tokenizer.json", revision=REVISION)
    return Tokenizer.from_file(chemin)


def entete(section: dict) -> str:
    return " › ".join([section["fiche_titre"]] + section["chemin"])


def compter(tok: Tokenizer, texte: str) -> int:
    return len(tok.encode("passage: " + texte).ids)


def passage(section, strategie, numero, contenu, tok):
    texte = entete(section) + "\n" + contenu
    return {
        "passage_id": f"{section['section_id']}#{strategie[0]}{numero}",
        "section_id": section["section_id"],
        "fiche_id": section["fiche_id"],
        "strategie": strategie,
        "texte": texte,
        "n_tokens": compter(tok, texte),
    }


def regrouper(blocs, tok, budget):
    """Rassemble des blocs consécutifs sans dépasser le budget de tokens."""
    groupes, courant = [], []
    for bloc in blocs:
        essai = courant + [bloc]
        if courant and compter(tok, "\n".join(essai)) > budget:
            groupes.append(courant)
            courant = [bloc]
        else:
            courant = essai
    if courant:
        groupes.append(courant)
    return groupes


def par_section(section, tok):
    budget = LIMITE - compter(tok, entete(section))
    groupes = regrouper(section["blocs"], tok, budget)
    return [passage(section, "section", i + 1, "\n".join(g), tok) for i, g in enumerate(groupes)]


def par_fenetre(section, tok):
    contenu = section["texte"]
    codage = tok.encode(contenu, add_special_tokens=False)
    positions = codage.offsets
    sorties, debut, numero = [], 0, 1
    while True:
        fin = min(debut + FENETRE, len(positions))
        extrait = contenu[positions[debut][0]:positions[fin - 1][1]]
        sorties.append(passage(section, "fenetre", numero, extrait, tok))
        if fin == len(positions):
            return sorties
        debut += PAS
        numero += 1


def par_paragraphe(section, tok):
    groupes, courant = [], []
    for bloc in section["blocs"]:
        rattacher = courant and (bloc.startswith("- ") or courant[-1].endswith(":")
                                 or compter(tok, "\n".join(courant)) < COURT)
        if rattacher:
            courant.append(bloc)
        else:
            if courant:
                groupes.append(courant)
            courant = [bloc]
    if courant:
        groupes.append(courant)
    budget = LIMITE - compter(tok, entete(section))
    sorties = []
    for groupe in groupes:
        for morceau in regrouper(groupe, tok, budget):
            sorties.append(passage(section, "paragraphe", len(sorties) + 1, "\n".join(morceau), tok))
    return sorties


def main() -> None:
    tok = charger_tokenizer()
    sections = [json.loads(l) for l in (CORPUS / "sections.jsonl").read_text(encoding="utf-8").splitlines()]
    for strategie, fonction in (("section", par_section), ("fenetre", par_fenetre), ("paragraphe", par_paragraphe)):
        passages = [p for s in sections for p in fonction(s, tok)]
        trop_longs = [p["passage_id"] for p in passages if p["n_tokens"] > 512]
        if trop_longs:
            sys.exit(f"ERREUR : passages de plus de 512 tokens : {trop_longs[:5]}")
        chemin = CORPUS / f"passages_{strategie}.jsonl"
        with open(chemin, "w", encoding="utf-8", newline="\n") as sortie:
            for p in passages:
                sortie.write(json.dumps(p, ensure_ascii=False) + "\n")
        tailles = sorted(p["n_tokens"] for p in passages)
        print(f"{strategie:<11} {len(passages):>4} passages, tokens médian {tailles[len(tailles) // 2]}, "
              f"max {tailles[-1]} -> {chemin.relative_to(RACINE)}")
    print(f"Version de découpage : {VERSION_DECOUPAGE}")


if __name__ == "__main__":
    main()