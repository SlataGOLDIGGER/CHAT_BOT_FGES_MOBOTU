// Interface du volet A : aucune inférence ici, tout le calcul est délégué au Web Worker.
import './style.css';
import { MODELES, PRODUCTION, SEUIL_PERTINENCE, STRATEGIES } from './config.js';

const $ = (id) => document.getElementById(id);
const champ = $('question');
const bouton = $('bouton');
const exemples = [...document.querySelectorAll('.exemple')];
const nombre = (x, chiffres) => x.toLocaleString('fr-FR', { minimumFractionDigits: chiffres, maximumFractionDigits: chiffres });

// Modes réservés à l'équipe : ?evaluation, ?diagnostic, ?modele=…, ?strategie=…
const parametres = new URLSearchParams(location.search);
const modele = MODELES[parametres.get('modele')] ? parametres.get('modele') : PRODUCTION.modele;
const strategie = STRATEGIES.includes(parametres.get('strategie')) ? parametres.get('strategie') : PRODUCTION.strategie;
const combinaison = `${modele}/${strategie}`;

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
    const nb = index.combinaisons[combinaison].nombre;
    $('perimetre-resume').textContent =
        `${index.fiches.length} fiches Service-Public sur les stages, découpées en ${nb} passages (collecte du ${index.dateCollecte}).`;
    $('liste-fiches').replaceChildren(...index.fiches.map((f) => {
        const item = document.createElement('li');
        item.append(lien(f.url, f.titre), ` (mise à jour du ${f.dateMaj})`);
        return item;
    }));
    $('attribution').textContent = index.attribution;
}

function activer(actif) {
    champ.disabled = !actif;
    bouton.disabled = !actif;
    exemples.forEach((b) => { b.disabled = !actif; });
}

function afficherResultats({ question, resultats, dureeMs }) {
    $('resume-resultats').textContent =
        `${resultats.length} passages pour « ${question} » (calculés en ${nombre(dureeMs, 0)} ms).`;
    $('liste-resultats').replaceChildren(...resultats.map((r, rang) => {
        const item = document.createElement('li');
        item.className = 'resultat';
        const entete = document.createElement('div');
        entete.className = 'resultat-entete';
        const reference = document.createElement('p');
        reference.className = 'reference';
        reference.textContent = r.reference;
        const score = document.createElement('p');
        score.className = 'score';
        score.textContent = `Similarité ${nombre(r.score, 3)}`;
        if (SEUIL_PERTINENCE !== null && r.score < SEUIL_PERTINENCE) {
            score.textContent += ' · proximité faible';
            item.classList.add('faible');
        }
        entete.append(reference, score);
        const texte = document.createElement('p');
        texte.className = 'texte';
        texte.textContent = r.texte;
        const suite = lien(r.url, 'Lire la fiche complète sur service-public.gouv.fr');
        suite.setAttribute('aria-label', `Lire la fiche complète du résultat ${rang + 1}`);
        item.append(entete, texte, suite);
        return item;
    }));
    bouton.disabled = false;
}

function preparerEvaluation() {
    $('panneau-evaluation').hidden = false;
    $('evaluation-config').textContent = `Combinaison évaluée : ${combinaison} (changer avec ?evaluation&modele=…&strategie=…).`;
    $('lancer-evaluation').addEventListener('click', async () => {
        const fichier = $('fichier-questions').files[0];
        if (!fichier) {
            $('evaluation-etat').textContent = 'Choisissez d\'abord un fichier de questions.';
            return;
        }
        const questions = (await fichier.text()).split('\n').filter((l) => l.trim()).map(JSON.parse)
            .map(({ qid, question }) => ({ qid, question }));
        $('evaluation-etat').textContent = `Classement de ${questions.length} questions…`;
        worker.postMessage({ type: 'evaluer', questions, combinaison });
    });
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
        $('etat').classList.add('pret');
        activer(true);
        champ.focus();
        if (parametres.has('evaluation')) preparerEvaluation();
        if (parametres.has('diagnostic')) {
            const demande = parametres.get('diagnostic');
            worker.postMessage({ type: 'diagnostic', nombre: demande === 'tout' ? Infinity : Number(demande) || 20 });
        }
    } else if (data.type === 'resultats') afficherResultats(data);
    else if (data.type === 'evaluation-progression') {
        $('evaluation-etat').textContent = `${data.fait} / ${data.total} questions classées…`;
    } else if (data.type === 'evaluation') {
        const telechargement = $('telecharger-classement');
        telechargement.href = URL.createObjectURL(new Blob([data.contenu], { type: 'application/x-ndjson' }));
        telechargement.download = `classement-${modele}-${strategie}.jsonl`;
        telechargement.hidden = false;
        $('evaluation-etat').textContent = `${data.nombre} questions classées : téléchargez le fichier.`;
    } else if (data.type === 'diagnostic') {
        $('diagnostic').hidden = false;
        $('diagnostic').textContent = JSON.stringify(data.mesures, null, 2);
    } else if (data.type === 'erreur') {
        $('etat').classList.add('erreur');
        $('message-etat').textContent = `Le moteur n'a pas pu démarrer : ${data.message} Rechargez la page ; si le problème persiste, essayez un autre navigateur.`;
        activer(false);
    }
};

function chercher(question) {
    const texte = question.trim();
    if (!texte) {
        $('resume-resultats').textContent = 'Saisissez une question avant de lancer la recherche.';
        champ.focus();
        return;
    }
    bouton.disabled = true;
    $('resume-resultats').textContent = 'Recherche en cours…';
    worker.postMessage({ type: 'chercher', question: texte });
}

$('formulaire').addEventListener('submit', (evenement) => {
    evenement.preventDefault();
    chercher(champ.value);
});
exemples.forEach((b) => b.addEventListener('click', () => {
    champ.value = b.textContent;
    chercher(b.textContent);
}));
$('vider-cache').addEventListener('click', async () => {
    if ('caches' in window) {
        for (const nom of await caches.keys()) await caches.delete(nom);
    }
    location.reload();
});