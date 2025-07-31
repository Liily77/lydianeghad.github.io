const express = require('express');
const router  = express.Router();

router.get('/auth/connect', (req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     process.env.SUMUP_CLIENT_ID,
    redirect_uri:  process.env.REDIRECT_URI,
    scope:         'transactions.checkout'
  });
  res.redirect(`https://api.sumup.com/authorize?${params.toString()}`);
});

module.exports = router;
