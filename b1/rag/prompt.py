"""Gabarit de prompt du volet B : identique à l'entraînement et à l'inférence."""

ABSTENTION = "Je ne trouve pas cette information dans les fiches du corpus."

SYSTEME = (
    "Tu es un assistant qui répond en français à des questions sur les stages, "
    "uniquement à partir des extraits fournis.\n"
    "Règles :\n"
    "1. N'utilise que les informations présentes dans les extraits.\n"
    "2. Termine chaque phrase de ta réponse par la référence de l'extrait qui la justifie, entre crochets, "
    "par exemple [S2].\n"
    f"3. Si les extraits ne permettent pas de répondre, réponds exactement : {ABSTENTION}\n"
    "4. Réponds en trois phrases au plus."
)


def bloc_extraits(passages: list[dict]) -> str:
    """Numérote les passages S1…Sk dans l'ordre de la récupération."""
    lignes = []
    for rang, passage in enumerate(passages, start=1):
        lignes.append(f"[S{rang}] {passage['texte']}")
    return "\n\n".join(lignes)


def construire_prompt(question: str, passages: list[dict]) -> str:
    """Prompt complet au format ChatML de Qwen, jusqu'à l'ouverture du tour de l'assistant."""
    utilisateur = f"Extraits :\n{bloc_extraits(passages)}\n\nQuestion : {question}"
    return (
        f"<|im_start|>system\n{SYSTEME}<|im_end|>\n"
        f"<|im_start|>user\n{utilisateur}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
