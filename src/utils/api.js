// src/utils/api.js

/**
 * BASE = chaîne vide en prod (même domaine, on passe par le rewrite Render),
 *        URL complète en dev.
 */
export const BASE = import.meta.env.MODE === 'production'
  ? ''                      // prod → on reste sur le même domaine
  : 'http://localhost:3001';// dev  → on appelle le back local

/**
 * Fonction utilitaire pour appeler l'API.
 * @param {string} url     Chemin relatif (ex: '/api/produits')
 * @param {object} options fetch options (method, body, headers, etc.)
 * @returns {Promise<any>} JSON parsé de la réponse.
 */
export async function api(url, options = {}) {
  const res = await fetch(BASE + url, {
    credentials: 'include',    // si besoin d’envoyer cookies/jwt
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return await res.json();
}

