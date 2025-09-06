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
 * - Ajoute automatiquement Content-Type si JSON
 * - En cas de 401 → supprime le token admin et redirige vers /admin
 * @param {string} url     Chemin relatif (ex: '/api/produits')
 * @param {object} options fetch options
 * @returns {Promise<any>} JSON parsé ou texte brut
 */
export async function api(url, options = {}) {
  const fullUrl = `${BASE}${url}`

  const res = await fetch(fullUrl, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  // Gestion auto des erreurs
  if (res.status === 401) {
    // 🔒 Token expiré ou invalide → logout
    sessionStorage.removeItem('admin_token')
    if (window.location.pathname !== '/admin') {
      window.location.href = '/admin'
    }
    throw new Error('401 Unauthorized')
  }

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`)
  }

  // Retourne JSON si dispo, sinon texte
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) {
    return res.json()
  } else {
    return res.text()
  }
}
