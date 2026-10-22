import { resolve } from 'node:path';
import { defineConfig } from 'vite';

// BASE_PATH ne sert qu'à l'hébergement de repli dans un sous-dossier (GitHub Pages).
export default defineConfig({
  base: process.env.BASE_PATH ?? '/',
  build: {
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    // Deux pages : la recherche et les mentions légales.
    rollupOptions: {
      input: { index: resolve(import.meta.dirname, 'index.html'), mentions: resolve(import.meta.dirname, 'mentions.html') },
    },
  },
  worker: { format: 'es' },
});
