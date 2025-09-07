<template>
  <section class="checkout">
    <div class="card">
      <h1 class="title">Finaliser ma commande</h1>

      <div class="grid">
        <!-- Infos client -->
        <form class="form" @submit.prevent="submit">
          <h2 class="subtitle">Informations</h2>

          <label>Email</label>
          <input v-model.trim="form.email" type="email" required placeholder="votre@email.com" />

          <label>Nom complet</label>
          <input v-model.trim="form.fullName" type="text" required placeholder="Prénom Nom" />

          <label>Adresse</label>
          <input v-model.trim="form.address1" type="text" required placeholder="N° et rue" />
          <input v-model.trim="form.address2" type="text" placeholder="Complément (optionnel)" />

          <div class="row">
            <div>
              <label>Code postal</label>
              <input v-model.trim="form.postcode" type="text" required />
            </div>
            <div>
              <label>Ville</label>
              <input v-model.trim="form.city" type="text" required />
            </div>
          </div>

          <label>Pays</label>
          <input v-model.trim="form.country" type="text" required placeholder="France" />

          <button class="pay" :disabled="loading">
            {{ loading ? "Redirection vers le paiement..." : "Payer maintenant" }}
          </button>
        </form>

        <!-- Récap panier -->
        <aside class="summary">
          <h2 class="subtitle">Votre panier</h2>

          <ul class="items">
            <li v-for="it in cart" :key="it.id">
              <div class="row-between">
                <span>{{ it.name }} × {{ it.qty }}</span>
                <span>{{ (it.price * it.qty).toFixed(2) }} €</span>
              </div>
            </li>
          </ul>

          <div class="line">
            <span>Sous-total</span>
            <span>{{ subTotal.toFixed(2) }} €</span>
          </div>

          <div class="line">
            <span>Frais de livraison</span>
            <span>
              <template v-if="shippingFee === 0">Gratuite</template>
              <template v-else>{{ shippingFee.toFixed(2) }} €</template>
            </span>
          </div>

          <div class="total">
            <span>Total</span>
            <span>{{ total.toFixed(2) }} €</span>
          </div>

          <!-- Encadré d’infos livraison -->
          <div class="shipping-info">
            <h3>Conditions de livraison</h3>
            <ul>
              <li><strong>Bijoux</strong> : 5,40 €</li>
              <li><strong>Au-delà de 100 €</strong> : livraison <strong>offerte</strong></li>
            </ul>
            <small>Les frais exacts sont calculés automatiquement au paiement.</small>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<script>
import { getPanier } from '../utils/panier'
import { api } from '../utils/api'

export default {
  name: 'Checkout',
  data() {
    return {
      loading: false,
      cart: [], // [{id,name,category,price,qty}]
      form: {
        email: '',
        fullName: '',
        address1: '',
        address2: '',
        postcode: '',
        city: '',
        country: 'France',
      },
    }
  },
  computed: {
    subTotal() {
      return this.cart.reduce((s, it) => s + Number(it.price) * Number(it.qty), 0)
    },
    shippingFee() {
      // Bijoux uniquement
      if (this.subTotal > 100) return 0
      return 5.40
    },
    total() {
      return +(this.subTotal + this.shippingFee).toFixed(2)
    },
  },
  methods: {
    loadCart() {
      const raw = getPanier()
      this.cart = raw.map(p => ({
        id: p._id || p.id,
        name: p.nom,
        category: 'bijoux', // ⬅️ tout est bijoux
        price: Number(p.prix),
        qty: Number(p.quantite),
      }))
    },
    async submit() {
      try {
        if (this.loading) return
        this.loading = true

        if (!this.form.email || !this.cart.length) {
          alert('Email et panier sont requis.')
          return
        }

        const payload = {
          email: this.form.email,
          shippingAddress: {
            fullName: this.form.fullName,
            address1: this.form.address1,
            address2: this.form.address2,
            postcode: this.form.postcode,
            city: this.form.city,
            country: this.form.country,
          },
          items: this.cart.map(({ id, name, price, qty }) => ({
            id,
            name,
            category: 'bijoux',
            unit_price: Number(price),
            quantity: Number(qty),
          })),
          title: 'Commande Arc En Ciel',
          currency: 'EUR',
        }

        const data = await api('/api/checkout', {
          method: 'POST',
          body: JSON.stringify(payload),
        })

        if (!data?.checkoutUrl) {
          throw new Error('Réponse checkout invalide')
        }

        window.location.href = data.checkoutUrl
      } catch (e) {
        alert('Impossible de lancer le paiement : ' + (e.message || 'Erreur inconnue'))
      } finally {
        this.loading = false
      }
    },
  },
  mounted() {
    this.loadCart()
    window.addEventListener('maj-panier', this.loadCart)
  },
  beforeUnmount() {
    window.removeEventListener('maj-panier', this.loadCart)
  },
}
</script>

<style scoped>
.checkout {
  display: flex;
  justify-content: center;
  padding: 2.5rem;
  font-family: "Lucida Sans", "Lucida Grande", sans-serif;
}

.card {
  width: 100%;
  max-width: 980px;
  background: #fff;
  border-radius: 18px;
  padding: 2rem;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
}

.title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 700;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem; /* ✅ plus d’espace entre form et récap */
}

.form label {
  font-weight: 600;
  margin-bottom: 0.4rem;
  display: block;
  font-size: 1rem;
}

.form input {
  width: 100%;
  padding: 0.9rem;
  font-size: 1rem;
  margin-bottom: 1rem; /* ✅ plus d’espace entre les champs */
  border: 1px solid #ddd;
  border-radius: 12px;
  outline: none;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.pay {
  margin-top: 1.5rem;
  width: 100%;
  padding: 1rem 1.2rem;
  border: 0;
  border-radius: 14px;
  background: #222;
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
.pay:hover {
  background: #444;
}

.summary {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 1.5rem;
  font-size: 1rem;
}

.subtitle {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.items {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: grid;
  gap: 0.5rem;
}

.row-between {
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
}

.line,
.total {
  display: flex;
  justify-content: space-between;
  padding: 0.6rem 0;
  border-top: 1px dashed #e5e5e5;
}

.total {
  font-weight: 800;
  font-size: 1.2rem;
  border-top: 2px solid #ddd;
  margin-top: 0.5rem;
}

/* Encadré frais livraison */
.shipping-info {
  margin-top: 1.5rem;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 1rem 1.2rem;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
  font-size: 0.95rem;
}
.shipping-info h3 {
  margin: 0 0 0.6rem;
  font-size: 1.1rem;
  font-weight: 600;
}
.shipping-info ul {
  margin: 0 0 0.6rem;
  padding-left: 18px;
}
.shipping-info li {
  line-height: 1.5;
}
.shipping-info small {
  color: #666;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
