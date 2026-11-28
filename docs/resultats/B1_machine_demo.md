# Volet B : mesures sur la machine de démonstration

Date : 28/11/2026 · configuration : tag b1-config-gelee (commit 75d5ba1) · machine : ordinateur portable Apple Silicon (Apple M5 Pro), 24 Go de mémoire unifiée, macOS 27.2.1 · ensemble : développement (40 questions).
Ces mesures ne remplacent pas celles de l'évaluation finale (poste du détenteur du test, docs/resultats/B1_evaluation.md).

| Mesure | Base (échelle 0) | Adapté (échelle 1) |
|---|---|---|
| Démarrage du serveur avec adaptateur (« Serveur prêt en N s ») | 1 s | |
| Latence de bout en bout, médiane | 0,97 s | 0,77 s |
| Latence de bout en bout, 95ᵉ centile | 1,90 s | 1,06 s |
| Débit de génération | 89,3 tokens/s | 79,4 tokens/s |
| Mémoire résidente maximale de llama-server (banc) | 5 921,2 Mo | 6 680,1 Mo |
| Mémoire affichée par le Moniteur d'activité (maximum) | | 4,40 Go |

Lecture : sur cette machine, llama.cpp calcule sur la puce graphique grâce à Metal, et une question prend moins d'une seconde en médiane, récupération comprise. Les 40 questions passent en 44,8 s pour la base et en 31,3 s pour l'adapté. Le débit est un peu plus bas avec l'adaptateur (79,4 contre 89,3 tokens/s), ce qui est logique puisque ses matrices s'ajoutent au calcul. Le traitement du prompt, qui fait 812 tokens en moyenne avec les cinq extraits, passe d'ailleurs de 0,38 à 0,50 s par question. L'adapté reste pourtant le plus rapide, parce que ses sorties sont beaucoup plus courtes (21 tokens en moyenne contre 63 pour la base) et que la durée de génération dépend surtout du nombre de tokens écrits. Le débit de la base est proche de celui de la première génération de MOBOTU-29 (92,0 tokens/s sur une question courte, sans extraits) : la longueur du prompt change donc peu la vitesse d'écriture.

Côté mémoire, le Moniteur d'activité affiche au plus 4,40 Go pour llama-server. C'est environ 0,8 Go de plus que l'estimation de la section 3 de docs/architecture_B1.md pour le serveur seul (poids, cache clé-valeur, tampons de calcul et adaptateur, de 3,4 à 3,6 Go) ; le reste de l'estimation (encodeur, Python et Streamlit) concerne d'autres processus. La mémoire lue par le banc est plus haute (5 921,2 puis 6 680,1 Mo) parce qu'elle ne mesure pas la même chose : le banc lit la mémoire résidente du processus, qui compte aussi les pages du fichier du modèle présentes en mémoire, alors que le Moniteur affiche son empreinte mémoire. Dans les deux cas, on reste loin des 24 Go de la machine. Le maximum du Moniteur a été relevé toutes les 2 secondes pendant le passage adapté avec la commande top (colonne MEM), qui donne la même valeur que la colonne « Mémoire » du Moniteur : 4,33 Go dans les deux cas, serveur au repos après les mesures.

Les indicateurs de qualité affichés par score_auto sur cette machine ne sont pas publiés : le calcul Metal peut différer légèrement du calcul sur processeur ; seuls latence, débit et mémoire sont retenus ici.
