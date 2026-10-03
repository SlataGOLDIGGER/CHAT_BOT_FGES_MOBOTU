# shared/corpus — corpus versionné

**Source.** Jeu de données « Fiches pratiques et ressources de Service-Public.gouv.fr Particuliers » publié par la DILA sur data.gouv.fr (archive XML `vosdroits-latest.zip`, schéma 3.5), réutilisé sous Licence Ouverte / Open Licence 2.0. L'attribution complète, la date de collecte et les empreintes figurent dans `manifest.json`.

| Fichier | Contenu |
|---|---|
| `fiches.json` | liste des fiches retenues, version du corpus, adresse de l'archive |
| `source/` | fiches XML extraites de l'archive, octets conservés, et `collecte.json` (date, empreintes de l'archive et de chaque fiche) |
| `sections.jsonl` | une section par ligne : identifiant, fiche, chemin des titres, nature des unités (chapitre, sous-chapitre, cas, situation), blocs de texte |
| `passages_section.jsonl`, `passages_fenetre.jsonl`, `passages_paragraphe.jsonl` | passages selon trois stratégies de découpage, chacun précédé du chemin de titres de sa section, avec son nombre de tokens |
| `manifest.json` | source, licence, attribution, fiches (titre, lien, date de mise à jour, empreinte), version de découpage, empreintes de tous les fichiers dérivés |

**Identifiants stables.** Une section est identifiée par la fiche et la position de chaque unité dans le document : `F32131-3` (3ᵉ chapitre), `F16734-4.1` (1ᵉʳ sous-chapitre du 4ᵉ chapitre), `F32131-1.c2` (2ᵉ cas du 1ᵉʳ chapitre), `F13879-c1` (1ᵉʳ cas au niveau de la fiche). Un passage ajoute la stratégie et son rang : `F32131-3#p2`. Les fiches sources étant figées, les identifiants ne changent pas.

**Reconstruction.** `python -m scripts.collecter_fiches`, `extraire_sections`, `decouper_passages`, `construire_manifeste`, puis `python -m scripts.verifier_corpus`.
