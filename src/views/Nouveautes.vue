<template>
  <div class="nouveautes-page">
    <h1>⭐ Nos nouveautés ⭐</h1>

    <div v-if="produits.length" class="grille-produits">
      <div
        v-for="(produit, index) in produits"
        :key="produit._id || produit.id"
        class="carte-produit"
      >
        <!-- SLIDE D’IMAGES -->
        <div class="slider-container">
          <button
            v-if="produit.images.length > 1"
            class="arrow left"
            @click="prevImage(index)"
            aria-label="Image précédente"
          >‹</button>

          <img
            :src="getImageUrl(produit.images[currentIndexes[index] || 0])"
            :alt="produit.nom"
            loading="lazy"
          />

          <button
            v-if="produit.images.length > 1"
            class="arrow right"
            @click="nextImage(index)"
            aria-label="Image suivante"
          >›</button>
        </div>

        <h3>{{ produit.nom }}</h3>
        <p>{{ produit.description }}</p>
        <p>{{ produit.prix.toFixed(2) }} €</p>
        <router-link
          :to="`/produit/${produit._id || produit.id}`"
          class="voir-btn"
        >
          Voir
        </router-link>
      </div>
    </div>

    <div v-else class="chargement">
      Chargement des nouveautés...
    </div>
  </div>
</template>

<script>
import { api } from '@/utils/api.js';

export default {
  name: 'Nouveautes',
  data() {
    return {
      produits: [],
      currentIndexes: {}
    };
  },
  async mounted() {
    try {
      const data = await api('/api/produits');
      // On prend les 10 derniers produits
      const derniers = data.slice().reverse().slice(0, 10);
      this.produits = derniers;
      this.currentIndexes = Object.fromEntries(
        derniers.map((_, i) => [i, 0])
      );
    } catch (err) {
      console.error('❌ Erreur chargement nouveautés', err);
    }
  },
  methods: {
    getImageUrl(img) {
      if (!img) return '';
      // Utilise BASE défini dans api.js pour prepender en prod
      const backendUrl = import.meta.env.VITE_BACKEND_URL || '';
      return img.startsWith('/uploads') ? backendUrl + img : img;
    },
    nextImage(index) {
      const total = this.produits[index].images.length;
      this.currentIndexes[index] =
        (this.currentIndexes[index] + 1) % total;
    },
    prevImage(index) {
      const total = this.produits[index].images.length;
      this.currentIndexes[index] =
        (this.currentIndexes[index] - 1 + total) % total;
    }
  }
};
</script>


<style scoped>
/* Ton style actuel, très bien */

.nouveautes-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background-color: #fff;
  max-width: 1300px;
  margin: auto;
}

h1 {
  text-align: center;
  font-size: 2.2rem;
  margin-bottom: 2rem;
}

.grille-produits {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.carte-produit {
  background: #f9f4f0;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.slider-container {
  position: relative;
  width: 100%;
  height: 200px;
  margin-bottom: 1rem;
  overflow: hidden;
  border-radius: 10px;
}

.slider-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 2rem;
  color: black;
  cursor: pointer;
  z-index: 1;
}

.arrow.left {
  left: 10px;
}

.arrow.right {
  right: 10px;
}

.voir-btn {
  display: inline-block;
  margin-top: 0.6rem;
  padding: 0.4rem 1rem;
  background-color: #edc6c1;
  color: #000;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: background 0.2s ease;
}

.voir-btn:hover {
  background-color: #e20e7fe1;
  color: white;
  font-weight: bold;
}

.chargement {
  text-align: center;
  font-style: italic;
  color: #777;
}

/* MOBILE */
@media (max-width: 768px) {
  .nouveautes-page {
    padding: clamp(0.5rem, 3vw, 1rem);
  }

  h1 {
    font-size: clamp(1rem, 4.5vw, 1.5rem);
    margin-bottom: clamp(1rem, 3vw, 1.5rem);
  }

  .grille-produits {
    grid-template-columns: repeat(2, 1fr);
    gap: clamp(0.5rem, 3vw, 1rem);
  }

  .carte-produit {
    padding: clamp(0.5rem, 2vw, 1rem);
    border-radius: clamp(8px, 2vw, 12px);
    font-size: clamp(0.7rem, 2.2vw, 0.85rem);
  }

  .slider-container {
    height: clamp(140px, 35vw, 180px);
    border-radius: clamp(6px, 2vw, 10px);
  }

  .slider-container img {
    border-radius: clamp(6px, 2vw, 10px);
  }

  .arrow {
    font-size: clamp(1.2rem, 5vw, 1.6rem);
  }

  .arrow.left {
    left: clamp(5px, 2vw, 10px);
  }

  .arrow.right {
    right: clamp(5px, 2vw, 10px);
  }

  .voir-btn {
    font-size: clamp(0.7rem, 1.8vw, 0.85rem);
    padding: clamp(0.3rem, 2vw, 0.5rem) clamp(0.5rem, 2.5vw, 0.8rem);
    border-radius: clamp(5px, 1.5vw, 8px);
  }
}
</style>
