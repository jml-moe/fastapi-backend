import { defineConfig } from 'astro/config';

// Build statis: hasilnya (frontend/dist) disajikan FastAPI dari satu origin.
// Saat `astro dev`, panggilan API diteruskan ke FastAPI di :8000.
const API = 'http://localhost:8000';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  vite: {
    server: {
      proxy: {
        '/auth': API,
        '/admin': API,
        '/technologies': API,
        '/recommendations': API,
      },
    },
  },
});
