"""Première génération locale : preuve que la chaîne du volet B fonctionne sur ce poste.

Usage (serveur lancé dans un autre terminal) : python -m b1.scripts.generer_essai
Affiche le build de llama.cpp, le modèle chargé, la réponse et la vitesse de génération.
"""
from b1.rag.client_llm import etat_serveur, generer

QUESTION = "En une phrase, qu'est-ce qu'une convention de stage ?"


def main() -> None:
    etat = etat_serveur()
    prompt = f"<|im_start|>user\n{QUESTION}<|im_end|>\n<|im_start|>assistant\n"
    resultat = generer(prompt)
    vitesse = resultat["tokens_generes"] / (resultat["ms_generation"] / 1000)
    print(f"| Build llama.cpp | {etat['build']} |")
    print(f"| Modèle | {etat['modele'].replace(chr(92), '/').split('/')[-1]} ({etat['quantification']}) |")
    print(f"| Question | {QUESTION} |")
    print(f"| Réponse | {resultat['texte']} |")
    print(f"| Vitesse de génération | {vitesse:.1f} tokens/s ({resultat['tokens_generes']} tokens) |")


if __name__ == "__main__":
    main()