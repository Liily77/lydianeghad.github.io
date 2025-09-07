// backend/sumupTokenStore.js
// Gère un access_token SumUp côté serveur (fetch + cache + refresh automatique)

const axios = require('axios');

let state = {
  access_token: null,
  // timestamp en secondes; on rafraîchit 60s avant l'expiration
  expires_at: 0,
};

const now = () => Math.floor(Date.now() / 1000);

// Choisit automatiquement les creds : PROD si présents, sinon SANDBOX
function pickCreds() {
  const useSandbox =
    String(process.env.USE_SUMUP_SANDBOX || '').toLowerCase() === 'true';

  const client_id =
    process.env.SUMUP_CLIENT_ID || process.env.SUMUP_SANDBOX_CLIENT_ID;

  const client_secret =
    process.env.SUMUP_CLIENT_SECRET || process.env.SUMUP_SANDBOX_CLIENT_SECRET;

  return { client_id, client_secret, useSandbox };
}

// Appelle l'endpoint OAuth pour obtenir un access_token
async function fetchToken() {
  const { client_id, client_secret } = pickCreds();

  if (!client_id || !client_secret) {
    throw new Error(
      'SUMUP_CLIENT_ID / SUMUP_CLIENT_SECRET manquants (ou leurs variantes SANDBOX).'
    );
  }

  const body = new URLSearchParams({
    grant_type: 'client_credentials',
    client_id,
    client_secret,
    // scope facultatif; la plupart des intégrations n'en ont pas besoin
    // scope: 'payments'
  });

  const resp = await axios.post('https://api.sumup.com/token', body.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    timeout: 15000,
  });

  const { access_token, expires_in } = resp.data || {};
  if (!access_token) {
    throw new Error('Réponse token invalide de SumUp.');
  }

  const ttl = Number(expires_in || 900); // fallback 15min si non fourni
  state.access_token = access_token;
  state.expires_at = now() + ttl - 60; // refresh 60s avant expiration

  return access_token;
}

// Retourne un token valide (rafraîchit si besoin)
async function getValidToken() {
  if (state.access_token && now() < state.expires_at) {
    return state.access_token;
  }
  return await fetchToken();
}

module.exports = {
  getValidToken,
  // optionnel: exposer l'état pour debug
  _state: state,
};
