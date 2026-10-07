"""Client HTTP minimal du serveur llama.cpp local (aucune API distante)."""
import json
import pathlib

import requests

ETAT = pathlib.Path(__file__).resolve().parents[2] / "artifacts" / "b1" / "serveur.json"
URL_DEFAUT = "http://127.0.0.1:8080"
REGLAGES = {"n_predict": 256, "temperature": 0.0, "top_k": 1, "seed": 42,
            "stop": ["<|im_end|>"], "cache_prompt": False}


def serveur() -> tuple[str, dict]:
    """Adresse et clé d'accès écrites par lancer_serveur (le port peut avoir été changé)."""
    if ETAT.exists():
        etat = json.loads(ETAT.read_text(encoding="utf-8"))
        return etat["url"], ({"Authorization": f"Bearer {etat['cle_api']}"} if etat.get("cle_api") else {})
    return URL_DEFAUT, {}


def generer(prompt: str, echelle_lora: float | None = None) -> dict:
    """Génère une réponse ; echelle_lora = 0 désactive l'adaptateur chargé, 1 l'active, None n'y touche pas."""
    url, entetes = serveur()
    corps = {"prompt": prompt, **REGLAGES}
    if echelle_lora is not None:
        corps["lora"] = [{"id": 0, "scale": echelle_lora}]
    reponse = requests.post(f"{url}/completion", json=corps, headers=entetes, timeout=600)
    reponse.raise_for_status()
    donnees = reponse.json()
    temps = donnees.get("timings", {})
    return {
        "texte": donnees["content"].strip(),
        "tokens_prompt": temps.get("prompt_n"),
        "tokens_generes": temps.get("predicted_n"),
        "ms_prompt": temps.get("prompt_ms"),
        "ms_generation": temps.get("predicted_ms"),
    }


def etat_serveur() -> dict:
    """Empreinte de la configuration réellement chargée : build, modèle, adaptateurs et leur échelle."""
    url, entetes = serveur()
    proprietes = requests.get(f"{url}/props", headers=entetes, timeout=10).json()
    adaptateurs = requests.get(f"{url}/lora-adapters", headers=entetes, timeout=10).json()
    return {
        "build": proprietes.get("build_info"),
        "modele": proprietes.get("model_path"),
        "quantification": proprietes.get("model_ftype"),
        "contexte": proprietes.get("default_generation_settings", {}).get("n_ctx"),
        "adaptateurs": adaptateurs,
    }
