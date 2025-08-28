// backend/routes/checkout.js
const express = require('express');
const axios   = require('axios');
const store   = require('../sumupTokenStore'); // ← on lit le token ici
const router  = express.Router();

// ─── URL SumUp (identique sandbox & production) ──────────────────────────
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE; // ex: M99GF6UV

// ─── Création d’un checkout SumUp ────────────────────────────────────────
router.post('/', async (req, res) => {
  try {
    // 0) Vérifier le token côté serveur
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const { items, amount, currency, title, orderId } = req.body;

    // 1) Calcule le montant total
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

    // 2) Construire le payload pour SumUp
    const payload = {
      checkout_reference: orderId || `order_${Date.now()}`,
      amount:             Number(total.toFixed(2)),
      currency:           currency || 'EUR',
      description:        title || 'Commande Arc En Ciel',
      hosted_checkout:    { enabled: true },
      return_url: process.env.CHECKOUT_RETURN_URL || 'https://arcenciel-backend.onrender.com/panier',
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    // Debug log
    console.log('SumUp payload →', payload);

    // 3) Appel API SumUp
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    // 4) Réponse au front
    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Erreur création checkout SumUp:', err.response?.data || err.message);
    const status = err.response?.status || 500;
    res.status(status).json({ error: 'Impossible de créer le checkout' });
  }
});

module.exports = router;
