import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'http://localhost:3444',
  outDir: './dist',
  build: {
    inlineStylesheets: 'auto',
  },
});
