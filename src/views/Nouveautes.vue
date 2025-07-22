<template>
  <div class="nouveautes-page">
    <h1>⭐ Nos nouveautés ⭐</h1>

    <div v-if="produits.length" class="grille-produits">
      <div v-for="(produit, index) in produits" :key="produit._id || produit.id" class="carte-produit">
        <!-- SLIDE D’IMAGES -->
        <div class="slider-container">
          <button
            v-if="produit.images.length > 1"
            class="arrow left"
            @click="prevImage(index)"
          >‹</button>

          <img
            :src="getImageUrl(produit.images[currentIndexes[index] || 0])"
            :alt="produit.nom"
          />

          <button
            v-if="produit.images.length > 1"
            class="arrow right"
            @click="nextImage(index)"
          >›</button>
        </div>

        <h3>{{ produit.nom }}</h3>
        <p>{{ produit.description }}</p>
        <p>{{ produit.prix.toFixed(2) }} €</p>
        <router-link :to="`/produit/${produit._id || produit.id}`" class="voir-btn">Voir</router-link>
      </div>
    </div>

    <div v-else class="chargement">
      Chargement des nouveautés...
    </div>
  </div>
</template>

<script>
export default {
  name: 'Nouveautes',
  data() {
    return {
      produits: [],
      currentIndexes: {}
    };
  },
  mounted() {
    fetch('/produits')
      .then(res => res.json())
      .then(data => {
        const derniers = data.slice().reverse().slice(0, 10);
        this.produits = derniers;
        this.currentIndexes = Object.fromEntries(derniers.map((_, i) => [i, 0]));
      })
      .catch(err => {
        console.error('❌ Erreur chargement nouveautés', err);
      });
  },
  methods: {
    getImageUrl(img) {
      return img || '';
  },
    nextImage(index) {
      const total = this.produits[index].images.length;
      this.currentIndexes[index] = (this.currentIndexes[index] + 1) % total;
    },
    prevImage(index) {
      const total = this.produits[index].images.length;
      this.currentIndexes[index] = (this.currentIndexes[index] - 1 + total) % total;
    }
  }
};
</script>

<style scoped>
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

/* Flèches */
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
</style>
