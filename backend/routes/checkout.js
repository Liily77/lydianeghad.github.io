// backend/routes/checkout.js

const express = require('express');
const axios   = require('axios');
const router  = express.Router();

// Configuration sandbox vs production
const isSandbox    = process.env.USE_SUMUP_SANDBOX === 'true';
const CHECKOUT_URL = isSandbox
  ? 'https://sandbox.sumup.com/v0.1/checkouts'
  : 'https://api.sumup.com/v0.1/checkouts';

// Sélection dynamique du token OAuth
const ACCESS_TOKEN = isSandbox
  ? process.env.SUMUP_SANDBOX_ACCESS_TOKEN
  : process.env.SUMUP_PROD_ACCESS_TOKEN;

router.post('/', async (req, res) => {
  try {
    const { items } = req.body;
    const total = items.reduce((sum, i) => sum + i.quantity * i.unit_price, 0);

    const response = await axios.post(
      CHECKOUT_URL,
      {
        checkout_reference: `order_${Date.now()}`,
        amount: total,
        currency: 'EUR',
        shop_name: 'Arc En Ciel',
        description: 'Commande Arc En Ciel'
      },
      {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
          'Content-Type':  'application/json'
        }
      }
    );

    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Erreur création checkout SumUp:', err.response?.data || err);
    res.status(500).json({ error: 'Impossible de créer le checkout' });
  }
});

module.exports = router;
