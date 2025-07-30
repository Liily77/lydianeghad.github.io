// src/utils/api.js

// 1) En prod on utilise la variable VITE_BACKEND_URL,
//    sinon localhost en dev.
export const BASE = import.meta.env.MODE === 'production'
  ? import.meta.env.VITE_BACKEND_URL
  : 'http://localhost:3001';

console.log('🔧 API base URL →', BASE); // pour debug

/**
 * Appelle l’API en préfixant avec BASE.
 * Lève une erreur si status ≠ 2xx.
 */
export async function api(url, options = {}) {
  const res = await fetch(BASE + url, {
    credentials: 'include', // si besoin d’envoyer cookies/jwt
    ...options
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}
