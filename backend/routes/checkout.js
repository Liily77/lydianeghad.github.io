const express = require('express');
const axios   = require('axios');
const store   = require('../sumupTokenStore'); // ← on lit le token ici
const router  = express.Router();

// ─── Sandbox vs Production pour SumUp ──────────────────────────────────
const isSandbox    = process.env.USE_SUMUP_SANDBOX === 'true';
const CHECKOUT_URL = isSandbox
  ? 'https://sandbox.sumup.com/v0.1/checkouts'
  : 'https://api.sumup.com/v0.1/checkouts';

// ─── Création d’un checkout SumUp ─────────────────────────────────────
router.post('/', async (req, res) => {
  try {
    // 0) Vérifier le token côté serveur
    const token = store.get();
    if (!token) {
      return res.status(400).json({ error: 'Token SumUp manquant côté serveur' });
    }

    const { items, amount, currency, title, orderId } = req.body;

    // 1) Calcule le montant selon le format reçu
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

    // 2) Appel API SumUp
    const response = await axios.post(
      CHECKOUT_URL,
      {
        checkout_reference: orderId || `order_${Date.now()}`,
        amount:             Number(total.toFixed(2)),
        currency:           currency || 'EUR',
        shop_name:          'Arc En Ciel',
        description:        title || 'Commande Arc En Ciel'
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );

    // 3) Répond avec la clé attendue par le front
    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Erreur création checkout SumUp:', err.response?.data || err.message);
    const status = err.response?.status || 500;
    res.status(status).json({ error: 'Impossible de créer le checkout' });
  }
});

module.exports = router;

