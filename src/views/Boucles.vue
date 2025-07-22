<template>
  <div class="boucles-page">
    <!-- TITRE -->
    <div class="section-title">
      <img src="/assets/images/titre-boucles.jpg" alt="Nos Boucles d'oreilles" />
    </div>

    <!-- RETOUR ACCUEIL -->
    <div class="back-home">
      <router-link to="/#categories" class="back-button">← Accueil</router-link>
    </div>

    <!-- FICHES PRODUITS -->
    <div id="boucles-cards" class="products-container">
      <BouclesProduit
        v-for="produit in produitsBoucles"
        :key="produit.id"
        :produit="produit"
      />
    </div>

    <!-- BANNIÈRE -->
    <div class="banner">
      <img src="/assets/images/banner-boucles.jpg" alt="Bannière Boucles d’oreilles" class="banner-img" />
      <div class="banner-text">
        <div class="banner-text-box">
          <p>Exprimez votre style avec nos boucles d’oreilles en pierres naturelles.</p>
          <p>Chaque paire incarne féminité, force et délicatesse.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BouclesProduit from '../components/BouclesProduit.vue'

export default {
  name: 'Boucles',
  components: {
    BouclesProduit
  },
  data() {
    return {
      produitsBoucles: []
    }
  },
  mounted() {
    window.scrollTo(0, 0)
    fetch('/produits')
      .then(res => res.json())
      .then(data => {
        this.produitsBoucles = data.filter(p => p.categorie.toLowerCase().includes('boucles'))
      })
      .catch(err => console.error('Erreur chargement boucles :', err))
  }
}
</script>


<style scoped>
.boucles-page {
  background-color: #f9f4f0;
  padding-bottom: 4rem;
}

/* TITRE */
.section-title {
  text-align: center;
  margin: 3rem 0 2rem;
}
.section-title img {
  max-width: 800px;
  width: 60%;
}

/* BOUTON ACCUEIL */
.back-home {
  margin-top: 2.5rem;
  margin-left: 3rem;
  margin-bottom: 2rem;
}
.back-button {
  display: inline-block;
  background-color: #f3e8f5;
  color: #a074ae;
  padding: 0.5rem 1rem;
  font-family: 'Lucida Sans', sans-serif;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}
.back-button:hover {
  background-color: #e20e80;
  color: #fff;
}

/* FICHES PRODUITS */
.products-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  padding: 0 2rem;
  gap: 1.5rem;
}

/* BANNIÈRE */
.banner {
  position: relative;
  width: 100%;
  height: 50vh;
  overflow: hidden;
  margin-top: 4rem;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.banner-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  text-align: center;
}
.banner-text-box {
  background-color: rgba(245, 237, 224, 0.858);
  font-family: 'Raleway', sans-serif;
  padding: 1rem 2rem;
  border-radius: 10px;
  color: #333;
  font-size: 1.4rem;
  line-height: 1.6;
}
</style>
