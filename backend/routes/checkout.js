// backend/routes/checkout.js
const express = require('express');
const axios   = require('axios');
const store   = require('../sumupTokenStore');
const mongoose = require('mongoose');
const router  = express.Router();

// Import du modèle Order (défini dans server.js)
const Order = mongoose.model('Order');

// SumUp
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE; // ex: M39S3HK3

router.post('/', async (req, res) => {
  try {
    // 0) Token OAuth côté serveur
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const { items, amount, currency, title, orderId } = req.body;

    // 1) Calcul du montant total
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

    // 2) Référence commande + return_url
    const orderRef = orderId || `order_${Date.now()}`;
    const BASE_URL = process.env.BASE_URL || 'https://arcenciel-backend.onrender.com';
    const returnUrl = `${BASE_URL}/merci?ref=${encodeURIComponent(orderRef)}`;

    // 3) Payload pour SumUp
    const payload = {
      checkout_reference: orderRef,
      amount:             Number(total.toFixed(2)),
      currency:           currency || 'EUR',
      description:        title || 'Commande Arc En Ciel',
      hosted_checkout:    { enabled: true },
      return_url:         returnUrl,
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    console.log('SumUp payload →', payload);

    // 4) Appel API SumUp
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    console.log('SumUp response status:', response.status);
    console.log('SumUp response data:', response.data);

    // 5) URL de paiement
    const checkoutUrl =
      response?.data?.checkout_url || response?.data?.hosted_checkout_url;

    if (!checkoutUrl) {
      return res.status(502).json({
        error: 'Réponse SumUp sans URL de paiement',
        sumup: response.data
      });
    }

    // 6) Enregistrement de la commande en base (statut PENDING)
    await Order.findOneAndUpdate(
      { ref: orderRef },
      {
        ref:        orderRef,
        checkoutId: response?.data?.id,
        amount:     Number(total.toFixed(2)),
        currency:   currency || 'EUR',
        status:     'PENDING',
        raw:        response?.data
      },
      { upsert: true, new: true }
    );

    // 7) Retourner l’URL de paiement au frontend
    res.json({ checkoutUrl, ref: orderRef });
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
