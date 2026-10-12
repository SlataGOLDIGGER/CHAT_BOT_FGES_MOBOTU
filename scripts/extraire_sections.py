"""Découpe chaque fiche XML en sections référencées : situations, chapitres, sous-chapitres et cas.

Usage : python -m scripts.extraire_sections
Sortie : shared/corpus/sections.jsonl (une section par ligne)
"""
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = RACINE / "shared" / "corpus"
DC = "{http://purl.org/dc/elements/1.1/}"

UNITES = {"Chapitre": "chapitre", "SousChapitre": "sous-chapitre", "Cas": "cas", "Situation": "situation"}
CONDITIONNELS = {"cas", "situation"}
ENCADRES = {"ANoter": "À noter", "Attention": "Attention", "ASavoir": "À savoir",
            "Rappel": "Rappel", "Exemple": "Exemple", "Condition": "Condition"}
IGNORES = {"Titre", "TitreRiche", "ServiceEnLigne", "OuSAdresser", "Source", "Complement",
           "PourEnSavoirPlus", "Reference", "VoirAussi", "Definition", "Abreviation", "Colonne"}


def normaliser(texte: str) -> str:
    texte = texte.replace("\xa0", " ").replace("\u202f", " ")
    return re.sub(r"\s+", " ", texte).strip()


def texte_en_ligne(element: ET.Element) -> str:
    return normaliser("".join(element.itertext()))


def titre_de(element: ET.Element) -> str:
    titre = element.find("Titre")
    if titre is None:
        return ""
    paragraphe = titre.find("Paragraphe")
    return texte_en_ligne(paragraphe if paragraphe is not None else titre)


def conteneur(element: ET.Element) -> ET.Element:
    """Une Situation porte son contenu dans un élément Texte ; les autres unités le portent directement."""
    if element.tag == "Situation" and element.find("Texte") is not None:
        return element.find("Texte")
    return element


def blocs_de(element: ET.Element) -> list[str]:
    """Texte propre d'une unité, sans le contenu des unités imbriquées."""
    blocs: list[str] = []
    for enfant in element:
        balise = enfant.tag
        if balise in UNITES or balise in ("BlocCas", "ListeSituations") or balise in IGNORES:
            continue
        if balise == "Paragraphe":
            texte = texte_en_ligne(enfant)
            if texte:
                blocs.append(texte)
        elif balise == "Liste":
            for item in enfant.findall("Item"):
                lignes = blocs_de(item)
                if lignes:
                    blocs.append("- " + " ".join(lignes))
        elif balise == "Tableau":
            legende = enfant.find("TitreRiche")
            lignes = ["Tableau : " + texte_en_ligne(legende)] if legende is not None else []
            for rangee in enfant.findall("Rangée"):
                lignes.append(" | ".join(texte_en_ligne(c) for c in rangee.findall("Cellule")))
            blocs.append("\n".join(lignes))
        elif balise in ENCADRES:
            etiquette = titre_de(enfant) or ENCADRES[balise]
            interieur = blocs_de(enfant)
            if interieur:
                blocs.append(f"{etiquette} : " + "\n".join(interieur))
        else:
            blocs.extend(blocs_de(enfant))
    return blocs


def enfants_unites(element: ET.Element):
    """Unités filles dans l'ordre du document, avec leur code de position."""
    compteurs = {"chapitre": 0, "sous-chapitre": 0, "cas": 0, "situation": 0}
    for enfant in element:
        if enfant.tag in ("BlocCas", "ListeSituations"):
            for fille in enfant:
                if fille.tag in ("Cas", "Situation"):
                    genre = UNITES[fille.tag]
                    compteurs[genre] += 1
                    yield fille, genre, f"{genre[0]}{compteurs[genre]}"
        elif enfant.tag in UNITES:
            genre = UNITES[enfant.tag]
            compteurs[genre] += 1
            yield enfant, genre, str(compteurs[genre])


def parcourir(element, fiche, codes, chemin, genres, sorties, conditionnels_vus):
    contenu = conteneur(element)
    blocs = blocs_de(contenu)
    section_id = fiche["fiche_id"] + "-" + (".".join(codes) if codes else "0")
    if genres and genres[-1] in CONDITIONNELS:
        conditionnels_vus.add(section_id)
    if blocs:
        sorties.append({**fiche, "section_id": section_id, "chemin": chemin, "genres": genres,
                        "blocs": blocs, "texte": "\n".join(blocs)})
    for enfant, genre, code in enfants_unites(contenu):
        parcourir(enfant, fiche, codes + [code], chemin + [titre_de(enfant)],
                  genres + [genre], sorties, conditionnels_vus)


def extraire_fiche(chemin_xml: pathlib.Path):
    racine = ET.parse(chemin_xml).getroot()
    fiche = {
        "fiche_id": racine.get("ID"),
        "fiche_titre": normaliser(racine.findtext(DC + "title") or ""),
        "url": racine.get("spUrl"),
        "date_maj": (racine.findtext(DC + "date") or "").replace("modified", "").strip(),
    }
    corps = ET.Element("Corps")
    texte = racine.find("Texte")
    if texte is not None:
        corps.extend(list(texte))
    situations = racine.find("ListeSituations")
    if situations is not None:
        corps.append(situations)
    if len(corps) == 0:
        sys.exit(f"ERREUR : {chemin_xml.name} ne contient ni Texte ni ListeSituations")
    sections: list[dict] = []
    vus: set = set()
    parcourir(corps, fiche, [], [], [], sections, vus)
    attendus = len(corps.findall(".//Cas")) + len(corps.findall(".//Situation"))
    couverts = {v for v in vus if any(s["section_id"] == v or s["section_id"].startswith(v + ".") for s in sections)}
    return sections, attendus, couverts


def main() -> None:
    config = json.loads((CORPUS / "fiches.json").read_text(encoding="utf-8"))
    toutes: list[dict] = []
    erreurs = 0
    for fiche_id in config["fiches"]:
        sections, attendus, couverts = extraire_fiche(CORPUS / "source" / f"{fiche_id}.xml")
        statut = "OK" if len(couverts) == attendus else "ERREUR"
        erreurs += statut == "ERREUR"
        print(f"{fiche_id} : {len(sections)} sections, branches conditionnelles conservées "
              f"{len(couverts)}/{attendus} [{statut}]")
        toutes.extend(sections)
    identifiants = [s["section_id"] for s in toutes]
    if len(identifiants) != len(set(identifiants)):
        sys.exit("ERREUR : identifiants de section en double")
    with open(CORPUS / "sections.jsonl", "w", encoding="utf-8", newline="\n") as sortie:
        for section in toutes:
            sortie.write(json.dumps(section, ensure_ascii=False) + "\n")
    print(f"Total : {len(toutes)} sections écrites dans shared/corpus/sections.jsonl")
    if erreurs:
        sys.exit(1)


if __name__ == "__main__":
    main()