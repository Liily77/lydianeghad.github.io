// backend/routes/checkout.js
const express   = require('express');
const axios     = require('axios');
const store     = require('../sumupTokenStore');
const mongoose  = require('mongoose');
const router    = express.Router();

// ⚠️ Order est enregistré dans server.js, on le récupère ici :
const Order = mongoose.model('Order');

// SumUp
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE; // ex: M39S3HK3

router.post('/', async (req, res) => {
  try {
    // 0) Token OAuth côté serveur (obtenu via /auth/connect)
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const { items, amount, currency, title, orderId } = req.body || {};

    // 1) Calcul du montant total côté serveur (NE JAMAIS faire confiance au front)
    let total = 0;
    if (Array.isArray(items) && items.length) {
      total = items.reduce((sum, i) =>
        sum + Number(i.quantity || 0) * Number(i.unit_price || 0), 0
      );
    } else {
      total = Number(amount || 0);
    }
    total = Number(total.toFixed(2));
    if (!total || total <= 0) {
      return res.status(400).json({ error: 'Montant invalide' });
    }

    // 2) Référence + URLs de retour
    const orderRef  = orderId || `order_${Date.now()}`;
    const BASE_URL  = process.env.BASE_URL || 'https://arcenciel-backend.onrender.com';
    const thankyou  = `${BASE_URL}/merci?ref=${encodeURIComponent(orderRef)}`;

    // 3) Payload SumUp (Hosted Checkout)
    // - return_url   : ping serveur (POST) après changement de statut
    // - redirect_url : bouton "Retour au site marchand" sur l’écran vert ✅
    const payload = {
      checkout_reference: orderRef,
      amount:             total,
      currency:           (currency || 'EUR').toUpperCase(),
      description:        title || 'Commande Arc En Ciel',
      hosted_checkout:    { enabled: true },
      return_url:         thankyou,
      redirect_url:       thankyou,
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    // 4) Appel API SumUp
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    // 5) URL de paiement
    const data = response?.data || {};
    const checkoutUrl = data.checkout_url || data.hosted_checkout_url;
    if (!checkoutUrl) {
      return res.status(502).json({
        error: 'Réponse SumUp sans URL de paiement',
        sumup: data
      });
    }

    // 6) Sauvegarde / Mise à jour de la commande (PENDING)
    await Order.findOneAndUpdate(
      { ref: orderRef },
      {
        ref:        orderRef,
        checkoutId: data.id, // id de checkout SumUp
        amount:     total,
        currency:   (currency || 'EUR').toUpperCase(),
        status:     'PENDING',
        raw:        data
      },
      { upsert: true, new: true }
    );

    // 7) Retour front
    // Mode B : on va rediriger DIRECTEMENT vers checkoutUrl (même onglet)
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
