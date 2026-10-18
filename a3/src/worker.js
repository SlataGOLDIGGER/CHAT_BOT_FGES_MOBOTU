// Web Worker : charge l'index et le modèle, encode les questions et classe les passages, sans bloquer la page.
import { env } from '@huggingface/transformers';
import { NB_RESULTATS } from './config.js';
import { classer, creerExtracteur, descripteur, encoder } from './moteur.js';

env.allowLocalModels = false;
const envoyer = (message) => self.postMessage(message);
const base = import.meta.env.BASE_URL;
let extracteur;
let index;
let passages;
let matrice;

async function empreinte(texte) {
    const octets = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(texte));
    return [...new Uint8Array(octets)].map((o) => o.toString(16).padStart(2, '0')).join('');
}

async function cacheDisponible() {
    try {
        await caches.open('essai');
        await caches.delete('essai');
        return true;
    } catch {
        return false;
    }
}

async function initialiser({ modele, strategie }) {
    index = await (await fetch(`${base}data/index.json`, { cache: 'no-cache' })).json();
    const combinaison = index.combinaisons[`${modele}/${strategie}`];
    if (!combinaison) throw new Error(`combinaison ${modele}/${strategie} absente de l'index publié.`);
    // Clé d'invalidation : l'index publié doit avoir été calculé avec exactement la configuration du site.
    if ((await empreinte(descripteur(modele, strategie, combinaison.sha256Passages))) !== combinaison.cle) {
        throw new Error("l'index publié ne correspond pas à la configuration du modèle (reconstruire l'index).");
    }
    envoyer({ type: 'perimetre', index, combinaison: `${modele}/${strategie}` });
    const [p, v] = await Promise.all([
        fetch(`${base}data/${combinaison.passages}`).then((r) => r.json()),
        fetch(`${base}data/${combinaison.vecteurs}`).then((r) => r.arrayBuffer()),
    ]);
    passages = p;
    matrice = new Float32Array(v);
    envoyer({ type: 'progression', element: 'index', pourcentage: 100 });
    if (!(await cacheDisponible())) {
        envoyer({ type: 'avertissement', message: 'Cache du navigateur indisponible (navigation privée ?) : le modèle sera retéléchargé à chaque visite.' });
    }
    const debut = performance.now();
    extracteur = await creerExtracteur(modele, (e) => {
        if (e.status === 'progress' && e.file && e.file.endsWith('.onnx')) {
            envoyer({ type: 'progression', element: 'modele', pourcentage: e.progress, charge: e.loaded, total: e.total });
        }
    });
    await encoder(extracteur, 'initialisation', 'requete');
    envoyer({ type: 'progression', element: 'modele', pourcentage: 100 });
    envoyer({ type: 'pret', dureeMs: performance.now() - debut });
}

async function chercher(question) {
    const debut = performance.now();
    const meilleurs = classer(await encoder(extracteur, question, 'requete'), matrice, index.dimension, NB_RESULTATS);
    envoyer({
        type: 'resultats', question, dureeMs: performance.now() - debut,
        resultats: meilleurs.map(({ indice, score }) => ({ ...passages[indice], score }))
    });
}

self.onmessage = async ({ data }) => {
    try {
        if (data.type === 'initialiser') await initialiser(data);
        else if (data.type === 'chercher') await chercher(data.question);
    } catch (erreur) {
        envoyer({ type: 'erreur', message: erreur.message });
    }
};