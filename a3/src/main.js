// Interface du volet A : aucune inférence ici, tout le calcul est délégué au Web Worker.
import './style.css';
import { PRODUCTION } from './config.js';

const $ = (id) => document.getElementById(id);
const champ = $('question');
const bouton = $('bouton');
const nombre = (x, chiffres) => x.toLocaleString('fr-FR', { minimumFractionDigits: chiffres, maximumFractionDigits: chiffres });
const { modele, strategie } = PRODUCTION;

const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
worker.postMessage({ type: 'initialiser', modele, strategie });

function lien(url, texte) {
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = texte;
    return a;
}

function afficherPerimetre(index) {
    const nb = index.combinaisons[`${modele}/${strategie}`].nombre;
    $('perimetre-resume').textContent =
        `${index.fiches.length} fiches Service-Public sur les stages, découpées en ${nb} passages (collecte du ${index.dateCollecte}).`;
    $('liste-fiches').replaceChildren(...index.fiches.map((f) => {
        const item = document.createElement('li');
        item.append(lien(f.url, f.titre), ` (mise à jour du ${f.dateMaj})`);
        return item;
    }));
    $('attribution').textContent = index.attribution;
}

function afficherResultats({ question, resultats, dureeMs }) {
    $('resume-resultats').textContent =
        `${resultats.length} passages pour « ${question} » (calculés en ${nombre(dureeMs, 0)} ms).`;
    $('liste-resultats').replaceChildren(...resultats.map((r) => {
        const item = document.createElement('li');
        const reference = document.createElement('p');
        reference.className = 'reference';
        reference.textContent = `${r.reference} — similarité ${nombre(r.score, 3)}`;
        const texte = document.createElement('p');
        texte.className = 'texte';
        texte.textContent = r.texte;
        item.append(reference, texte, lien(r.url, 'Lire la fiche complète sur service-public.gouv.fr'));
        return item;
    }));
    bouton.disabled = false;
}

worker.onmessage = ({ data }) => {
    if (data.type === 'perimetre') afficherPerimetre(data.index);
    else if (data.type === 'progression') {
        $(data.element === 'index' ? 'progres-index' : 'progres-modele').value = data.pourcentage;
        if (data.total) $('taille-modele').textContent = `${nombre(data.charge / 2 ** 20, 0)} / ${nombre(data.total / 2 ** 20, 0)} Mo`;
    } else if (data.type === 'avertissement') {
        $('message-etat').textContent = data.message;
    } else if (data.type === 'pret') {
        $('message-etat').textContent = `Moteur prêt en ${nombre(data.dureeMs / 1000, 1)} s. Posez votre question.`;
        champ.disabled = false;
        bouton.disabled = false;
        champ.focus();
    } else if (data.type === 'resultats') afficherResultats(data);
    else if (data.type === 'erreur') {
        $('message-etat').textContent = `Le moteur n'a pas pu démarrer : ${data.message}`;
    }
};

$('formulaire').addEventListener('submit', (evenement) => {
    evenement.preventDefault();
    const texte = champ.value.trim();
    if (!texte) {
        $('resume-resultats').textContent = 'Saisissez une question avant de lancer la recherche.';
        return;
    }
    bouton.disabled = true;
    $('resume-resultats').textContent = 'Recherche en cours…';
    worker.postMessage({ type: 'chercher', question: texte });
});