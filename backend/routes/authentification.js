const express = require('express');
const axios   = require('axios');
const router  = express.Router();

// ─── URL OAuth fixes ─────────────────────────────────────────────────────
const AUTHORIZE_URL = 'https://api.sumup.com/authorize';
const TOKEN_URL     = 'https://api.sumup.com/token';

// ─── Client ID & Redirect URI ─────────────────────────────────────────────
const CLIENT_ID     = process.env.USE_SUMUP_SANDBOX === 'true'
  ? process.env.SUMUP_SANDBOX_CLIENT_ID
  : process.env.SUMUP_CLIENT_ID;
const CLIENT_SECRET = process.env.USE_SUMUP_SANDBOX === 'true'
  ? process.env.SUMUP_SANDBOX_CLIENT_SECRET
  : process.env.SUMUP_CLIENT_SECRET;
const REDIRECT_URI  = process.env.REDIRECT_URI;  // Doit matcher exactement le dashboard SumUp

// ─── Route de connexion OAuth SumUp ──────────────────────────────────────
router.get('/connect', (req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     CLIENT_ID,
    redirect_uri:  REDIRECT_URI,
    scope:         'payments'
  });
  res.redirect(`${AUTHORIZE_URL}?${params.toString()}`);
});

// ─── Route de callback OAuth SumUp ────────────────────────────────────────
router.get('/callback', async (req, res, next) => {
  console.log('/auth/callback reçu, req.query =', req.query);

  try {
    const code = req.query.code;
    if (!code) {
      return res.status(400).send('Code manquant');
    }

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

    const accessToken = tokenRes.data.access_token;
    console.log('access_token reçu =', accessToken);

    // TODO : persister accessToken (BDD ou session)

    // Front et back sur le même domaine : on renvoie vers la page admin de la SPA
    res.redirect('/admin');
  } catch (err) {
    next(err);
  }
});

module.exports = router;
