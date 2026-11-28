// Classe les questions du test scellé avec le moteur de production (pre/fenetre), hors navigateur.
// Usage (dossier a3/) : node scripts/classer_production_test.mjs <questions.jsonl> <sortie.jsonl>
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DIMENSION, NB_CLASSEMENT_EVALUATION, PRODUCTION } from '../src/config.js';
import { creerExtracteur, classer, encoder } from '../src/moteur.js';

const ICI = path.dirname(fileURLToPath(import.meta.url));
const DONNEES = path.resolve(ICI, '../public/data');

const [, , fichierQuestions, fichierSortie] = process.argv;
const index = JSON.parse(fs.readFileSync(path.join(DONNEES, 'index.json'), 'utf8'));
const { modele, strategie } = PRODUCTION;
const combinaison = index.combinaisons[`${modele}/${strategie}`];
const passages = JSON.parse(fs.readFileSync(path.join(DONNEES, combinaison.passages), 'utf8'));
const vecteurs = new Float32Array(fs.readFileSync(path.join(DONNEES, combinaison.vecteurs)).buffer);

const questions = fs.readFileSync(fichierQuestions, 'utf8').split('\n').filter(Boolean).map(JSON.parse);
const extracteur = await creerExtracteur(modele, null);

const sortie = fs.createWriteStream(fichierSortie);
for (const q of questions) {
  const vecteurRequete = await encoder(extracteur, q.question, 'requete');
  const top = classer(vecteurRequete, vecteurs, DIMENSION, NB_CLASSEMENT_EVALUATION);
  const classement = top.map(({ indice, score }) => ({
    section_id: passages[indice].section,
    passage_id: passages[indice].id,
    score,
  }));
  sortie.write(JSON.stringify({ qid: q.qid, combinaison: `${modele}/${strategie}`, classement }) + '\n');
  console.log(`${q.qid} classé`);
}
sortie.end();
