<template> 
  <div class="panier-page">
    <div class="panier-header">
      <img src="/assets/images/logo_titre_panier.png" alt="Mon panier" class="logo-panier" />
    </div>

    <div v-if="panier.length" class="panier-liste">
      <div class="panier-item" v-for="item in panier" :key="item.id">
        <div class="image-container">
          <img :src="getImageUrl(item.images?.[0])" alt="Produit" />
        </div>

        <div class="infos">
          <h3>{{ item.nom }}</h3>
          <p>{{ item.prix }} € × {{ item.quantite }} = {{ (item.prix * item.quantite).toFixed(2) }} €</p>

          <div class="quantity-controls">
            <button @click="decreaseQuantity(item.id)">−</button>
            <span>{{ item.quantite }}</span>
            <button @click="increaseQuantity(item.id)">+</button>
            <button class="retirer-btn" @click="retirerDuPanier(item.id)">🗑 Retirer</button>
          </div>
        </div>
      </div>

      <div class="panier-footer">
        <h2>Total : {{ totalPanier }} €</h2>
        <button class="payer-btn" @click="payer">Payer</button>
      </div>
    </div>

    <div v-else class="panier-vide">
      <p>Votre panier est vide.</p>
    </div>
  </div>
</template>

<script>
import { getPanier, retirerProduit, modifierQuantite } from '../utils/panier';
import { api } from '@/utils/api'; // doit renvoyer le JSON (fetch wrapper)

export default {
  name: 'Panier',
  data() {
    return {
      panier: []
    };
  },
  computed: {
    totalPanier() {
      return this.panier
        .reduce((total, item) => total + item.prix * item.quantite, 0)
        .toFixed(2);
    }
  },
  methods: {
    getImageUrl(img) {
      if (!img) return '';
      const backendUrl = import.meta.env.VITE_BACKEND_URL || '';
      return img.startsWith('/uploads') ? backendUrl + img : img;
    },
    chargerPanier() {
      this.panier = getPanier();
    },
    retirerDuPanier(id) {
      retirerProduit(id);
      this.chargerPanier();
    },
    increaseQuantity(id) {
      modifierQuantite(id, 1);
      this.chargerPanier();
    },
    decreaseQuantity(id) {
      modifierQuantite(id, -1);
      this.chargerPanier();
    },
    async payer() {
      try {
        if (!this.panier.length) {
          alert('Votre panier est vide.');
          return;
        }

        // Articles au format attendu par le backend
        const items = this.panier.map(p => ({
          name: p.nom,
          quantity: p.quantite,
          unit_price: p.prix
        }));

        // Création du checkout côté backend
        const data = await api('/api/checkout', {
          method: 'POST',
          body: JSON.stringify({ items })
        });

        if (!data || !data.checkoutUrl || !data.ref) {
          console.error('Réponse checkout invalide:', data);
          alert('Impossible de créer le paiement.');
          return;
        }

        // ➜ On bascule vers la page d'attente avec ref + checkoutUrl
        this.$router.push({
          path: '/attente',
          query: {
            ref: data.ref,
            checkoutUrl: data.checkoutUrl
          }
        });

      } catch (e) {
        console.error(e);
        alert('Erreur lors de la création du paiement.');
      }
    }
  },
  mounted() {
    this.chargerPanier();
  }
};
</script>





<style scoped>
.panier-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background-color: #fff;
  max-width: 1100px;
  margin: auto;
}

.panier-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-panier {
  display: block;
  margin: 0 auto;
  transform: translateX(60px);
  max-width: 350px;
  height: auto;
}

.panier-liste {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Carte produit */
.panier-item {
  display: flex;
  gap: 1.5rem;
  background-color: #f6f2ee;
  padding: 1rem;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  align-items: center;
  width: 70%;
  margin: 0 auto;
}

.image-container img {
  width: 110px;
  height: 110px;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.infos {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.infos h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.infos p {
  margin: 0.3rem 0;
  font-size: 1rem;
  color: #555;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.quantity-controls button {
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  background-color: #edc6c1;
  color: #000;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.quantity-controls button:hover {
  background-color: #e20e7f;
  color: white;
}

.retirer-btn {
  background-color: #fdd;
  color: red;
  transition: background-color 0.3s ease, color 0.3s ease;
  margin-left: auto;
}

.retirer-btn:hover {
  background-color: #b00020 !important;
  color: white !important;
}

/* Footer panier – même style que les cartes */
.panier-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9f4f0;
  padding: 1rem;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  width: 70%;
  margin: 1.5rem auto 0;
}

.panier-footer h2 {
  font-size: 1.3rem;
  color: #000;
  margin: 0;
}

.payer-btn {
  padding: 0.6rem 1.5rem;
  background-color: #e21583b6;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.payer-btn:hover {
  background-color: #e20e7f;
}

.panier-vide {
  text-align: center;
  font-size: 1.2rem;
  color: #777;
  padding: 3rem 1rem;
}

@media (max-width: 768px) {
  /* on définit la hauteur approximative du footer du site */
  .panier-page { 
    --site-footer-h: 72px; /* ajuste à 64–80px selon ton footer */
  }

  .panier-page {
    padding: 1rem;
    max-width: 100%;
    display: flex;
    flex-direction: column;
  }

  /* on réserve assez d'espace en bas pour :
     footer site + bloc paiement */
  .panier-liste {
    flex: 1;
    padding-bottom: calc(var(--site-footer-h) + 140px);
  }

  .logo-panier { max-width: 180px; transform: translateX(0); }

  .panier-item {
    flex-direction: row;
    width: 90%;
    max-width: 480px;
    margin: 0 auto;
    padding: 0.8rem;
    gap: 0.8rem;
    align-items: center;
  }

  .image-container img {
    width: 70px; height: 70px; border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1); object-fit: cover;
  }

  .infos { flex: 1; width: auto; }
  .infos h3 { font-size: 0.9rem; }
  .infos p  { font-size: 0.75rem; }

  .quantity-controls { flex-wrap: nowrap; gap: 0.4rem; }
  .quantity-controls button { padding: 0.2rem 0.5rem; font-size: 0.7rem; }
  .retirer-btn { margin-left: auto; font-size: 0.7rem; padding: 0.2rem 0.5rem; }

  /* === BLOC PAIEMENT FIXE AU-DESSUS DU FOOTER DU SITE === */
  .panier-footer {
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    /* on place le bloc AU-DESSUS du footer site */
    bottom: calc(var(--site-footer-h) + env(safe-area-inset-bottom, 0px) + 8px);
    width: min(92%, 480px);
    display: flex;
    flex-direction: column-reverse; /* bouton au-dessus du total */
    align-items: center;
    gap: 0.5rem;
    background: rgba(249, 244, 240, 0.95);
    backdrop-filter: blur(2px);
    padding: 0.75rem 1rem;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    border-radius: 12px;
    z-index: 100;
  }

  .panier-footer h2 {
    font-size: 1rem;
    margin: 0;
    width: 100%;
    text-align: center;
  }

  .payer-btn {
    width: 100%;
    max-width: 320px;
    font-size: 0.85rem;
    padding: 0.55rem 1rem;
    border-radius: 10px;
  }
}


</style>
