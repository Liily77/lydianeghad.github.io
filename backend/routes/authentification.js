const express = require('express');
const router  = express.Router();

// ─── URL OAuth fixes ─────────────────────────────────────────────────────
const AUTHORIZE_URL = 'https://api.sumup.com/authorize';

// ─── Client ID & Redirect URI ─────────────────────────────────────────────
const CLIENT_ID    = process.env.USE_SUMUP_SANDBOX === 'true'
  ? process.env.SUMUP_SANDBOX_CLIENT_ID
  : process.env.SUMUP_CLIENT_ID;
const REDIRECT_URI = process.env.REDIRECT_URI;  // Doit matcher exactement le dashboard SumUp

// ─── Route de connexion OAuth SumUp ──────────────────────────────────────
router.get('/auth/connect', (_req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     CLIENT_ID,
    redirect_uri:  REDIRECT_URI,
    scope:         'payments'
  });
  res.redirect(`${AUTHORIZE_URL}?${params.toString()}`);
});

module.exports = router;
