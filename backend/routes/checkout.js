// backend/routes/checkout.js
const express = require('express');
const axios = require('axios');
const router = express.Router();

// ─── Sandbox vs Production pour SumUp ──────────────────────────────────
const isSandbox = process.env.USE_SUMUP_SANDBOX === 'true';
const CHECKOUT_URL = isSandbox
  ? 'https://sandbox.sumup.com/v0.1/checkouts'
  : 'https://api.sumup.com/v0.1/checkouts';

// ─── Sélection dynamique du token OAuth ───────────────────────────────
const ACCESS_TOKEN = isSandbox
  ? process.env.SUMUP_SANDBOX_ACCESS_TOKEN
  : process.env.SUMUP_PROD_ACCESS_TOKEN;

// ─── Création d’un checkout SumUp ─────────────────────────────────────
router.post('/', async (req, res) => {
  try {
    const { amount, currency, title, orderId } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Montant invalide' });
    }

    // Appel à l’API SumUp pour créer un checkout
    const response = await axios.post(
      CHECKOUT_URL,
      {
        checkout_reference: orderId || `order_${Date.now()}`,
        amount: Number(amount),
        currency: currency || 'EUR',
        shop_name: 'Arc En Ciel',
        description: title || 'Commande Arc En Ciel'
      },
      {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    // On renvoie l’URL de paiement au front
    res.json({ checkout_url: response.data.checkout_url });
  } catch (err) {
    console.error(
      'Erreur création checkout SumUp:',
      err.response?.data || err.message
    );
    res.status(500).json({ error: 'Impossible de créer le checkout' });
  }
});

module.exports = router;
