import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

// BASE_PATH ne sert qu'à l'hébergement de repli dans un sous-dossier (GitHub Pages).
export default defineConfig({
  base: process.env.BASE_PATH ?? '/',
  build: {
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    // Deux pages : la recherche et les mentions légales.
    rolldownOptions: {
      input: {
        main: fileURLToPath(new URL('./index.html', import.meta.url)),
        mentions: fileURLToPath(new URL('./mentions.html', import.meta.url)),
      },
    },
  },
  worker: { format: 'es' },
});
