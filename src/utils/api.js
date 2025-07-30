export const BASE = import.meta.env.MODE === 'production'
  ? import.meta.env.VITE_BACKEND_URL
  : 'http://localhost:3001';

console.log('🔧 API base URL →', BASE);    // ← juste pour debug

export async function api(url, options = {}) {
  const res = await fetch(BASE + url, options);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}
