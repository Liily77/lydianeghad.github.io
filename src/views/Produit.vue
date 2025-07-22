<template>
  <div class="produit-page" v-if="produit">
    <div class="back-home">
      <router-link
        :to="{ path: `/${categorieURL}`, hash: `#${categorieURL}-cards` }"
        class="back-button"
      >
        ← Revenir aux produits
      </router-link>
    </div>

    <!-- ID ajouté ici pour scroll automatique -->
    <div class="fiche-produit" id="fiche">
      <div class="fiche-image">
        <div class="carousel">
          <button class="arrow left" @click="prevImage" v-if="currentIndex > 0">❮</button>
          <transition :name="transitionName">
            <img
              :src="images[currentIndex]"
              :key="images[currentIndex]"
              :alt="produit.nom"
              class="product-image"
            />
          </transition>
          <button class="arrow right" @click="nextImage" v-if="currentIndex < images.length - 1">❯</button>
        </div>
      </div>

      <div class="fiche-details">
        <h2>{{ produit.nom }}</h2>
        <p>{{ produit.description }}</p>
        <p>{{ produit.prix.toFixed(2) }} €</p>
        <div class="actions-row">
          <div class="quantity-selector">
            <button @click="decreaseQuantity">−</button>
            <span>{{ quantity }}</span>
            <button @click="increaseQuantity">+</button>
          </div>
          <button class="add-to-cart" @click="ajouterProduitAuPanier">
            Ajouter au panier
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="produit-page">
    <p style="text-align: center; margin-top: 4rem; font-weight: bold;">
      Produit introuvable
    </p>
  </div>
</template>

<script>
import { ajouterAuPanier } from '@/utils/panier';

export default {
  name: 'Produit',
  data() {
    return {
      produit: null,
      quantity: 1,
      currentIndex: 0,
      transitionName: 'slide-right'
    };
  },
  computed: {
    images() {
      return this.produit?.images || [];
    },
    categorieURL() {
      const from = this.$route.query.from;
      if (from) return from;
      return this.cleanCategorie(this.produit?.categorie || '');
    }
  },
  methods: {
    cleanCategorie(text) {
      return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/\s+/g, '')
        .replace(/œ/g, 'oe')
        .replace(/[éè]/g, 'e');
    },
    nextImage() {
      this.transitionName = 'slide-right';
      if (this.currentIndex < this.images.length - 1) this.currentIndex++;
    },
    prevImage() {
      this.transitionName = 'slide-left';
      if (this.currentIndex > 0) this.currentIndex--;
    },
    increaseQuantity() {
      this.quantity++;
    },
    decreaseQuantity() {
      if (this.quantity > 1) this.quantity--;
    },
    ajouterProduitAuPanier() {
      ajouterAuPanier(this.produit, this.quantity);
      alert('✅ Produit ajouté au panier !');
    }
  },
  async mounted() {
    const id = this.$route.params.id;
    try {
      const res = await fetch(`/produits/${id}`);
      const produit = await res.json();
      if (res.ok && produit && produit.nom) {
        this.produit = produit;

        // Scroll vers #fiche après chargement du DOM
        this.$nextTick(() => {
          const el = document.getElementById('fiche');
          if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
          }
        });
      }
    } catch (error) {
      console.error('Erreur chargement produit :', error);
    }
  }
};
</script>


<style scoped>
.produit-page {
  background-color: #f9f4f0;
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
}

/* Bouton retour */
.back-home {
  margin-top: 2rem;
  margin-bottom: 2.5rem;
}
.back-button {
  background-color: #f3e8f5;
  color: #a074ae;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}
.back-button:hover {
  background-color: #e20e80;
  color: #fff;
}

/* Fiche produit */
.fiche-produit {
  display: flex;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 2rem;
  max-width: 850px;
  width: 100%;
  height: 380px;
}

/* Image produit */
.fiche-image {
  flex: 1;
  position: relative;
  background: #f2f2f2;
}
.carousel {
  position: relative;
  width: 100%;
  height: 100%;
}
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Détails produit */
.fiche-details {
  flex: 1;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.fiche-details h2 {
  margin: 0 0 0.8rem; /* ↑ Titre un peu plus haut */
  font-size: 1.3rem;
}
.fiche-details p {
  margin: 0.3rem 0;
  font-size: 0.95rem;
  line-height: 1.6; /* ↑ Espace entre les lignes */
}

/* Actions */
.actions-row {
  display: flex;
  justify-content: space-between; /* ↑ Bouton à droite */
  align-items: center;
  margin-top: 4rem;
}
.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.quantity-selector button {
  background: #f1dad7;
  border: none;
  padding: 0.3rem 0.8rem;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
}
.quantity-selector button:hover {
  background: #e8c4bf;
}
.add-to-cart {
  background-color: #98babb;
  color: white;
  border: none;
  padding: 0.5rem 1.1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s ease;
}
.add-to-cart:hover {
  background-color: #8c6da2;
}

/* Flèches carrousel */
.arrow {
  position: absolute;
  top: 50%;
  font-size: 1.8rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #444;
  z-index: 2;
  transform: translateY(-50%);
}
.arrow:hover {
  color: #a074ae;
}
.arrow.left {
  left: 10px;
}
.arrow.right {
  right: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .fiche-produit {
    flex-direction: column;
    height: auto;
    max-width: 100%;
  }
  .fiche-image {
    height: 280px;
  }
  .actions-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
