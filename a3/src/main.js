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
// La page reste utilisable pendant le premier chargement : une question posée avant la fin attend le moteur.
let moteurPret = false;
let questionEnAttente = null;

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
        // Le titre de la fiche, commun à beaucoup de résultats, passe en petit au-dessus du reste de la référence.
        const [titreFiche, ...parties] = r.reference.split('›').map((morceau) => morceau.trim());
        const source = document.createElement('div');
        const reference = document.createElement('p');
        reference.className = 'reference';
        if (parties.length) {
            const fiche = document.createElement('p');
            fiche.className = 'fiche';
            fiche.textContent = titreFiche;
            reference.textContent = parties.join(' › ');
            source.append(fiche, reference);
        } else {
            reference.textContent = titreFiche;
            source.append(reference);
        }
        const score = document.createElement('p');
        score.className = 'score';
        score.textContent = `Proximité de sens ${nombre(r.score, 3)}`;
        if (SEUIL_PERTINENCE !== null && r.score < SEUIL_PERTINENCE) {
            score.textContent += ' · proximité faible';
            item.classList.add('faible');
        }
        entete.append(source, score);
        const texte = document.createElement('p');
        texte.className = 'texte replie';
        texte.id = `texte-resultat-${rang + 1}`;
        // Une fenêtre qui n'est pas la première de sa section commence souvent au milieu d'une phrase.
        const milieuDePhrase = /#f\d+$/.test(r.id) && !r.id.endsWith('#f1');
        texte.textContent = milieuDePhrase ? `… ${r.texte.trimStart()}` : r.texte;
        // Sur téléphone, le texte est limité à quatre lignes (style.css) ; ce bouton l'affiche en entier.
        const lireSuite = document.createElement('button');
        lireSuite.type = 'button';
        lireSuite.className = 'lire-suite';
        lireSuite.textContent = 'Lire la suite';
        lireSuite.setAttribute('aria-controls', texte.id);
        lireSuite.setAttribute('aria-expanded', 'false');
        lireSuite.addEventListener('click', () => {
            const replie = texte.classList.toggle('replie');
            lireSuite.textContent = replie ? 'Lire la suite' : 'Réduire';
            lireSuite.setAttribute('aria-expanded', String(!replie));
        });
        // Quand la section donne un numéro de partie (F1882-2.1 donne 2), le lien ouvre et déplie cette partie.
        const numeroPartie = Number(/^F\d+-(\d+)/.exec(r.section)?.[1] ?? 0);
        const versPartie = numeroPartie >= 1 && parties.length > 0;
        const texteLien = versPartie
            ? `Lire la partie « ${parties[0]} » sur service-public.gouv.fr`
            : 'Lire la fiche complète sur service-public.gouv.fr';
        const suite = lien(versPartie ? `${r.url}#accordion-chapter-btn-${numeroPartie}` : r.url, texteLien);
        suite.setAttribute('aria-label', `${texteLien} (résultat ${rang + 1})`);
        item.append(entete, texte, lireSuite, suite);
        return item;
    }));
    ajusterLireSuite();
    bouton.disabled = false;
}

// Le bouton « Lire la suite » n'apparaît que si le passage replié dépasse vraiment quatre lignes.
function ajusterLireSuite() {
    for (const texte of document.querySelectorAll('#liste-resultats .texte.replie')) {
        texte.nextElementSibling.hidden = texte.scrollHeight <= texte.clientHeight + 1;
    }
}
matchMedia('(max-width: 600px)').addEventListener('change', ajusterLireSuite);

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
        moteurPret = true;
        $('message-etat').textContent = `Moteur prêt en ${nombre(data.dureeMs / 1000, 1)} s. Posez votre question.`;
        $('etat').classList.add('pret');
        activer(true);
        if (questionEnAttente !== null) {
            const question = questionEnAttente;
            questionEnAttente = null;
            chercher(question);
        } else if (document.activeElement === document.body) {
            champ.focus();
        }
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
        if (questionEnAttente !== null) {
            questionEnAttente = null;
            $('resume-resultats').textContent = "Recherche annulée : le moteur n'a pas pu démarrer.";
        }
    }
};

function chercher(question) {
    const texte = question.trim();
    if (!texte) {
        $('resume-resultats').textContent = 'Saisissez une question avant de lancer la recherche.';
        champ.focus();
        return;
    }
    if (!moteurPret) {
        questionEnAttente = texte;
        $('resume-resultats').textContent = 'Votre recherche sera lancée dès que le moteur sera prêt.';
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