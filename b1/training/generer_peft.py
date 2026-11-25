"""Génère avec PEFT, sur la base quantifiée comme à l'entraînement, les réponses de l'adaptateur à des prompts du dev.

Sert à mesurer l'écart entre l'entraînement (PEFT, base NF4) et l'inférence locale (llama.cpp, base Q4_K_M).
Usage sur Kaggle, après l'entraînement :
  python -m b1.training.generer_peft --adaptateur /kaggle/working/adaptateur-v1 --sortie /kaggle/working/peft_dev20.jsonl
"""
import argparse
import json
import pathlib

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

RACINE = pathlib.Path(__file__).resolve().parents[2]
QUOTAS = {"reponse": 10, "abstention_hors_corpus": 5, "abstention_contexte": 5}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--revision", default="cdbee75f17c01a7cc42f958dc650907174af0554")
    parser.add_argument("--adaptateur", required=True)
    parser.add_argument("--dev", default="b1/training/donnees/sft_dev.jsonl")
    parser.add_argument("--sortie", required=True)
    parser.add_argument("--sans-4bit", action="store_true", help="essai CPU sans quantification")
    args = parser.parse_args()

    appareil = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(args.base, revision=args.revision)
    if appareil == "cuda" and not args.sans_4bit:
        quantification = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                             bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
        modele = AutoModelForCausalLM.from_pretrained(args.base, revision=args.revision,
                                                      quantization_config=quantification, device_map={"": 0})
    else:
        modele = AutoModelForCausalLM.from_pretrained(args.base, revision=args.revision, dtype=torch.float32)
        modele.to(appareil)
    modele = PeftModel.from_pretrained(modele, args.adaptateur)
    modele.eval()
    fin = tok.convert_tokens_to_ids("<|im_end|>")

    exemples = [json.loads(l) for l in (RACINE / args.dev).read_text(encoding="utf-8").splitlines() if l.strip()]
    retenus = []
    for type_, quota in QUOTAS.items():
        retenus += [e for e in exemples if e["type"] == type_][:quota]
    with open(args.sortie, "w", encoding="utf-8", newline="\n") as sortie:
        for i, e in enumerate(retenus, start=1):
            entree = tok(e["prompt"], add_special_tokens=False, return_tensors="pt").to(appareil)
            with torch.no_grad():
                genere = modele.generate(**entree, max_new_tokens=256, do_sample=False, eos_token_id=fin,
                                         pad_token_id=fin)
            texte = tok.decode(genere[0][entree["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            sortie.write(json.dumps({"id": e["id"], "type": e["type"], "texte": texte}, ensure_ascii=False) + "\n")
            print(f"{i}/{len(retenus)} {e['id']} ({e['type']})")
    print(f"{len(retenus)} réponses PEFT -> {args.sortie}")


if __name__ == "__main__":
    main()
