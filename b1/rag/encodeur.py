"""Encodeur E5 exécuté par ONNX Runtime : même fichier de poids que le site du volet A.

Utilisé par la récupération du RAG du volet B. Lot de 1 : les vecteurs ne dépendent pas de la composition du lot.
"""

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

MODELE_PAR_DEFAUT = "Xenova/multilingual-e5-small"
REVISION_PAR_DEFAUT = "761b726dd34fb83930e26aab4e9ac3899aa1fa78"
FICHIER_ONNX = "onnx/model_quantized.onnx"
PREFIXE_REQUETE = "query: "
PREFIXE_PASSAGE = "passage: "


class Encodeur:
    def __init__(
        self,
        depot: str = MODELE_PAR_DEFAUT,
        revision: str = REVISION_PAR_DEFAUT,
        fichier_onnx: str = FICHIER_ONNX,
        lot: int = 1,
    ):
        chemin_tok = hf_hub_download(depot, "tokenizer.json", revision=revision)
        chemin_onnx = hf_hub_download(depot, fichier_onnx, revision=revision)
        self.depot, self.revision, self.fichier_onnx, self.lot = (
            depot,
            revision,
            fichier_onnx,
            lot,
        )
        self.tok = Tokenizer.from_file(chemin_tok)
        self.tok.enable_truncation(max_length=512)
        self.tok.enable_padding(pad_id=self.tok.token_to_id("<pad>"), pad_token="<pad>")
        options = ort.SessionOptions()
        options.log_severity_level = 3
        self.session = ort.InferenceSession(
            chemin_onnx, options, providers=["CPUExecutionProvider"]
        )
        self.entrees = {e.name for e in self.session.get_inputs()}

    def _encoder(self, textes: list[str]) -> np.ndarray:
        vecteurs = []
        for debut in range(0, len(textes), self.lot):
            codages = self.tok.encode_batch(textes[debut : debut + self.lot])
            ids = np.array([c.ids for c in codages], dtype=np.int64)
            masque = np.array([c.attention_mask for c in codages], dtype=np.int64)
            entrees = {"input_ids": ids, "attention_mask": masque}
            if "token_type_ids" in self.entrees:
                entrees["token_type_ids"] = np.zeros_like(ids)
            etats = self.session.run(None, entrees)[0]
            poids = masque[:, :, None].astype(np.float32)
            moyenne = (etats * poids).sum(axis=1) / np.clip(
                poids.sum(axis=1), 1e-9, None
            )
            vecteurs.append(moyenne / np.linalg.norm(moyenne, axis=1, keepdims=True))
        return np.concatenate(vecteurs).astype(np.float32)

    def encoder_requetes(self, questions: list[str]) -> np.ndarray:
        return self._encoder([PREFIXE_REQUETE + q for q in questions])

    def encoder_passages(self, passages: list[str]) -> np.ndarray:
        return self._encoder([PREFIXE_PASSAGE + p for p in passages])
