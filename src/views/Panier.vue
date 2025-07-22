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
      // On utilise directement le chemin relatif retourné par le backend
      return img || '';
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
    payer() {
      alert('Paiement non encore disponible.');
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

.panier-item {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  background-color: #f9f4f0;
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
  color: #000;
  transition: background-color 0.3s ease, color 0.3s ease;
  margin-left: 2rem;
}

.retirer-btn:hover {
  background-color: #b00020 !important;
  color: white !important;
}

.panier-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  width: 70%;
  margin: 0 auto;
}

.panier-footer h2 {
  font-size: 1.3rem;
  color: #000;
  margin: 0;
}

.payer-btn {
  padding: 0.6rem 1.5rem;
  background-color: #8c6da2;
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
</style>

