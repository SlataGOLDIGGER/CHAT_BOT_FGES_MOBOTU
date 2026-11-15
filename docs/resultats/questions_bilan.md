# Bilan des questions d'entraînement et de développement (NLP-42)

Date : 15/11/2026 · base de départ : commit de main `4b00bf5`. Après correction D14, `python -m scripts.valider_questions --test` affiche « Questions conformes » pour les trois ensembles.

**Statut : jeux corrigés localement.** D14 a changé onze affectations de familles F1882. Seize questions d'entraînement et quatre de développement ont été remplacées pour respecter le nouveau partage ; douze autres lignes ont été révisées pour lever des ambiguïtés, citations manquantes ou doublons. La métadonnée `famille` de `dev-P3-002` a aussi été corrigée. Le champ `auteur` conserve le rôle propriétaire initial de chaque ligne ; ces 32 révisions ont été rédigées par SLATA avec assistance IA le 15/11/2026. Cette provenance doit figurer dans le Journal IA de l'équipe.

| Auteur | Entraînement (dont hors corpus) | Développement (dont hors corpus) |
|---|---|---|
| P1 | 30 (7) | 10 (2) |
| P2 | 30 (7) | 10 (2) |
| P3 | 30 (7) | 10 (2) |
| P5 | 30 (7) | 10 (2) |
| Total | 120 (28) | 40 (8) |

Couverture après D14 : **32 familles d'entraînement sur 37** (minimum requis : 30), **12 familles de développement sur 12**. Avant D14, le validateur annonçait 36/37 et 11/12, tout en laissant passer des règles équivalentes dans plusieurs ensembles.

Avant D14, `F1882-5.4` n'était la famille d'aucune question d'entraînement, bien qu'elle apparaisse en section secondaire de `train-P2-019` ; le minimum de 30 familles était tout de même atteint. En développement, `F32131-4` n'était la famille principale d'aucune question alors qu'elle était citée par `dev-P3-002`. Sa métadonnée est désormais corrigée et la couverture atteint 12 familles.

## Défaut du tirage initial, corrigé dans D14

La version de `familles.json` du commit `4b00bf5` affectait à des ensembles différents plusieurs sections F1882 au texte identique. La saisie ne regroupait ces jumelles qu'à l'intérieur d'un même ensemble, et l'ancien validateur ne le détectait pas. Le tableau ci-dessous documente cet état antérieur ; la nouvelle répartition place chaque groupe dans un seul ensemble.

| Texte commun à | Ensembles |
|---|---|
| `F1882-4.1.c1` / `F1882-5.1.c1`, `F1882-4.1.c2` / `F1882-5.1.c2` | entraînement / développement |
| `F1882-3.1`, `F1882-4.2` / `F1882-5.2` / `F1882-2.1`, `F1882-6.2` | entraînement / développement / test |
| `F1882-1.2`, `F1882-2.2`, `F1882-3.2`, `F1882-5.4` / `F1882-4.3` | entraînement / test |

Conséquences observées avant D14 :
- Quatre questions de développement ont leur réponse dans des sections d'entraînement : dev-P1-003, dev-P1-004, dev-P2-005 et dev-P5-005. Toute question sur les familles de développement `F1882-5.1` et `F1882-5.2` est dans ce cas.
- Trois des douze familles initiales de test (`F1882-2.1`, `F1882-6.2`, `F1882-4.3`) avaient le texte de sections d'entraînement. Elles ont été réaffectées à l'entraînement avant le scellement. Le nombre et le contenu des questions de test touchées restent hors du dépôt.

## Révisions réalisées pour D14

Les questions ci-dessous ont été remplacées sous leur identifiant et rôle propriétaire d'origine, avec des sections d'or du nouvel ensemble. Les quotas par auteur et la part hors corpus sont inchangés. Une question a été remplacée dès qu'une de ses sections d'or changeait d'ensemble, même si sa famille principale restait à sa place.

| Rôle propriétaire | Entraînement remplacé | Développement remplacé |
|---|---|---|
| P1 | `train-P1-010`, `train-P1-015`, `train-P1-016`, `train-P1-017`, `train-P1-018`, `train-P1-020` | `dev-P1-004` |
| P2 | `train-P2-004` | — |
| P3 | `train-P3-001`, `train-P3-003`, `train-P3-008`, `train-P3-019`, `train-P3-021` | `dev-P3-004` |
| P5 | `train-P5-011`, `train-P5-018`, `train-P5-019`, `train-P5-021` | `dev-P5-005`, `dev-P5-007` |

Après remplacement, 32 familles d'entraînement et les 12 familles de développement sont couvertes. Les questions test touchées ont été rédigées et validées séparément sur le poste de P4 ; aucune question de test ne figure dans ce bilan.

Contrôles de sortie : `valider_questions --test` passe avec 120/40/40 questions et 28/8/10 hors corpus ; aucune phrase de référence sans citation, aucune question avec dix mots consécutifs recopiés d'une section, aucun quasi-doublon textuel entre ensembles au seuil de contrôle de 0,78. Ce dernier contrôle reste heuristique et ne remplace pas une relecture humaine.

## Suivi des corrections éditoriales

Les corrections de la colonne « Suite » sont locales à cette branche ; elles ne valent pas preuve d'une communication aux rôles propriétaires ni d'une fusion sur `main`.

| Question (identifiant) | Motif de la correction identifiée | Auteur | Suite |
|---|---|---|---|
| dev-P1-003 | réponse présente en entraînement avant D14 (`F1882-5.1.c1` = `F1882-4.1.c1`) | P1 | étanchéité corrigée et relue |
| dev-P1-004 | réponse présente en entraînement (`F1882-5.2` = `F1882-3.1`, `F1882-4.2`) | P1 | remplacée localement D14 |
| dev-P1-001 | doublon de dev-P2-001 (durée du délai de carence) | P1 | corrigée localement D14 |
| dev-P1-002 | doublon de dev-P2-004 (validation d'un stage interrompu) | P1 | corrigée localement D14 |
| train-P2-005 | ambiguë : la question porte sur les moins de 16 ans, la réponse sur les deux tranches d'âge | P2 | corrigée localement D14 |
| train-P2-008 | ambiguë : « apprenants » peut désigner des apprentis, thème hors corpus | P2 | corrigée localement D14 |
| dev-P2-005 | réponse présente en entraînement avant D14 (`F1882-5.1` = `F1882-4.1`) | P2 | étanchéité corrigée et relue |
| dev-P3-002 | champ `famille` : `F32131-4` au lieu de `F16734-5.3` | P3 | métadonnée corrigée et validée |
| dev-P5-008 | première phrase de la réponse sans citation ; doublon de dev-P2-007 | P5 | corrigée localement D14 |
| train-P5-019 | condition omise : « selon le cas applicable » ne dit pas l'âge (15 ans) | P5 | remplacée localement D14 |
| train-P5-022 | condition omise : « selon le cas applicable » ne dit pas l'âge (16 ans) | P5 | corrigée localement D14 |
| train-P5-018 | ambiguë : « un stage » sans préciser stage d'initiation | P5 | remplacée localement D14 |
| dev-P5-005 | réponse présente en entraînement (`F1882-5.2` = `F1882-3.1`, `F1882-4.2`) | P5 | remplacée localement D14 |
| dev-P5-007 | doublon de dev-P3-004 (responsabilité civile en PFMP) | P5 | remplacée localement D14 |
| dev-P5-001 | doublon de dev-P2-001 et dev-P3-005 (délai de carence et exception) | P5 | corrigée localement D14 |
| dev-P5-002 | doublon de dev-P2-002 (remboursement des transports) | P5 | corrigée localement D14 |
| dev-P5-003 | doublon de dev-P2-003 ; recopie la fiche (10 mots de suite) | P5 | corrigée localement D14 |
| dev-P5-004 | doublon de dev-P2-004 (validation d'un stage interrompu) | P5 | corrigée localement D14 |
| dev-P5-006 | doublon de dev-P2-006 (visite médicale) | P5 | corrigée localement D14 |

Règle appliquée aux doublons : deux questions du même ensemble qui appellent la même réponse comptent pour une. La question fusionnée la dernière est remplacée par une question sur une autre règle de la même famille, ou sur une autre famille de développement. Les remplacements ne portent pas sur `F1882-5.1` ni `F1882-5.2`.

Non bloquant : dev-P2-009 et dev-P5-009 (points du permis), train-P2-027 et train-P5-027 (rémunération d'un apprenti) sont formulées presque de la même façon. Les thèmes hors corpus de développement sont imposés (deux thèmes, `shared/eval/themes_hors_corpus.json`) : seul l'angle de la question peut varier.
