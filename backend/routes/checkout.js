/ backend/routes/checkout.js

const express = require('express');
const axios   = require('axios');
const router  = express.Router();

// ─── Sandbox vs Production pour SumUp ──────────────────────────────────
const isSandbox    = process.env.USE_SUMUP_SANDBOX === 'true';
const CHECKOUT_URL = isSandbox
  ? 'https://sandbox.sumup.com/v0.1/checkouts'
  : 'https://api.sumup.com/v0.1/checkouts';

// ─── Sélection dynamique du token OAuth ───────────────────────────────
const ACCESS_TOKEN = isSandbox
  ? process.env.SUMUP_SANDBOX_ACCESS_TOKEN
  : process.env.SUMUP_PROD_ACCESS_TOKEN;

router.post('/', async (req, res) => {
  try {
    const { items } = req.body;
    // Calcul du total en fonction des articles reçus
    const total = items.reduce(
      (sum, item) => sum + item.quantity * item.unit_price,
      0
    );

    // Création du checkout
    const response = await axios.post(
      CHECKOUT_URL,
      {
        checkout_reference: `order_${Date.now()}`,
        amount:             total,
        currency:           'EUR',
        description:        'Commande Arc En Ciel',
        return_url:         process.env.CHECKOUT_RETURN_URL  // à définir dans .env
      },
      {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
          'Content-Type':  'application/json'
        }
      }
    );

    // On renvoie l'URL du widget de paiement
    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Erreur création checkout SumUp :', err.response?.data || err);
    res.status(500).json({ error: 'Impossible de créer le checkout' });
  }
});