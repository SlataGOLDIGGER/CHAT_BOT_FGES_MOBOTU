# Vérification du site gelé

Tag : site-gele (posé le 28/11/2026 à 0 h 31) · commit : c8b8f71 · URL : https://nlp-a3-b1.vercel.app · date de vérification : 28/11/2026

| Appareil                       | Système et navigateur (versions) | Réseau     | Premier chargement jusqu'à « Moteur prêt » (s) | Rechargement (s) | Contrôles                                                                      |
| ------------------------------ | --------------------------------- | ----------- | -------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------- |
| Téléphone Samsung Galaxy S10 | Android 10, Chrome 127            | mobile (4G) | 36                                                 | 2,9              | périmètre, exemples, hors corpus, liens, pied de page : OK                    |
| Ordinateur portable MSI GL65   | Windows 11, Chrome 158            | Wi-Fi       | 7,2                                                | 0,9              | mêmes contrôles : OK ; onglet Réseau : aucune requête pendant une recherche |

Méthode : temps lus dans le message « Moteur prêt en … s » (docs/architecture_A3.md, section 5), au premier chargement puis au rechargement. Aucun des deux appareils n'est le poste qui a servi au gel.

Contrôle hors corpus : la question « Quels documents faut-il fournir à la préfecture pour obtenir une carte de séjour portant la mention stagiaire ? » reçoit la mention « proximité faible ». La question « Comment demander la prime d'activité pendant mon stage ? » ne la reçoit pas (meilleur score 0,883, relevé sur le poste du gel avant le tag), comme l'annonçait déjà la section « Seuil » de docs/resultats/A3_recherche.md. Le visiteur reste prévenu par le bloc « Non couvert », qui cite la prime d'activité.

Écarts constatés : aucun sur le site. Le tag a été posé le 28/11 à 0 h 31.

Vidéo de secours du volet A : enregistrée le 28/11, durée 2 min 25, dossier partagé « Videos », lien testé par P5 le 28/11.
