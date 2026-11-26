# Performances du site du volet A

Date : 25/11/2026 · commit de production : b876001 · URL : https://nlp-a3-b1.vercel.app · ordinateur : P3 (macOS 27.2.1, Apple M5 Pro, 24 Go) · connexion : ordinateur en Wi-Fi, téléphone en 4G · téléphone : Samsung Galaxy S10, Android 10, Chrome 127

| Navigateur (version) | Transféré au 1er chargement | « Moteur prêt » 1er chargement (s) | « Moteur prêt » rechargement (s) | Latence médiane (ms) | Latence 95ᵉ centile (ms) | cosinusMin / cosinusMoyen (passages comparés) |
|---|---|---|---|---|---|---|
| Safari 27.2 | 140,4 Mo | 10,3 | 0,8 | 36 | 39 | 0,9976 / 0,9988 (113) |
| Chrome 158 | 118,4 Mo | 8,9 | 1,0 | 48 | 68 | 0,9976 / 0,9988 (113) |
| Firefox 161 | 163,2 Mo | 10,7 | 1,0 | 32 | 37 | 0,9976 / 0,9988 (113) |
| Mobile Chrome 127 (réseau mobile 4G) | (ordinateur) | 41,6 | 3,9 | 59 (5 questions) | 78 (5 questions) | 0,9976 / 0,9987 (20) |

Méthode : docs/architecture_A3.md, section 5 ; 20 questions fixes (fiche de mesure), latence lue dans la durée affichée par le site ; centile par la méthode du rang le plus proche.

Lecture : au premier passage, le site télécharge entre 118 et 163 Mo selon le navigateur, et c'est surtout le modèle d'encodage qui pèse. Il faut donc 9 à 11 s sur ordinateur avant de pouvoir chercher, et 42 s sur le téléphone en 4G, ce qui reste long pour un visiteur pressé. Le cache change beaucoup les choses : au rechargement, le moteur est prêt en 1 s environ sur ordinateur et en 4 s sur le téléphone. Une fois le moteur prêt, une recherche prend moins de 80 ms partout. Firefox est le plus rapide et le plus régulier (médiane de 32 ms, 95ᵉ centile de 37 ms), Safari le suit de près (36 et 39 ms), et Chrome est un peu plus lent et plus irrégulier (48 et 68 ms). Pour encoder les 113 passages du diagnostic, Chrome et Firefox mettent environ 12 s, contre 37 s pour Safari, mais cela ne se voit pas sur une recherche isolée, qui n'encode qu'une phrase. Le cosinus minimal entre les vecteurs calculés dans le navigateur et ceux de l'index est de 0,9976 sur les quatre appareils, au-dessus du seuil de 0,99 de la décision D3. Les volumes transférés ne se comparent pas directement, car chaque navigateur compte les octets à sa façon : Firefox, par exemple, affiche 163 Mo transférés pour 276 Mo de ressources une fois décompressées.
