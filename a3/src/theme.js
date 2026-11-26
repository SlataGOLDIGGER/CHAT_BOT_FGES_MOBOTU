// Bouton du bandeau : mode clair ou sombre au choix du visiteur, sinon celui du système.
// Le choix est posé sur <html data-theme> (style.css) et gardé dans le navigateur ;
// le petit script en tête de chaque page l'applique avant l'affichage.
const CLE = 'stages-theme';
const racine = document.documentElement;
const systemeSombre = matchMedia('(prefers-color-scheme: dark)');
const bouton = document.getElementById('bouton-theme');

const themeSysteme = () => (systemeSombre.matches ? 'dark' : 'light');
const themeAffiche = () => racine.dataset.theme ?? themeSysteme();

function garder(theme) {
    try {
        if (theme) localStorage.setItem(CLE, theme);
        else localStorage.removeItem(CLE);
    } catch {
        // Stockage refusé par le navigateur : le choix vaut seulement pour la page en cours.
    }
}

function mettreAJourBouton() {
    const sombre = themeAffiche() === 'dark';
    const action = sombre ? 'Passer en mode clair' : 'Passer en mode sombre';
    bouton.dataset.mode = sombre ? 'sombre' : 'clair';
    bouton.setAttribute('aria-label', action);
    bouton.title = action;
}

if (bouton) {
    bouton.addEventListener('click', () => {
        const voulu = themeAffiche() === 'dark' ? 'light' : 'dark';
        // Choisir le mode du système revient à ne plus rien imposer : le site le suit de nouveau.
        if (voulu === themeSysteme()) {
            delete racine.dataset.theme;
            garder(null);
        } else {
            racine.dataset.theme = voulu;
            garder(voulu);
        }
        mettreAJourBouton();
    });
    systemeSombre.addEventListener('change', mettreAJourBouton);
    mettreAJourBouton();
    bouton.hidden = false;
}
