import './style.css';

console.log('Volet A Semantic Search app initialized.');

const form = document.getElementById('search-form');
const input = document.getElementById('search-input');
const statusText = document.getElementById('status-text');
const resultsContainer = document.getElementById('results-container');
const resultsCount = document.getElementById('results-count');

if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    if (statusText) {
      statusText.textContent = `Recherche en cours pour : "${query}"...`;
    }

    if (resultsContainer) {
      resultsContainer.innerHTML = `
        <div class="result-card">
          <div class="result-header">
            <span class="score-badge">Score : 0.94</span>
            <span class="passage-id">Passage #1</span>
          </div>
          <p class="result-text">Exemple de passage sémantiquement similaire trouvé pour la requête "${query}".</p>
        </div>
      `;
    }

    if (resultsCount) {
      resultsCount.textContent = '1 résultat';
    }
  });
}
