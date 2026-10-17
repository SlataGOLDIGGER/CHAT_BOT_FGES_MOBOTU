// Fonctions de recherche communes au Web Worker (navigateur) et au script d'index (Node).
import { pipeline } from '@huggingface/transformers';
import { MODELES, PREFIXES } from './config.js';

export function creerExtracteur(nomModele, surProgression) {
    const { depot, revision, dtype } = MODELES[nomModele];
    return pipeline('feature-extraction', depot, { revision, dtype, progress_callback: surProgression });
}

// Un texte à la fois : avec la quantification dynamique, le vecteur dépend de la composition du lot.
export async function encoder(extracteur, texte, genre) {
    const prefixe = genre === 'requete' ? PREFIXES.requete : PREFIXES.passage;
    const sortie = await extracteur(prefixe + texte, { pooling: 'mean', normalize: true });
    return sortie.data;
}

// Vecteurs normalisés : le produit scalaire est la similarité cosinus.
export function classer(requete, matrice, dimension, k) {
    const nombre = matrice.length / dimension;
    const scores = new Float32Array(nombre);
    for (let i = 0; i < nombre; i += 1) {
        let somme = 0;
        const debut = i * dimension;
        for (let j = 0; j < dimension; j += 1) somme += requete[j] * matrice[debut + j];
        scores[i] = somme;
    }
    const ordre = Array.from(scores.keys()).sort((a, b) => scores[b] - scores[a]);
    return ordre.slice(0, k).map((indice) => ({ indice, score: scores[indice] }));
}

// Tout ce qui rend deux index comparables : si un seul élément change, l'index doit être reconstruit.
export function descripteur(nomModele, strategie, sha256Passages) {
    return JSON.stringify({
        ...MODELES[nomModele], strategie, prefixes: PREFIXES, agregation: 'mean',
        normalisation: 'l2', sha256Passages
    });
}