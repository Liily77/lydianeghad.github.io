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

    <div class="fiche-produit" id="fiche">
      <div class="fiche-image">
        <div class="carousel">
          <button class="arrow left" @click="prevImage" v-if="currentIndex > 0">❮</button>
          <transition :name="transitionName">
            <img
              :src="prefixedImages[currentIndex]"
              :key="prefixedImages[currentIndex]"
              :alt="produit.nom"
              class="product-image"
            />
          </transition>
          <button class="arrow right" @click="nextImage" v-if="currentIndex < prefixedImages.length - 1">❯</button>
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
          <div class="buttons-group">
            <button class="add-to-cart" @click="ajouterProduitAuPanier">
              Ajouter au panier
            </button>
            <router-link to="/panier" class="view-cart">
              Voir mon panier
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <div v-if="showToast" class="toast-message">
      ✅ Produit ajouté au panier !
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
      transitionName: 'slide-right',
      showToast: false,
    };
  },
  computed: {
    // Préfixe backend sur chaque image si besoin
    prefixedImages() {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || '';
      return (this.produit?.images || []).map(img =>
        img.startsWith('/uploads') ? backendUrl + img : img
      );
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
      if (this.currentIndex < this.prefixedImages.length - 1) {
        this.currentIndex++;
      }
    },
    prevImage() {
      this.transitionName = 'slide-left';
      if (this.currentIndex > 0) {
        this.currentIndex--;
      }
    },
    increaseQuantity() {
      this.quantity++;
    },
    decreaseQuantity() {
      if (this.quantity > 1) {
        this.quantity--;
      }
    },
    ajouterProduitAuPanier() {
      ajouterAuPanier(this.produit, this.quantity);
      this.showToast = true;
      setTimeout(() => {
        this.showToast = false;
      }, 2500);
    }
  },
  async mounted() {
    const id = this.$route.params.id;
    try {
      const res = await fetch(`/api/produits/${id}`);
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      if (data && data.nom) {
        this.produit = data;
        this.$nextTick(() => {
          const el = document.getElementById('fiche');
          if (el) el.scrollIntoView({ behavior: 'smooth' });
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
  max-width: 1100px;   /* ← largeur max de la page détail */
  margin: 0 auto;      /* ← centre toute la zone contenu */
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
  font-family: 'Raleway', sans-serif;
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
  max-width: 850px;
  width: 100%;
  height: 380px;
  margin: 0 auto 2rem; /* ← centre le bloc fiche */
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
  margin: 0 0 0.8rem;
  font-size: 1.3rem;
}
.fiche-details p {
  margin: 0.3rem 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* Actions */
.actions-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4rem;
}

/* Sélecteur de quantité */
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
  font-family: 'Raleway', sans-serif;
}
.quantity-selector button:hover {
  background: #e8c4bf;
}


.buttons-group {
  display: flex;
  flex-direction: column;  
  gap: 0.5rem;
}

.add-to-cart,
.view-cart {
  width: 10rem;             
  padding: 0.6rem 0;        
  font-family: 'Raleway', sans-serif;
  font-size: 0.9rem;        
  font-weight: 600;
  text-align: center;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s ease;
  text-decoration: none;
  display: block;
  margin-left: auto;      
}


.add-to-cart {
  background-color: #f3e8f5;
  color: #a074ae;

}
.add-to-cart:hover {

  background-color:  #8c6da2;
  color: white;

}


.view-cart {
  background-color: #98babb;
  color:whitesmoke;
}
  
.view-cart:hover {
  background-color: #719394;
  color: white;
}


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

.toast-message {
  position: fixed;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: #e0cecc;
  color: rgb(7, 86, 45);
  padding: 0.8rem 1.5rem;
  border-radius: 5px;
  box-shadow: 0 3px 8px rgba(0,0,0,0.3);
  font-weight: bold;
  z-index: 9999;
  white-space: nowrap;
  animation: fadeinout 2.5s ease forwards;
}

@keyframes fadeinout {
  0% {opacity: 0;}
  10% {opacity: 1;}
  90% {opacity: 1;}
  100% {opacity: 0;}
}



@media (max-width: 768px) {
  
  .fiche-produit {
    flex-direction: column;
    height: auto;
    max-width: 100%;
    margin-bottom: 1.5rem;
    transform: scale(0.9);
    transform-origin: top center;
    margin: 1rem auto 1.5rem;
  }

  .fiche-image {
    height: 240px;
  }

  .back-home {
    margin-top: 0.8rem;
    margin-bottom: 4rem;
  }

  .back-button {
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    border-radius: 6px;
  }

  .actions-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
  }


  .quantity-selector {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .buttons-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 140px;       
    margin-left: auto;  
  }

  .add-to-cart,
  .view-cart {
    width: 100%;       
    white-space: nowrap;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    text-align: center;
    box-sizing: border-box; 
  }

  .fiche-details p:last-of-type {
    margin-bottom: 0.5rem;
  }

  .toast-message {
    bottom: 80px; 
  }
}


</style>
