const express = require('express');
const axios   = require('axios');
const store   = require('../sumupTokenStore'); // ← on stocke le token ici
const router  = express.Router();

// ─── URL OAuth fixes ─────────────────────────────────────────────────────
const AUTHORIZE_URL = 'https://api.sumup.com/authorize';
const TOKEN_URL     = 'https://api.sumup.com/token';

// ─── Client ID & Redirect URI ─────────────────────────────────────────────
const IS_SANDBOX    = process.env.USE_SUMUP_SANDBOX === 'true';
const CLIENT_ID     = IS_SANDBOX ? process.env.SUMUP_SANDBOX_CLIENT_ID     : process.env.SUMUP_CLIENT_ID;
const CLIENT_SECRET = IS_SANDBOX ? process.env.SUMUP_SANDBOX_CLIENT_SECRET : process.env.SUMUP_CLIENT_SECRET;
const REDIRECT_URI  = process.env.REDIRECT_URI; // doit matcher le dashboard SumUp

// ─── Lancer l’OAuth SumUp ────────────────────────────────────────────────
router.get('/connect', (_req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     CLIENT_ID,
    redirect_uri:  REDIRECT_URI,
    scope:         'payments'
    // Astuce si besoin de forcer l’écran d’autorisation à réapparaître :
    // prompt: 'consent'
  });
  res.redirect(`${AUTHORIZE_URL}?${params.toString()}`);
});

// ─── Callback OAuth : échange code → token et mémorise ───────────────────
router.get('/callback', async (req, res, next) => {
  try {
    const code = req.query.code;
    if (!code) return res.status(400).send('Code manquant');

    const body = new URLSearchParams({
      grant_type:    'authorization_code',
      code,
      client_id:     CLIENT_ID,
      client_secret: CLIENT_SECRET,
      redirect_uri:  REDIRECT_URI
    }).toString();

    const tokenRes = await axios.post(TOKEN_URL, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const { access_token, expires_in } = tokenRes.data || {};
    if (!access_token) return res.status(500).send('Pas de token reçu');

    // ✅ on mémorise le token côté serveur (en mémoire)
    store.set(access_token, expires_in);

    // Retour à l’admin de ta SPA (même domaine)
    res.redirect('/admin');
  } catch (err) {
    next(err);
  }
});

// (optionnel) endpoint pour “déconnexion” technique (vide le token en mémoire)
router.post('/disconnect', (_req, res) => {
  store.clear();
  res.json({ ok: true });
});

module.exports = router;
