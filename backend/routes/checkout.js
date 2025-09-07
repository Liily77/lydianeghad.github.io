// backend/routes/checkout.js
const express   = require('express');
const axios     = require('axios');
const store     = require('../sumupTokenStore');
const mongoose  = require('mongoose');
const router    = express.Router();

// Modèle Order
const Order = mongoose.model('Order');

// Constantes SumUp
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE;

// ---------- Helpers ----------
function safeNum(v) {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : 0;
}

function computeSubTotal(items = []) {
  return items.reduce((sum, i) =>
    sum + safeNum(i.quantity) * safeNum(i.unit_price), 0
  );
}

function computeShippingFee_bijouxOnly(items = [], subTotal) {
  if (subTotal > 100) return 0;
  const hasBijoux = items.some(i => i.category === 'bijoux');
  return hasBijoux ? 5.40 : 0;
}

function validateItems_bijouxOnly(items = []) {
  const allowed = new Set(['bijoux']);
  if (!Array.isArray(items) || !items.length) return '❌ Items requis';
  for (const it of items) {
    if (!allowed.has(it.category)) return `❌ Catégorie invalide (${it.category}) — uniquement 'bijoux' pour le moment`;
    if (safeNum(it.unit_price) === 0) return `❌ Prix invalide pour ${it.name || 'un produit'}`;
    if (safeNum(it.quantity) === 0) return `❌ Quantité invalide pour ${it.name || 'un produit'}`;
  }
  return null;
}

// ---------- Route principale ----------
router.post('/', async (req, res) => {
  try {
    console.log('📥 Requête checkout reçue:', req.body);

    // 0) Vérifier token
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const {
      items = [],
      currency = 'EUR',
      title   = 'Commande Arc En Ciel',
      orderId,
      email,
      shippingAddress
    } = req.body || {};

    // 1) Validation
    if (!email) {
      return res.status(400).json({ error: '❌ Email requis' });
    }
    const itemsError = validateItems_bijouxOnly(items);
    if (itemsError) {
      return res.status(400).json({ error: itemsError });
    }

    // 2) Calcul
    let subTotal    = Number(computeSubTotal(items).toFixed(2));
    let shippingFee = Number(computeShippingFee_bijouxOnly(items, subTotal).toFixed(2));
    let total       = Number((subTotal + shippingFee).toFixed(2));

    if (!total || total <= 0) {
      return res.status(400).json({ error: '❌ Montant total invalide' });
    }

    // 3) Référence commande
    const orderRef    = orderId || `order_${Date.now()}`;
    const BACKEND_URL = process.env.BASE_URL || 'https://arcenciel-backend.onrender.com';
    const thankyou    = `${BACKEND_URL}/merci?ref=${encodeURIComponent(orderRef)}`;

    // 4) Enregistrer en base
    await Order.findOneAndUpdate(
      { ref: orderRef },
      {
        ref:        orderRef,
        email,
        shippingAddress: shippingAddress || null,
        items,
        amounts:    { subTotal, shippingFee, total },
        currency:   currency.toUpperCase(),
        status:     'PENDING',
        channel:    'sumup',
        updatedAt:  new Date(),
        createdAt:  new Date()
      },
      { upsert: true, new: true }
    );

    // 5) Payload SumUp
    const payload = {
      checkout_reference: orderRef,
      amount:             total,
      currency:           currency.toUpperCase(),
      description:        title,
      hosted_checkout:    { enabled: true },
      return_url:         thankyou,
      redirect_url:       thankyou,
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    console.log('📤 Payload envoyé à SumUp:', payload);

    // 6) Appel API SumUp
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    const data = response?.data || {};
    console.log('✅ Réponse SumUp:', data);

    const checkoutUrl = data.checkout_url || data.hosted_checkout_url;
    if (!checkoutUrl) {
      return res.status(502).json({
        error: 'Réponse SumUp sans URL de paiement',
        sumup: data
      });
    }

    // 7) Sauvegarde checkoutId
    await Order.findOneAndUpdate(
      { ref: orderRef },
      { checkoutId: data.id, raw: data },
      { new: true }
    );

    // 8) Réponse front
    res.json({ checkoutUrl, ref: orderRef });

  } catch (err) {
    const status  = err.response?.status || 500;
    const details = err.response?.data || { message: err.message };

    console.error('❌ Erreur création checkout SumUp:', details);

    res.status(status).json({
      error: details?.message || details?.error_message || 'Impossible de créer le checkout',
      sumup: details
    });
  }
});

module.exports = router;
