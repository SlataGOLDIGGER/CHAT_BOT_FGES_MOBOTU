# Retour d'expérience individuel P3

## Méthodologie

Mon travail sur le volet B a suivi l'ordre imposé par les dépendances. J'ai d'abord construit la chaîne RAG v1 (MOBOTU-59, fusionnée le 13/10), puis écrit le script QLoRA et réussi son micro-essai sur Kaggle (MOBOTU-64, le 24/11), et enfin gelé la configuration et mesuré la machine de démonstration (MOBOTU-74 et MOBOTU-75, le 28/11). Le RAG venait en premier parce que les données d'adaptation reprennent son prompt et ses extraits (architecture_B1.md, section 5) : sans lui, il n'y avait rien à apprendre au modèle. Le micro-essai passait avant l'entraînement complet parce qu'il coûte peu, 20 pas d'optimisation et 520 s sur un T4. Il vérifie d'un coup que la perte est finie et baisse, que l'adaptateur s'enregistre, et quelle mémoire GPU il faut. Le 24/11, il a relevé 7,37 Go au maximum, loin des 16 Go de la carte, ce qui a permis de garder la longueur maximale de 3 072 tokens pour l'entraînement complet (B1_entrainement.md). Le gel ne pouvait venir qu'une fois l'adaptateur choisi, ici la v1 (decisions.md, D15). Pour chaque ticket, j'ai suivi le même cycle : une branche, une pull request, les contrôles automatiques, puis la fusion.

## Outillage

Kaggle m'a donné un GPU sans rien installer, pour le micro-essai du 24/11 comme pour l'affinage de l'encodeur du volet A (MOBOTU-52, fusionné le 18/11). Sur GitHub, j'ai fusionné 27 pull requests entre le 10/09 et le 28/11. Les contrôles automatiques ont tous tenu : la pull request du nouveau design du volet B a passé b1-portabilite sous Windows, Linux et macOS, en moins de six minutes par système. Le banc d'évaluation m'a servi le même jour à mesurer la machine de démonstration, où les 40 questions du développement passent en 44,8 s avec la base et en 31,3 s avec l'adapté (B1_machine_demo.md). Dans Jira, les états des tickets ont été tenus au fil du projet. Pour la charge, Jira a servi d'outil de pilotage. Le lien avec GitHub passe par la clé du ticket en tête du titre.

## Difficultés

La principale difficulté a été le retard pris dans la réalisation des différentes tâches. Le projet étant volumineux et les membres du groupe n'ayant pas tous les mêmes obligations professionnelles et scolaires, notamment en raison de leur répartition dans différents sous-groupes, il n'était pas toujours évident pour tout le monde de réaliser les tâches dans les délais. De plus, une tâche non réalisée par un membre du groupe bloque l'avancement des tâches des membres suivants et entraîne ainsi un retard de plus en plus important au fur et à mesure.

Quant à la charge de travail, le plus gros dépassement de charge est sur MOBOTU-75 : 4 h saisies pour 2 h prévues. En plus des deux passages du banc, il a fallu relever la mémoire avec top pendant le passage adapté, parce que le banc (5 921,2 Mo) et le Moniteur d'activité (4,40 Go) ne donnaient pas la même valeur (B1_machine_demo.md). L'écart total reste faible : 38 h saisies pour 36 h prévues, soit 5,6 % de plus.

## Enseignements

Sur un prochain projet, je séparerais mieux ce qui peut avancer sans la dépendance. Le script QLoRA pouvait être écrit et essayé sur des données factices bien avant le 21/11. J'ai aussi vu qu'un micro-essai de quelques minutes évite de perdre une session GPU entière, puisqu'il valide la mémoire et la perte avant le vrai calcul. Enfin, figer la configuration par un tag (b1-config-gelee, le 28/11) rend la démonstration vérifiable : il suffit de constater que git diff ne montre aucun changement depuis ce tag sur b1/rag, b1/config et le script du serveur. Ces trois réflexes se transposent en entreprise : découper le travail pour ne pas rester bloqué, tester petit avant un calcul coûteux, et versionner l'état exact de ce qu'on montre.

## Axes de progression

Sur le plan technique, j'ai écrit le script d'entraînement QLoRA et la génération de contrôle avec PEFT, mais je dois progresser sur l'évaluation. L'adaptateur v1 n'a pas été évalué sur le développement avant le gel, le seul contrôle publié montre un faux refus (B1_preuve_adaptateur.md), et le transfert de la base NF4 vers la base Q4_K_M n'est pas encore mesuré.

Sur le plan collectif, j'étais le propriétaire de la machine de démonstration sans porter plus d'un quart du volet B, le plafond fixé dans notre répartition. Cette règle a tenu, mais elle m'a placé en bout de chaîne, puisque le gel et les mesures de démonstration ne pouvaient commencer qu'après la décision sur l'adaptateur. Je veux aussi garder la relecture même quand le temps manque.
