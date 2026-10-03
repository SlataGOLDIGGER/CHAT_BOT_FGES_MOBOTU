import { defineConfig } from 'vite';

// BASE_PATH ne sert qu'à l'hébergement de repli dans un sous-dossier (GitHub Pages).
export default defineConfig({
  base: process.env.BASE_PATH ?? '/',
  build: { target: 'es2022', outDir: 'dist', emptyOutDir: true },
  worker: { format: 'es' },
});
