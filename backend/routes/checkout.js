const express = require('express');
const axios   = require('axios');
const router  = express.Router();

router.post('/', async (req, res) => {
  try {
    const { items } = req.body;
    const total = items.reduce((sum, i) => sum + i.quantity * i.unit_price, 0);
    const response = await axios.post(
      'https://api.sumup.com/v0.1/checkouts',
      {
        checkout_reference: `order_${Date.now()}`,
        amount: total,
        currency: 'EUR',
        shop_name: 'Arc En Ciel',
        description: 'Commande Arc En Ciel'
      },
      {
        headers: { Authorization: `Bearer ${process.env.SUMUP_API_KEY}` }
      }
    );
    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Erreur création checkout SumUp:', err.response?.data || err);
    res.status(500).json({ error: 'Impossible de créer le checkout' });
  }
});

module.exports = router;
