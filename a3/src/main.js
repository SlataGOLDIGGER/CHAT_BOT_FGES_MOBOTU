// Essai de faisabilité : le Web Worker encode une phrase ; la page affiche les mesures.
import './style.css';

const sortie = document.getElementById('sortie');
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
worker.onmessage = ({ data }) => {
    if (data.type === 'progression') sortie.textContent = `Téléchargement du modèle : ${Math.round(data.pourcentage)} %`;
    else sortie.textContent = JSON.stringify(data, null, 2);
};
worker.postMessage({ type: 'essai' });