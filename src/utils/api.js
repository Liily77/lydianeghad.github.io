// src/utils/api.js

// 1) En prod on utilise toujours des URLs relatives (/api/...),
//    en dev on pointe vers le back local.
export const BASE = import.meta.env.MODE === 'production'
  ? ''                         // prod : même domaine + rewrite Render
  : 'http://localhost:3001';   // dev : back local

console.log('🔧 API base URL →', BASE);

/**
 * Appelle l’API en préfixant avec BASE.
 * Lève une erreur si status ≠ 2xx.
 *
 * Exemple :
 *   api('/api/produits');
 *   api('/api/login', { method: 'POST', body: JSON.stringify({ ... }) });
 */
export async function api(url, options = {}) {
  const res = await fetch(BASE + url, {
    credentials: 'include', // si besoin d’envoyer cookies/jwt
    headers: {
      'Content-Type': 'application/json',
      // ...options.headers si tu veux ajouter d'autres
    },
    ...options
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}
