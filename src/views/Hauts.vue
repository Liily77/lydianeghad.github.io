<template>
  <div class="home">

  
    <!-- RETOUR ACCUEIL -->
    <div class="back-home">
      <router-link to="/#categories" class="back-button">← Accueil</router-link>
    </div>

    <!-- FICHES PRODUITS -->
    <div id="hauts-cards" class="products-container">
      <BagueProduit
        v-for="produit in produitsHauts"
        :key="produit._id"
        :produit="produit"
        :getImageUrl="getImageUrl"
      />
    </div>

    <!-- BANNIÈRE -->
    <div class="banner">
      <!-- 👇 image conservée (bagues) -->
      <img src="/assets/images/banner-bagues.jpg" alt="Bannière Hauts" class="banner-img" />
      <div class="banner-text">
        <div class="banner-text-box">
          <p>Chemises, blouses, tops, pulls : vos indispensables.</p>
          <p>Une sélection pratique et stylée.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HautProduit from '../components/HautProduit.vue'
import { api } from '@/utils/api'

export default {
  name: 'Hauts',
  components: { BagueProduit: HautProduit },
  data() {
    return { produitsHauts: [] }
  },
  methods: {
    getImageUrl(img) {
      if (!img) return '/assets/images/image-placeholder.png'
      const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
      return img.startsWith('/uploads') ? `${backendUrl}${img}` : img
    }
  },
  async mounted() {
    window.scrollTo(0, 0)
    try {
      const all = await api('/api/produits', { credentials: 'include' })
      this.produitsHauts = (all || []).filter(
        p => (p.categorie || '').toLowerCase() === 'hauts'
      )
    } catch (err) {
      console.error('[Hauts.vue] Erreur chargement hauts :', err)
    }
  }
}
</script>




<style scoped>
.home {
  background-color: #f9f4f0;
  padding: 0;
  margin: 0;
  overflow-x: hidden;
  max-width: 100vw;
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

/* BANNIÈRE */
.banner {
  position: relative;
  width: 100%;
  height: 50vh;  /* hauteur dynamique */
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


/* CONTENEUR DE PRODUITS */
.products-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  padding: 0 2rem;
  gap: 1.5rem;
}


@media (max-width: 768px) {
  
    .back-home {
      padding-left: clamp(0.1rem, 1vw, 0.5rem);
      width: fit-content;
    }
  
    .back-button {
      font-size: clamp(0.6rem, 2vw, 0.85rem);
      padding: clamp(0.3rem, 1vw, 0.6rem) clamp(0.6rem, 2vw, 1rem);
    }
  
    .products-container {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      justify-items: center;
      gap: clamp(0.5rem, 3vw, 1rem);
      padding: clamp(0.5rem, 3vw, 1rem);
    }
  
    .product-card {
      width: clamp(140px, 90%, 220px);
      margin: 0;
      transform: none;
    }
  
    .product-card:hover {
      transform: none !important;
      box-shadow: none !important;
    }
  
    .banner {
      position: relative;
      height: auto;
      margin-top: 1.5rem;
    }
  
    .banner-img {
      width: 100%;
      height: auto;
      max-height: 180px;
      object-fit: cover;
      display: block;
      margin-top: 30px;
    }
  
    .banner-text {
      position: absolute;
      bottom: 35px;
      left: 50%;
      transform: translateX(-50%);
      width: 90%;
      max-width: 340px;
      background-color: rgba(245, 237, 224, 0.9);
      border-radius: 10px;
      padding: 0.5rem 0.5rem;
      box-sizing: border-box;
      text-align: center;
    }
  
    .banner-text-box {
      background: transparent;
      padding: 0;
      font-size: 0.6rem;
      line-height: 1.3;
      color: #333;
      white-space: normal;
      overflow-wrap: break-word;
      word-break: break-word;
    }
  }
  
 
</style>
