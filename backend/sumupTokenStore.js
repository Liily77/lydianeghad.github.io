// backend/sumupTokenStore.js
const axios = require('axios');
const mongoose = require('mongoose');

/**
 * Ce store assure :
 * - lecture d'un refresh_token persistant (Mongo ou ENV au premier run)
 * - refresh automatique de l'access_token quand il manque ou est expiré
 * - sauvegarde en base (collection 'integrations', provider: 'sumup')
 *
 * Variables d'env nécessaires (backend):
 *  - SUMUP_CLIENT_ID
 *  - SUMUP_CLIENT_SECRET
 *  - SUMUP_REFRESH_TOKEN   (optionnel, juste pour l’amorçage la 1ère fois)
 */

const SUMUP_TOKEN_URL = 'https://api.sumup.com/token';

// --------- Modèle Mongo (léger) ----------
const IntegrationSchema = new mongoose.Schema(
  {
    provider: { type: String, unique: true, index: true },
    data:     { type: Object, default: {} }, // { access_token, refresh_token, expires_at, merchant_code, ... }
    updatedAt:{ type: Date, default: Date.now }
  },
  { collection: 'integrations' }
);

const Integration =
  mongoose.models.Integration || mongoose.model('Integration', IntegrationSchema);

// --------- Mémoire process ----------
let mem = {
  access_token: null,
  refresh_token: null,
  expires_at: 0, // epoch ms
};

// --------- Helpers ----------
function nowMs() {
  return Date.now();
}
function isAccessExpired() {
  // on prend une marge de 60s
  return !mem.access_token || !mem.expires_at || mem.expires_at - 60_000 <= nowMs();
}

async function saveToDb() {
  const payload = {
    access_token: mem.access_token || null,
    refresh_token: mem.refresh_token || null,
    expires_at: mem.expires_at || 0,
  };
  await Integration.findOneAndUpdate(
    { provider: 'sumup' },
    { provider: 'sumup', data: payload, updatedAt: new Date() },
    { upsert: true, new: true }
  );
}

async function loadFromDbOrEnvOnce() {
  // 1) DB
  const doc = await Integration.findOne({ provider: 'sumup' }).lean();
  if (doc?.data) {
    mem.access_token  = doc.data.access_token || null;
    mem.refresh_token = doc.data.refresh_token || null;
    mem.expires_at    = doc.data.expires_at || 0;
  }

  // 2) Amorçage depuis ENV si pas de refresh_token en base
  if (!mem.refresh_token) {
    const seedRefresh = process.env.SUMUP_REFRESH_TOKEN;
    if (seedRefresh) {
      mem.refresh_token = seedRefresh.trim();
      // on persiste immédiatement pour ne pas dépendre de l'ENV ensuite
      await saveToDb();
      console.log('🔑 SumUp: refresh_token initial chargé depuis ENV et sauvegardé en base.');
    }
  }
}

async function refreshAccessToken() {
  const clientId     = process.env.SUMUP_CLIENT_ID;
  const clientSecret = process.env.SUMUP_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error('SUMUP_CLIENT_ID / SUMUP_CLIENT_SECRET manquants dans les variables d’environnement');
  }
  if (!mem.refresh_token) {
    throw new Error('Aucun refresh_token SumUp disponible (renseigner SUMUP_REFRESH_TOKEN une seule fois ou connecter via OAuth)');
  }

  // grant_type=refresh_token
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: mem.refresh_token,
    client_id: clientId,
    client_secret: clientSecret,
  });

  const { data } = await axios.post(SUMUP_TOKEN_URL, body.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    timeout: 15000,
  });

  // data: { access_token, token_type, expires_in, refresh_token? ... }
  if (!data?.access_token) {
    throw new Error('Réponse SumUp sans access_token lors du refresh');
  }

  mem.access_token = data.access_token;
  // s’il renvoie un nouveau refresh_token, on le remplace
  if (data.refresh_token) {
    mem.refresh_token = data.refresh_token;
  }
  // exp en secondes -> ms
  const expiresInSec = Number(data.expires_in || 0);
  mem.expires_at = nowMs() + expiresInSec * 1000;

  await saveToDb();
  console.log('✅ SumUp: access_token rafraîchi. Expiration dans ~', expiresInSec, 's');
}

// --------- API publique du store ----------
/**
 * get() -> retourne un access_token valide, en le rafraîchissant si besoin.
 * usage: const token = await store.get()
 */
async function get() {
  // charge DB/ENV au premier appel du process
  if (!mem._loadedOnce) {
    await loadFromDbOrEnvOnce();
    mem._loadedOnce = true;
  }

  if (isAccessExpired()) {
    await refreshAccessToken();
  }
  return mem.access_token;
}

// Optionnel : utilitaires pour debug/admin si besoin
async function status() {
  return {
    has_refresh: Boolean(mem.refresh_token),
    has_access:  Boolean(mem.access_token),
    expires_at:  mem.expires_at,
    expires_in_s: mem.expires_at ? Math.max(0, Math.floor((mem.expires_at - nowMs()) / 1000)) : 0,
  };
}

module.exports = { get, status };
