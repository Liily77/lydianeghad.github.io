// backend/routes/webhooksumup.js
const express  = require('express');
const axios    = require('axios');
const mongoose = require('mongoose');
const store    = require('../sumupTokenStore');

const router = express.Router();
const Order  = mongoose.models.Order || mongoose.model('Order');

// Petit helper pour vérifier un checkout chez SumUp
async function fetchCheckout(checkoutId, token) {
  const url = `https://api.sumup.com/v0.1/checkouts/${encodeURIComponent(checkoutId)}`;
  const { data } = await axios.get(url, {
    headers: { Authorization: `Bearer ${token}` },
    timeout: 15000
  });
  return data;
}

router.post('/sumup', async (req, res) => {
  // ⚡ SumUp attend juste un 200 rapide
  res.status(200).end();

  try {
    const body = req.body || {};
    const checkoutId = body?.id || body?.data?.id;
    if (!checkoutId) return;

    const token = store.get();
    if (!token) {
      console.warn('[WEBHOOK] Pas de token SumUp côté serveur');
      return;
    }

    // 1) Vérifier l’état réel côté SumUp
    const checkout = await fetchCheckout(checkoutId, token);
    if (!checkout) return;

    if ((checkout.status || '').toUpperCase() !== 'PAID') return;

    // 2) Identifier la commande locale
    const orderRef = checkout.checkout_reference;
    if (!orderRef) return;

    // 3) Mettre à jour la commande en PAID
    const resUpd = await Order.updateOne(
      { ref: orderRef, status: { $ne: 'PAID' } },
      { $set: { status: 'PAID', paidAt: new Date(), raw: checkout } }
    );

    if (resUpd.modifiedCount > 0) {
      console.log('[WEBHOOK] ✅ Commande PAYÉE :', orderRef);
    } else {
      console.log('[WEBHOOK] ℹ️ Déjà PAID ou non trouvée :', orderRef);
    }
  } catch (err) {
    console.error('[WEBHOOK] Erreur :', err.message);
  }
});

module.exports = router;
