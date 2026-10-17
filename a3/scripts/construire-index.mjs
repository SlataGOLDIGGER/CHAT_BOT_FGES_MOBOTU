// Construit l'index statique du site pour chaque couple (modèle, stratégie de découpage).
// Usage (dossier a3/) : npm run index
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DIMENSION, MODELES, PRODUCTION, STRATEGIES } from '../src/config.js';
import { creerExtracteur, descripteur, encoder } from '../src/moteur.js';

const ICI = path.dirname(fileURLToPath(import.meta.url));
const CORPUS = path.resolve(ICI, '../../shared/corpus');
const SORTIE = path.resolve(ICI, '../public/data');
const lireJsonl = (fichier) => fs.readFileSync(fichier, 'utf8').split('\n').filter(Boolean).map(JSON.parse);
const sha256 = (donnees) => createHash('sha256').update(donnees).digest('hex');

const sections = new Map(lireJsonl(path.join(CORPUS, 'sections.jsonl')).map((s) => [s.section_id, s]));
const manifeste = JSON.parse(fs.readFileSync(path.join(CORPUS, 'manifest.json'), 'utf8'));
fs.rmSync(SORTIE, { recursive: true, force: true });
fs.mkdirSync(SORTIE, { recursive: true });

const extracteurs = {};
for (const nomModele of Object.keys(MODELES)) extracteurs[nomModele] = await creerExtracteur(nomModele, null);

const combinaisons = {};
for (const strategie of STRATEGIES) {
  const fichier = path.join(CORPUS, `passages_${strategie}.jsonl`);
  const empreintePassages = sha256(fs.readFileSync(fichier));
  const passages = lireJsonl(fichier);
  const affichage = passages.map((p) => {
    const s = sections.get(p.section_id);
    return { id: p.passage_id, section: p.section_id, reference: [s.fiche_titre, ...s.chemin].join(' › '),
      url: s.url, encode: p.texte, texte: p.texte.split('\n').slice(1).join('\n') };
  });
  const nomPassages = `passages-${strategie}-${empreintePassages.slice(0, 10)}.json`;
  fs.writeFileSync(path.join(SORTIE, nomPassages), JSON.stringify(affichage));
  for (const nomModele of Object.keys(MODELES)) {
    const debut = Date.now();
    const vecteurs = new Float32Array(passages.length * DIMENSION);
    for (const [i, p] of passages.entries()) {
      vecteurs.set(await encoder(extracteurs[nomModele], p.texte, 'passage'), i * DIMENSION);
    }
    const cle = sha256(descripteur(nomModele, strategie, empreintePassages));
    const nomVecteurs = `vecteurs-${nomModele}-${strategie}-${cle.slice(0, 10)}.bin`;
    fs.writeFileSync(path.join(SORTIE, nomVecteurs), Buffer.from(vecteurs.buffer));
    combinaisons[`${nomModele}/${strategie}`] = { passages: nomPassages, vecteurs: nomVecteurs,
      nombre: passages.length, cle, sha256Passages: empreintePassages };
    console.log(`${nomModele}/${strategie} : ${passages.length} passages encodés en ${((Date.now() - debut) / 1000).toFixed(1)} s`);
  }
}

const index = {
  production: PRODUCTION,
  combinaisons,
  modeles: MODELES,
  dimension: DIMENSION,
  versionCorpus: manifeste.version_corpus,
  versionDecoupage: manifeste.version_decoupage,
  dateCollecte: manifeste.date_collecte,
  attribution: manifeste.attribution,
  licence: manifeste.licence,
  fiches: manifeste.fiches.map((f) => ({ id: f.fiche_id, titre: f.titre, url: f.url, dateMaj: f.date_maj })),
};
fs.writeFileSync(path.join(SORTIE, 'index.json'), `${JSON.stringify(index, null, 2)}\n`);
console.log(`Index écrit dans public/data/ (${Object.keys(combinaisons).length} combinaisons)`);