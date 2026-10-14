"""Récupération dense du volet B : encodeur E5 (ONNX Runtime) et similarité cosinus."""

import hashlib
import json
import pathlib

import numpy as np

from b1.rag.encodeur import Encodeur

RACINE = pathlib.Path(__file__).resolve().parents[2]
CORPUS = RACINE / "shared" / "corpus"


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [
        json.loads(l)
        for l in chemin.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


class Recherche:
    def __init__(self, strategie: str):
        self.encodeur = Encodeur()
        chemin = CORPUS / f"passages_{strategie}.jsonl"
        self.passages = lire_jsonl(chemin)
        sections = {s["section_id"]: s for s in lire_jsonl(CORPUS / "sections.jsonl")}
        for p in self.passages:
            s = sections[p["section_id"]]
            p["reference"] = " › ".join([s["fiche_titre"]] + s["chemin"])
            p["url"] = s["url"]
        empreinte = hashlib.sha256(
            chemin.read_bytes() + self.encodeur.revision.encode()
        ).hexdigest()[:12]
        cache = RACINE / "artifacts" / "b1" / "index" / f"{strategie}-{empreinte}.npy"
        if cache.exists():
            self.matrice = np.load(cache)
        else:
            print(
                f"Encodage de {len(self.passages)} passages (une seule fois, puis mis en cache)…"
            )
            self.matrice = self.encodeur.encoder_passages(
                [p["texte"] for p in self.passages]
            )
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, self.matrice)

    def chercher(self, question: str, k: int) -> list[tuple[dict, float]]:
        scores = self.matrice @ self.encodeur.encoder_requetes([question])[0]
        rangs = np.argsort(-scores)[:k]
        return [(self.passages[i], float(scores[i])) for i in rangs]
