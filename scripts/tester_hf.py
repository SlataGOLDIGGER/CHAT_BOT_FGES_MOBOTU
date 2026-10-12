"""Vérifie que le jeton Hugging Face du poste fonctionne : identité du compte et téléchargement authentifié.

Usage : python -m scripts.tester_hf
Le jeton est lu là où « hf auth login » l'a rangé (hors du dépôt) ou dans la variable HF_TOKEN.
"""
import sys

from huggingface_hub import HfApi, get_token, hf_hub_download

DEPOT, REVISION = "Xenova/multilingual-e5-small", "761b726dd34fb83930e26aab4e9ac3899aa1fa78"


def main() -> None:
    jeton = get_token()
    if not jeton:
        sys.exit("ERREUR : aucun jeton trouvé. Exécutez « hf auth login » puis relancez ce test.")
    identite = HfApi().whoami(token=jeton)
    droits = identite.get("auth", {}).get("accessToken", {}).get("role", "inconnu")
    print(f"Appel whoami réussi : compte authentifié, rôle du jeton « {droits} »")
    chemin = hf_hub_download(DEPOT, "config.json", revision=REVISION, token=jeton, force_download=True)
    print(f"Téléchargement authentifié réussi : {DEPOT}@{REVISION[:8]} config.json -> {chemin}")
    if droits not in ("read", "fineGrained"):
        print("ATTENTION : utilisez un jeton en lecture seule (Read) ou à granularité fine limité à la lecture.")


if __name__ == "__main__":
    main()
