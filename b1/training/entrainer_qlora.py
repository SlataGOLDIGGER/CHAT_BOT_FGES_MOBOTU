"""Adaptation QLoRA du générateur (GPU gratuit Kaggle ou Colab) ; mode CPU sans quantification pour les essais.

Usage sur Kaggle (depuis la racine du dépôt cloné) :
  python -m b1.training.entrainer_qlora --sortie /kaggle/working/adaptateur-v1 --micro 20   (micro-essai)
  python -m b1.training.entrainer_qlora --sortie /kaggle/working/adaptateur-v1               (entraînement)
"""

import argparse
import hashlib
import json
import math
import pathlib
import random
import time

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

RACINE = pathlib.Path(__file__).resolve().parents[2]
MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def lire(chemin: pathlib.Path) -> list[dict]:
    return [
        json.loads(l)
        for l in chemin.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


def encoder(exemple: dict, tok, longueur_max: int) -> dict:
    """Concatène prompt et complétion ; la perte ne porte que sur la complétion (masquage du prompt)."""
    ids_prompt = tok(exemple["prompt"], add_special_tokens=False)["input_ids"]
    ids_reponse = tok(exemple["completion"], add_special_tokens=False)["input_ids"]
    ids = (ids_prompt + ids_reponse)[:longueur_max]
    etiquettes = ([-100] * len(ids_prompt) + ids_reponse)[:longueur_max]
    return {"input_ids": torch.tensor([ids]), "labels": torch.tensor([etiquettes])}


def perte_moyenne(modele, lots, appareil, precision) -> float:
    modele.eval()
    total = 0.0
    with torch.no_grad():
        for lot in lots:
            with torch.autocast(appareil, dtype=precision, enabled=appareil == "cuda"):
                total += modele(
                    input_ids=lot["input_ids"].to(appareil),
                    labels=lot["labels"].to(appareil),
                ).loss.item()
    modele.train()
    return total / max(len(lots), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument(
        "--revision", default="cdbee75f17c01a7cc42f958dc650907174af0554"
    )
    parser.add_argument("--train", default="b1/training/donnees/sft_train.jsonl")
    parser.add_argument("--dev", default="b1/training/donnees/sft_dev.jsonl")
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--rang", type=int, default=16)
    parser.add_argument("--alpha", type=int, default=32)
    parser.add_argument("--dropout", type=float, default=0.05)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--epoques", type=int, default=2)
    parser.add_argument("--accumulation", type=int, default=8)
    parser.add_argument("--longueur-max", type=int, default=3072)
    parser.add_argument(
        "--micro",
        type=int,
        default=0,
        help="arrêt après N pas d'optimisation (micro-essai)",
    )
    parser.add_argument(
        "--sans-4bit", action="store_true", help="essai CPU sans quantification"
    )
    parser.add_argument("--graine", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.graine)
    torch.manual_seed(args.graine)
    appareil = "cuda" if torch.cuda.is_available() else "cpu"
    precision = torch.float16
    tok = AutoTokenizer.from_pretrained(args.base, revision=args.revision)
    if appareil == "cuda" and not args.sans_4bit:
        quantification = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=precision,
        )
        modele = AutoModelForCausalLM.from_pretrained(
            args.base,
            revision=args.revision,
            quantization_config=quantification,
            device_map={"": 0},
        )
        modele = prepare_model_for_kbit_training(
            modele, use_gradient_checkpointing=True
        )
    else:
        modele = AutoModelForCausalLM.from_pretrained(
            args.base, revision=args.revision, dtype=torch.float32
        )
        modele.to(appareil)
    modele = get_peft_model(
        modele,
        LoraConfig(
            r=args.rang,
            lora_alpha=args.alpha,
            lora_dropout=args.dropout,
            target_modules=MODULES,
            task_type="CAUSAL_LM",
        ),
    )
    modele.print_trainable_parameters()

    chemin_train, chemin_dev = RACINE / args.train, RACINE / args.dev
    train = [encoder(e, tok, args.longueur_max) for e in lire(chemin_train)]
    dev = [encoder(e, tok, args.longueur_max) for e in lire(chemin_dev)]
    pas_total = math.ceil(len(train) / args.accumulation) * args.epoques
    if args.micro:
        pas_total = min(pas_total, args.micro)
    parametres = [p for p in modele.parameters() if p.requires_grad]
    optimiseur = torch.optim.AdamW(parametres, lr=args.lr, weight_decay=0.0)
    echauffement = max(1, int(0.1 * pas_total))
    planning = torch.optim.lr_scheduler.LambdaLR(
        optimiseur,
        lambda pas: min(1.0, (pas + 1) / echauffement) * max(0.0, 1 - pas / pas_total),
    )
    echelle = torch.amp.GradScaler(appareil, enabled=appareil == "cuda")

    journal = {
        "base": args.base,
        "revision": args.revision,
        "hyperparametres": vars(args),
        "sha256_train": hashlib.sha256(chemin_train.read_bytes()).hexdigest(),
        "sha256_dev": hashlib.sha256(chemin_dev.read_bytes()).hexdigest(),
        "exemples_train": len(train),
        "exemples_dev": len(dev),
        "gpu": torch.cuda.get_device_name(0) if appareil == "cuda" else "cpu",
        "pertes": [],
    }
    journal["perte_dev_initiale"] = perte_moyenne(modele, dev, appareil, precision)
    print(
        f"perte dev initiale : {journal['perte_dev_initiale']:.4f} ; {pas_total} pas prévus"
    )
    debut, pas, cumul = time.time(), 0, 0.0
    modele.train()
    for epoque in range(args.epoques):
        ordre = list(range(len(train)))
        random.shuffle(ordre)
        for i, indice in enumerate(ordre, start=1):
            lot = train[indice]
            with torch.autocast(appareil, dtype=precision, enabled=appareil == "cuda"):
                perte = modele(
                    input_ids=lot["input_ids"].to(appareil),
                    labels=lot["labels"].to(appareil),
                ).loss
            echelle.scale(perte / args.accumulation).backward()
            cumul += perte.item() / args.accumulation
            if i % args.accumulation == 0 or i == len(ordre):
                echelle.unscale_(optimiseur)
                torch.nn.utils.clip_grad_norm_(parametres, 1.0)
                echelle.step(optimiseur)
                echelle.update()
                optimiseur.zero_grad(set_to_none=True)
                planning.step()
                pas += 1
                journal["pertes"].append({"pas": pas, "perte": round(cumul, 4)})
                print(
                    f"pas {pas}/{pas_total} époque {epoque + 1} perte {cumul:.4f} ({time.time() - debut:.0f} s)"
                )
                cumul = 0.0
                if pas >= pas_total:
                    break
        journal[f"perte_dev_epoque_{epoque + 1}"] = perte_moyenne(
            modele, dev, appareil, precision
        )
        print(
            f"perte dev après l'époque {epoque + 1} : {journal[f'perte_dev_epoque_{epoque + 1}']:.4f}"
        )
        if pas >= pas_total:
            break
    journal["duree_s"] = round(time.time() - debut)
    if appareil == "cuda":
        journal["memoire_max_go"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
    sortie = pathlib.Path(args.sortie)
    modele.save_pretrained(sortie)
    (sortie / "entrainement.json").write_text(
        json.dumps(journal, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Adaptateur enregistré dans {sortie}")


if __name__ == "__main__":
    main()
