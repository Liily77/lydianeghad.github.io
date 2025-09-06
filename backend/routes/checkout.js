// backend/routes/checkout.js
const express   = require('express');
const axios     = require('axios');
const store     = require('../sumupTokenStore');
const mongoose  = require('mongoose');
const router    = express.Router();

// Récupère le modèle Order défini dans server.js / models/Order.js
const Order = mongoose.model('Order');

// SumUp
const CHECKOUT_URL  = 'https://api.sumup.com/v0.1/checkouts';
const MERCHANT_CODE = process.env.SUMUP_MERCHANT_CODE; // ex: M39S3HK3

// ---------- Helpers de calcul & validation ----------
function safeNum(v) {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : 0;
}

function computeSubTotal(items = []) {
  return items.reduce((sum, i) =>
    sum + safeNum(i.quantity) * safeNum(i.unit_price), 0
  );
}

// ⚠️ VERSION ACTUELLE (bijoux uniquement)
// - Bijoux: 5.40 €
// - > 100 € (strictement) : gratuit
// TODO: Quand les vêtements seront ajoutés, réintroduire:
//       vetements: 6.90, mix: 6.90
function computeShippingFee_bijouxOnly(items = [], subTotal) {
  if (subTotal > 100) return 0;
  const hasBijoux = items.some(i => i.category === 'bijoux');
  if (hasBijoux) return 5.40;
  return 0; // panier vide → 0
}

function validateItems_bijouxOnly(items = []) {
  // ⚠️ pour l’instant on n’accepte que la catégorie 'bijoux'
  const allowed = new Set(['bijoux']);
  if (!Array.isArray(items) || !items.length) return 'Items requis';
  for (const it of items) {
    if (!allowed.has(it.category)) return 'Catégorie invalide (bijoux uniquement pour le moment)';
    if (safeNum(it.unit_price) === 0) return 'Prix invalide';
    if (safeNum(it.quantity) === 0) return 'Quantité invalide';
  }
  return null;
}

router.post('/', async (req, res) => {
  try {
    // 0) Token OAuth côté serveur
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    // Payload attendu :
    // { email, shippingAddress, items[], currency='EUR', title='Commande Arc En Ciel', orderId? }
    const {
      items = [],
      currency = 'EUR',
      title   = 'Commande Arc En Ciel',
      orderId,
      email,
      shippingAddress
    } = req.body || {};

    // 1) Validations d’entrée (bijoux uniquement pour le moment)
    if (!email) {
      return res.status(400).json({ error: 'Email requis' });
    }
    const itemsError = validateItems_bijouxOnly(items);
    if (itemsError) {
      return res.status(400).json({ error: itemsError });
    }

    // 2) Recalcul du montant total côté serveur
    let subTotal    = Number(computeSubTotal(items).toFixed(2));
    let shippingFee = Number(computeShippingFee_bijouxOnly(items, subTotal).toFixed(2));
    let total       = Number((subTotal + shippingFee).toFixed(2));

    if (!total || total <= 0) {
      return res.status(400).json({ error: 'Montant invalide' });
    }

    // 3) Référence + URL de retour (même domaine front+back)
    const orderRef    = orderId || `order_${Date.now()}`;
    const BACKEND_URL = process.env.BASE_URL || 'https://arcenciel-backend.onrender.com';
    const thankyou    = `${BACKEND_URL}/merci?ref=${encodeURIComponent(orderRef)}`;

    // 4) Enregistrer/Mettre à jour la commande (PENDING) avec détails
    await Order.findOneAndUpdate(
      { ref: orderRef },
      {
        ref:        orderRef,
        email,
        shippingAddress: shippingAddress || null,
        items,
        amounts:    { subTotal, shippingFee, total },
        currency:   (currency || 'EUR').toUpperCase(),
        status:     'PENDING',
        channel:    'sumup',
        updatedAt:  new Date(),
        createdAt:  new Date()
      },
      { upsert: true, new: true }
    );

    // 5) Payload SumUp (Hosted Checkout) — montant = TOTAL (produits + port)
    const payload = {
      checkout_reference: orderRef,
      amount:             total,
      currency:           (currency || 'EUR').toUpperCase(),
      description:        title,
      hosted_checkout:    { enabled: true },
      return_url:         thankyou, // ping/POST SumUp + redirection SPA (Merci.vue)
      redirect_url:       thankyou, // bouton “Retour au site marchand”
      ...(MERCHANT_CODE ? { merchant_code: MERCHANT_CODE } : {})
    };

    // 6) Appel API SumUp
    const response = await axios.post(CHECKOUT_URL, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });

    // 7) URL de paiement
    const data = response?.data || {};
    const checkoutUrl = data.checkout_url || data.hosted_checkout_url;
    if (!checkoutUrl) {
      return res.status(502).json({
        error: 'Réponse SumUp sans URL de paiement',
        sumup: data
      });
    }

    // 8) Sauvegarder l'id checkout SumUp + raw
    await Order.findOneAndUpdate(
      { ref: orderRef },
      { checkoutId: data.id, raw: data },
      { new: true }
    );

    // 9) Retour front (redirection directe même onglet)
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
