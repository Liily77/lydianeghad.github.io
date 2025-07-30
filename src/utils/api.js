// En prod on fait des appels relatifs (/api/… réécrit par Render vers ton backend),
// en dev on pointe vers le backend local.
export const BASE = import.meta.env.MODE === 'production'
  ? ''                       // prod → on reste sur le même domaine
  : 'http://localhost:3001'; // dev  → back local

console.log('🔧 API base URL →', BASE);

/**
 * Appelle l’API en préfixant avec BASE.
 * Lève une erreur si status ≠ 2xx.
 *
 * Exemples :
 *   api('/api/produits');
 *   api('/api/login', { method: 'POST', body: JSON.stringify({ username, password }) });
 */
export async function api(url, options = {}) {
  const res = await fetch(BASE + url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}
