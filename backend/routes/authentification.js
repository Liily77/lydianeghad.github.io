// backend/routes/authentification.js

const express = require('express');
const router  = express.Router();

// ─── Sandbox vs Production ───────────────────────────────────────────────
const isSandbox     = process.env.USE_SUMUP_SANDBOX === 'true';
const AUTHORIZE_URL = 'https://auth.sumup.com/authorize';

// ─── OAuth Client ID & Redirect URI ──────────────────────────────────────
const CLIENT_ID    = isSandbox
  ? process.env.SUMUP_SANDBOX_CLIENT_ID
  : process.env.SUMUP_CLIENT_ID;
const REDIRECT_URI = process.env.REDIRECT_URI;  // Doit correspondre exactement à l'URL configurée chez SumUp

// ─── Route de connexion OAuth SumUp ──────────────────────────────────────
router.get('/auth/connect', (req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     CLIENT_ID,
    redirect_uri:  REDIRECT_URI,
    scope:         'payments'
  });

  const authorizeUrl = `${AUTHORIZE_URL}?${params.toString()}`;
  console.log('→ Redirecting to SumUp OAuth:', authorizeUrl);
  res.redirect(authorizeUrl);
});

module.exports = router;
