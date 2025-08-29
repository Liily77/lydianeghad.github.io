// backend/routes/checkout.js
const express = require('express');
const axios   = require('axios');
const store   = require('../sumupTokenStore');
const router  = express.Router();

// SumUp
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE; // ex: M99GF6UV

router.post('/', async (req, res) => {
  try {
    // 0) Token OAuth côté serveur
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const { items, amount, currency, title, orderId } = req.body;

    // 1) Montant total
    let total;
    if (Array.isArray(items) && items.length) {
      total = items.reduce(
        (sum, i) => sum + Number(i.quantity || 0) * Number(i.unit_price || 0),
        0
      );
    } else {
      total = Number(amount);
    }
    if (!total || total <= 0) {
      return res.status(400).json({ error: 'Montant invalide' });
    }

    // 2) Payload SumUp
    const payload = {
      checkout_reference: orderId || `order_${Date.now()}`,
      amount:             Number(total.toFixed(2)),
      currency:           currency || 'EUR',
      description:        title || 'Commande Arc En Ciel',
      hosted_checkout:    { enabled: true },
      return_url: process.env.CHECKOUT_RETURN_URL || 'https://arcenciel-backend.onrender.com/panier',
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    console.log('SumUp payload →', payload);

    // 3) Appel API
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    console.log('SumUp response status:', response.status);
    console.log('SumUp response data:', response.data);

    // ⚠️ SumUp renvoie "hosted_checkout_url" (et pas "checkout_url")
    const checkoutUrl =
      response?.data?.checkout_url || response?.data?.hosted_checkout_url;

    if (!checkoutUrl) {
      return res.status(502).json({
        error: 'Réponse SumUp sans URL de paiement',
        sumup: response.data
      });
    }

    // 4) OK
    res.json({ checkoutUrl });
  } catch (err) {
    const status  = err.response?.status || 500;
    const details = err.response?.data || { message: err.message };
    console.error('Erreur création checkout SumUp:', details);
    res.status(status).json({
      error: details?.message || details?.error_message || 'Impossible de créer le checkout',
      sumup: details
    });
  }
});

module.exports = router;
