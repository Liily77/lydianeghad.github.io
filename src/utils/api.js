// src/utils/api.js

// Base URL du backend
export const BASE = import.meta.env.VITE_BACKEND_URL || '';

/**
 * Petit wrapper fetch :
 *  - n’ajoute pas Content-Type lorsqu’on envoie du FormData
 *  - remonte le vrai message d’erreur JSON retourné par l’API
 *  - en 401: on nettoie le token admin et on renvoie vers /admin
 */
export async function api(path, options = {}) {
  const url = BASE + path;
  const isForm = options.body instanceof FormData;

  const res = await fetch(url, {
    method: options.method || 'GET',
    credentials: 'include',
    headers: {
      ...(isForm ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
    body: options.body,
  });

  // Essaye de parser la réponse
  let data = null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) {
    try {
      data = await res.json();
    } catch (_) {
      // pas de JSON lisible
    }
  } else {
    try {
      data = await res.text();
    } catch (_) {}
  }

  if (res.status === 401) {
    sessionStorage.removeItem('admin_token');
    if (window.location.pathname !== '/admin') {
      window.location.href = '/admin';
    }
    const msg = (data && (data.error || data.message)) || '401 Unauthorized';
    const err = new Error(msg);
    err.status = 401;
    err.data = data;
    throw err;
  }

  if (!res.ok) {
    const msg =
      (data && (data.error || data.message || data.error_description)) ||
      res.statusText ||
      'Erreur inconnue';
    const err = new Error(`API ${res.status}: ${msg}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}
