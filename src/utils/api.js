// src/utils/api.js

// Expose la constante BASE pour le monkey‑patch de fetch
export const BASE =
  import.meta.env.MODE === 'production'
    ? 'https://arcenciel-backend.onrender.com'
    : 'http://localhost:3001';

/**
 * this.$api(url, options)
 * @param {string} url - chemin relatif (ex: '/produits')
 * @param {object} options - fetch options (method, headers, body…)
 */
export async function api(url, options = {}) {
  const res = await fetch(BASE + url, options);
  if (!res.ok) throw new Error(`API ${res.status} ${res.statusText}`);
  return res.json();
}
