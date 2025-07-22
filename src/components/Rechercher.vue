<template>
  <div class="recherche-page">
    <h2 v-if="$route.query.q">Résultats pour "{{ $route.query.q }}"</h2>

    <div v-if="resultats.length" class="grille-produits">
      <div
        v-for="(produit, index) in resultats"
        :key="produit._id"
        class="carte-produit"
      >
        <!-- SLIDER IMAGE -->
        <div class="slider-container">
          <button
            v-if="produit.images.length > 1"
            class="arrow left"
            @click="prevImage(index)"
          >‹</button>

          <img
            :src="produit.images[currentIndexes[index] || 0]"
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
        <router-link :to="`/produit/${produit._id}`" class="voir-btn">Voir</router-link>
      </div>
    </div>

    <div v-else class="aucun-resultat">
      Aucun résultat trouvé.
    </div>
  </div>
</template>

<script>
export default {
  name: 'Rechercher',
  data() {
    return {
      resultats: [],
      currentIndexes: {}
    };
  },
  watch: {
    '$route.query.q': {
      handler() {
        this.lancerRecherche();
      },
      immediate: true
    }
  },
  methods: {
    nextImage(index) {
      const total = this.resultats[index].images.length;
      this.currentIndexes[index] = (this.currentIndexes[index] + 1) % total;
    },
    prevImage(index) {
      const total = this.resultats[index].images.length;
      this.currentIndexes[index] = (this.currentIndexes[index] - 1 + total) % total;
    },
    async lancerRecherche() {
      const terme = this.$route.query.q;
      if (!terme) {
        this.resultats = [];
        return;
      }

      try {
        const reponse = await fetch(`/produits/recherche?q=${encodeURIComponent(terme)}`);
        const donnees = await reponse.json();
        this.resultats = donnees;
        this.currentIndexes = Object.fromEntries(donnees.map((_, i) => [i, 0]));
      } catch (error) {
        console.error("Erreur lors de la recherche :", error);
        this.resultats = [];
      }
    }
  }
};
</script>


<style scoped>
.recherche-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background-color: #fff;
  max-width: 1300px;
  margin: auto;
}

h2 {
  text-align: center;
  font-size: 2rem;
  color: #e20e80;
  margin-bottom: 2rem;
}

/* GRILLE FIXE non responsive */
.grille-produits {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}

/* CARTE comme Nouveautés */
.carte-produit {
  background: #f9f4f0;
  border-radius: 12px;
  padding: 1rem;
  width: 230px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

/* SLIDER */
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
.arrow.left { left: 10px; }
.arrow.right { right: 10px; }

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

.aucun-resultat {
  text-align: center;
  font-style: italic;
  color: #777;
  margin-top: 2rem;
}
</style>
