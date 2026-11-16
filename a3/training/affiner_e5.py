"""Affine l'encodeur E5 par apprentissage contrastif puis l'exporte en ONNX quantifié.

Usage (Kaggle ou poste local, depuis la racine du dépôt) :
  python -m a3.training.affiner_e5 --strategie paragraphe --epoques 3 --sortie artifacts/a3/e5-affine
  python -m a3.training.affiner_e5 --epoques 0 --sortie artifacts/a3/e5-pre   (export du modèle préentraîné seul)
"""

import argparse
import json
import pathlib
import random
import shutil

import numpy as np
import onnxruntime as ort
import torch
from huggingface_hub import hf_hub_download
from onnxruntime.quantization import QuantType, quantize_dynamic
from transformers import AutoModel, AutoTokenizer

RACINE = pathlib.Path(__file__).resolve().parents[2]
BASE, REVISION_BASE = (
    "intfloat/multilingual-e5-small",
    "614241f622f53c4eeff9890bdc4f31cfecc418b3",
)
XENOVA, REVISION_XENOVA = (
    "Xenova/multilingual-e5-small",
    "761b726dd34fb83930e26aab4e9ac3899aa1fa78",
)
FICHIERS_TOKENIZER = [
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
]


def lire_jsonl(chemin: pathlib.Path) -> list[dict]:
    return [
        json.loads(l)
        for l in chemin.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


def moyenne(etats: torch.Tensor, masque: torch.Tensor) -> torch.Tensor:
    poids = masque.unsqueeze(-1).to(etats.dtype)
    vecteurs = (etats * poids).sum(1) / poids.sum(1).clamp(min=1e-9)
    return torch.nn.functional.normalize(vecteurs, dim=-1)


def encoder(modele, tok, textes, longueur, appareil):
    lot = tok(
        textes, padding=True, truncation=True, max_length=longueur, return_tensors="pt"
    ).to(appareil)
    return moyenne(modele(**lot).last_hidden_state, lot["attention_mask"])


def construire_paires(
    strategie: str, modele, tok, appareil
) -> list[tuple[str, str, str]]:
    """Une paire (question, passage positif, section) par question d'entraînement répondable.

    Le passage positif est, parmi les passages des sections d'or, celui que le modèle de départ juge le plus proche.
    """
    questions = [
        q
        for q in lire_jsonl(RACINE / "shared/eval/questions_train.jsonl")
        if q["dans_corpus"]
    ]
    passages = lire_jsonl(RACINE / f"shared/corpus/passages_{strategie}.jsonl")
    par_section: dict[str, list[dict]] = {}
    for p in passages:
        par_section.setdefault(p["section_id"], []).append(p)
    paires = []
    modele.eval()
    with torch.no_grad():
        for q in questions:
            candidats = [p for s in q["sections_or"] for p in par_section.get(s, [])]
            vq = encoder(modele, tok, ["query: " + q["question"]], 64, appareil)
            vp = encoder(
                modele,
                tok,
                ["passage: " + p["texte"] for p in candidats],
                256,
                appareil,
            )
            meilleur = candidats[int((vq @ vp.T).argmax())]
            paires.append((q["question"], meilleur["texte"], meilleur["section_id"]))
    return paires


def lots_sans_doublon(paires, taille, graine):
    """Mélange puis répartit les paires en lots sans deux fois la même section (faux négatifs)."""
    melange = paires[:]
    random.Random(graine).shuffle(melange)
    lots: list[list] = []
    for paire in melange:
        for lot in lots:
            if len(lot) < taille and all(paire[2] != autre[2] for autre in lot):
                lot.append(paire)
                break
        else:
            lots.append([paire])
    return lots


def entrainer(modele, tok, paires, args, appareil):
    optimiseur = torch.optim.AdamW(modele.parameters(), lr=args.lr, weight_decay=0.01)
    for epoque in range(args.epoques):
        modele.train()
        pertes = []
        for lot in lots_sans_doublon(paires, args.taille_lot, args.graine + epoque):
            vq = encoder(modele, tok, ["query: " + q for q, _, _ in lot], 64, appareil)
            vp = encoder(
                modele, tok, ["passage: " + p for _, p, _ in lot], 256, appareil
            )
            logits = vq @ vp.T / args.temperature
            perte = torch.nn.functional.cross_entropy(
                logits, torch.arange(len(lot), device=appareil)
            )
            optimiseur.zero_grad()
            perte.backward()
            torch.nn.utils.clip_grad_norm_(modele.parameters(), 1.0)
            optimiseur.step()
            pertes.append(perte.item())
        print(
            f"époque {epoque + 1}/{args.epoques} : perte moyenne {np.mean(pertes):.4f} sur {len(pertes)} lots"
        )


class Enveloppe(torch.nn.Module):
    def __init__(self, modele):
        super().__init__()
        self.modele = modele

    def forward(self, input_ids, attention_mask, token_type_ids):
        return self.modele(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        ).last_hidden_state


def exporter(modele, tok, sortie: pathlib.Path):
    (sortie / "onnx").mkdir(parents=True, exist_ok=True)
    modele.eval().to("cpu")
    exemple = tok(
        ["passage: exemple de texte pour le traçage du graphe"], return_tensors="pt"
    )
    types = torch.zeros_like(exemple["input_ids"])
    brut, quantifie = (
        sortie / "onnx" / "model.onnx",
        sortie / "onnx" / "model_quantized.onnx",
    )
    lot, longueur = (
        torch.export.Dim("batch_size"),
        torch.export.Dim("sequence_length", max=512),
    )
    axes = {
        "input_ids": {0: lot, 1: longueur},
        "attention_mask": {0: lot, 1: longueur},
        "token_type_ids": {0: lot, 1: longueur},
    }
    torch.onnx.export(
        Enveloppe(modele),
        (exemple["input_ids"], exemple["attention_mask"], types),
        str(brut),
        input_names=["input_ids", "attention_mask", "token_type_ids"],
        output_names=["last_hidden_state"],
        dynamic_shapes=axes,
        dynamo=True,
        external_data=False,
    )
    quantize_dynamic(
        str(brut),
        str(quantifie),
        per_channel=True,
        reduce_range=True,
        weight_type=QuantType.QInt8,
        op_types_to_quantize=["MatMul", "Gather"],
    )
    modele.config.save_pretrained(sortie)
    for nom in FICHIERS_TOKENIZER:
        shutil.copy(
            hf_hub_download(XENOVA, nom, revision=REVISION_XENOVA), sortie / nom
        )
    return brut, quantifie


def controler(modele, tok, chemin_onnx: pathlib.Path) -> float:
    """Compare un export ONNX au modèle PyTorch sur trois phrases."""
    phrases = [
        "query: Combien est payé un stagiaire ?",
        "passage: La gratification est versée chaque mois.",
        "passage: Le stage dure au plus six mois.",
    ]
    with torch.no_grad():
        reference = encoder(modele, tok, phrases, 256, "cpu").numpy()
    session = ort.InferenceSession(str(chemin_onnx), providers=["CPUExecutionProvider"])
    vecteurs = []
    for phrase in phrases:
        lot = tok([phrase], return_tensors="np")
        ids = lot["input_ids"].astype(np.int64)
        etats = session.run(
            None,
            {
                "input_ids": ids,
                "attention_mask": lot["attention_mask"].astype(np.int64),
                "token_type_ids": np.zeros_like(ids),
            },
        )[0]
        v = etats.mean(axis=1)[0]
        vecteurs.append(v / np.linalg.norm(v))
    cosinus = (np.array(vecteurs) * reference).sum(axis=1)
    print(f"cosinus PyTorch / {chemin_onnx.name} :", np.round(cosinus, 4))
    return float(cosinus.min())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strategie",
        default="paragraphe",
        choices=["section", "fenetre", "paragraphe"],
    )
    parser.add_argument("--epoques", type=int, default=3)
    parser.add_argument("--taille-lot", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--temperature", type=float, default=0.05)
    parser.add_argument("--graine", type=int, default=42)
    parser.add_argument("--sortie", required=True)
    args = parser.parse_args()

    torch.manual_seed(args.graine)
    appareil = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(BASE, revision=REVISION_BASE)
    modele = AutoModel.from_pretrained(
        BASE, revision=REVISION_BASE, attn_implementation="eager"
    ).to(appareil)
    if args.epoques > 0:
        paires = construire_paires(args.strategie, modele, tok, appareil)
        print(f"{len(paires)} paires question-passage, appareil {appareil}")
        entrainer(modele, tok, paires, args, appareil)
    sortie = RACINE / args.sortie
    brut, quantifie = exporter(modele, tok, sortie)
    fidelite_fp32 = controler(modele, tok, brut)
    minimum = controler(modele, tok, quantifie)
    (sortie / "entrainement.json").write_text(
        json.dumps(
            {
                "base": BASE,
                "revision_base": REVISION_BASE,
                "strategie": args.strategie,
                "epoques": args.epoques,
                "taille_lot": args.taille_lot,
                "lr": args.lr,
                "temperature": args.temperature,
                "graine": args.graine,
                "cosinus_min_fp32": fidelite_fp32,
                "cosinus_min_q8": minimum,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    brut.unlink()
    succes = fidelite_fp32 > 0.9999 and minimum > 0.998
    print(f"Modèle exporté dans {args.sortie} ; contrôle {'OK' if succes else 'ÉCHEC'}")


if __name__ == "__main__":
    main()
