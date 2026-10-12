"""Lance llama-server avec la configuration figée du volet B, avec ou sans adaptateur LoRA.

Usage (terminal dédié, laissé ouvert) :
  python -m b1.scripts.lancer_serveur                       # modèle de base
  python -m b1.scripts.lancer_serveur --adaptateur b1/models/adaptateur-v1.gguf
Arrêt : Ctrl+C dans ce terminal.
"""
import argparse
import json
import os
import pathlib
import secrets
import signal
import socket
import subprocess
import sys
import time

import requests

RACINE = pathlib.Path(__file__).resolve().parents[2]
VERROU = json.loads((RACINE / "b1" / "config" / "models.lock.json").read_text(encoding="utf-8"))
CONTEXTE = 4096


def port_libre(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connexion:
        return connexion.connect_ex(("127.0.0.1", port)) != 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adaptateur", help="chemin d'un adaptateur LoRA au format GGUF")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    repere = RACINE / "b1" / "runtime" / f"llama-{VERROU['llama_cpp']['version']}" / "chemin_serveur.txt"
    if not repere.exists():
        sys.exit("ERREUR : moteur absent. Exécutez d'abord : python -m b1.scripts.installer_llama")
    serveur = RACINE / repere.read_text(encoding="utf-8").strip()
    modele = RACINE / "b1" / "models" / VERROU["generateur"]["fichier"]
    if not modele.exists():
        sys.exit("ERREUR : modèle absent. Exécutez d'abord : python -m b1.scripts.telecharger_modeles")

    if not port_libre(args.port):
        sys.exit(f"ERREUR : le port {args.port} est déjà utilisé (un serveur tourne-t-il déjà ?). "
                 f"Arrêtez-le, ou relancez avec --port {args.port + 1}")

    commande = [str(serveur), "-m", str(modele), "-c", str(CONTEXTE), "-np", "1",
                "--host", "127.0.0.1", "--port", str(args.port)]
    if args.adaptateur:
        adaptateur = (RACINE / args.adaptateur).resolve()
        if not adaptateur.exists():
            sys.exit(f"ERREUR : adaptateur introuvable : {adaptateur}")
        commande += ["--lora", str(adaptateur)]
    print("Commande :", " ".join(commande))
    # Clé d'accès tirée à chaque lancement : une page web ouverte dans le navigateur ne peut pas
    # interroger le serveur local. Passée par l'environnement, elle n'apparaît pas dans la commande.
    cle = secrets.token_urlsafe(24)
    processus = subprocess.Popen(commande, env={**os.environ, "LLAMA_API_KEY": cle})
    # Arrêt demandé par le système (kill) : arrêter aussi llama-server, sinon il reste actif
    signal.signal(signal.SIGTERM, lambda *_: processus.terminate())

    url = f"http://127.0.0.1:{args.port}"
    debut = time.time()
    while time.time() - debut < 300:
        if processus.poll() is not None:
            sys.exit(f"ERREUR : llama-server s'est arrêté (code {processus.returncode}) ; lisez les messages ci-dessus")
        try:
            if requests.get(f"{url}/health", timeout=2).status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)
    else:
        processus.terminate()
        sys.exit("ERREUR : le serveur n'est pas prêt après 300 s")

    etat = {"commande": commande, "pid": processus.pid, "url": url, "cle_api": cle, "contexte": CONTEXTE,
            "adaptateur": args.adaptateur, "lancement": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sortie = RACINE / "artifacts" / "b1" / "serveur.json"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(etat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Serveur prêt sur {url} en {time.time() - debut:.0f} s (PID {processus.pid}). Ctrl+C pour l'arrêter.", flush=True)
    try:
        processus.wait()
    except KeyboardInterrupt:
        processus.terminate()
        processus.wait()
        print("Serveur arrêté.")


if __name__ == "__main__":
    main()
