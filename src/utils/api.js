// src/utils/api.js

/**
 * BASE = URL du backend en prod (via VITE_BACKEND_URL),
 *        chaîne vide en dev (on fait tourner le back en localhost).
 */
export const BASE = import.meta.env.PROD
  ? import.meta.env.VITE_BACKEND_URL
  : 'http://localhost:3001'

/**
 * Wrapper fetch pour appeler l’API.
 * @param {string} url     Chemin relatif (ex: '/api/produits')
 * @param {object} options fetch options
 */
export async function api(url, options = {}) {
  const fullUrl = `${BASE}${url}`
  const res = await fetch(fullUrl, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

