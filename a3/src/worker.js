// Essai de faisabilité : charger le modèle dans un Web Worker et encoder une question.
import { env } from '@huggingface/transformers';
import { creerExtracteur, encoder } from './moteur.js';

env.allowLocalModels = false;

self.onmessage = async () => {
    try {
        const debut = performance.now();
        const extracteur = await creerExtracteur('pre', (e) => {
            if (e.status === 'progress' && e.file && e.file.endsWith('.onnx')) {
                self.postMessage({ type: 'progression', pourcentage: e.progress });
            }
        });
        const chargementMs = performance.now() - debut;
        const t = performance.now();
        const vecteur = await encoder(extracteur, 'Combien est payé un stagiaire ?', 'requete');
        const encodageMs = performance.now() - t;
        self.postMessage({
            type: 'resultat',
            dimension: vecteur.length,
            valeursFinies: vecteur.every(Number.isFinite),
            norme: Math.sqrt(vecteur.reduce((s, x) => s + x * x, 0)),
            chargementMs: Math.round(chargementMs),
            encodageMs: Math.round(encodageMs),
            premieresValeurs: Array.from(vecteur.slice(0, 5)),
            navigateur: navigator.userAgent,
        });
    } catch (erreur) {
        self.postMessage({ type: 'erreur', message: erreur.message });
    }
};