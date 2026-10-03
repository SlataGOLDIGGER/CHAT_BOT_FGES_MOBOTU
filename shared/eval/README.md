# shared/eval — questions d'évaluation

| Fichier | Contenu |
|---|---|
| `familles.json` | familles de questions (une section ; les cas et situations rattachés à leur unité parente) et ensemble de chaque famille, tiré de façon reproductible et stratifiée par fiche |
| `themes_hors_corpus.json` | thèmes publics des questions hors corpus pour l'entraînement et le développement |
| `questions_train.jsonl`, `questions_dev.jsonl` | questions, sections d'or, réponse de référence citant les sections, auteur (rôle), date |
| `test_scelle.json` | empreinte SHA-256 du fichier de test, nombre de questions, part hors corpus, date de scellement, rôle détenteur |

**Format d'une question.** `qid`, `ensemble`, `auteur`, `question`, `dans_corpus`, `sections_or`, `famille`, `reponse_ref`, `date`. Une question hors corpus a pour réponse de référence la phrase d'abstention exacte : « Je ne trouve pas cette information dans les fiches du corpus. »

**Test scellé.** Le fichier de test n'est jamais versionné, jamais envoyé sur un service en ligne et n'est ouvert qu'au moment de l'évaluation finale, sur le poste de son détenteur. Seule son empreinte est versionnée ; elle est vérifiée avant l'évaluation.
