<template>
  <header>
    <div class="logo-area">
      <img src="/assets/images/logo-gif.gif" alt="Logo Arc En Ciel" />

      <div class="icon-group">
        <transition name="fade">
          <div class="search-inline" v-if="showSearch">
            <span class="search-icon-inside">🔍</span>
            <input
              type="text"
              v-model="termeRecherche"
              placeholder="Rechercher un produit..."
              @input="miseAJourRecherche"
            />
          </div>
        </transition>

        <router-link to="/panier" class="cart-icon" aria-label="Panier">
          <img src="@/assets/images/logo_panier.png" alt="Panier" />
          <span class="cart-badge" v-if="totalArticles > 0">{{ totalArticles }}</span>
        </router-link>
      </div>
    </div>

    <div class="top-nav">
      <nav class="nav-links">
        <router-link to="/">Accueil</router-link>
        <router-link to="/nouveautes">Nouveautés</router-link>
        <router-link to="#">À propos</router-link>
        <router-link to="/contact">Contact</router-link>
      </nav>
    </div>
  </header>
</template>

<script>
import { getTotalQuantite } from '@/utils/panier.js';
export default {
  name: 'Navbar',
  data() {
    return {
      totalArticles: 0,
      showSearch: true,
      termeRecherche: ''
    };
  },
  mounted() {
    this.totalArticles = getTotalQuantite();
    window.addEventListener('maj-panier', this.updateQuantite);
  },
  beforeUnmount() {
    window.removeEventListener('maj-panier', this.updateQuantite);
  },
  methods: {
    updateQuantite() {
      this.totalArticles = getTotalQuantite();
    },
    miseAJourRecherche() {
      if (this.termeRecherche.trim()) {
        this.$router.push({ path: '/recherche', query: { q: this.termeRecherche } });
      }
    }
  }
};
</script>

<style scoped>

header {
  width: 100%;
  position: relative;
  overflow: hidden;
}

/* Logo + fond rose */
.logo-area {
  background-color: #f1dad7;
  text-align: center;
  padding: 1rem 0;
  position: relative;
 
  margin-bottom: 0.3rem;
}
.logo-area img {
  height: 140px;
}

/* Barre + panier group */
.icon-group {
  position: absolute;
  top: 50%;
  right: 2rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 10;
}

/* Barre de recherche inline (desktop) */
.search-inline {
  position: static;  
  background: #fff;
  padding: 0.3rem 1.2rem 0.3rem 2rem;
  border-radius: 30px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  max-width: 180px;
  display: flex;
  align-items: center;
}
.search-inline .search-icon-inside {
  position: absolute;
  left: 1rem;
  color: #e20e80;
  font-size: 1rem;
}
.search-inline input {
  border: none;
  outline: none;
  background: transparent;
  margin-left: 1.2rem;
  font-size: 0.95rem;
  width: 100%;
}

/* Panier */
.cart-icon {
  position: relative;
  width: 60px;
  height: 60px;
}
.cart-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.cart-badge {
  position: absolute;
  top: -1px;
  right: 6px;
  font-family: Arial, Helvetica, sans-serif;
  background: #000;
  color: #fff;
  font-size: 0.70rem;
  padding: 2px 6px;
  border-radius: 50%;
}

/* Navigation desktop */
.top-nav {
  background: rgba(255,255,255,0.9);
  padding: 0.4rem 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.nav-links {
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  font-family: 'Raleway', sans-serif;
  font-size: 1.1rem;
}
.nav-links a {
  text-decoration: none;
  color: #333;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background 0.3s ease, color 0.3s ease;
}
.nav-links a:hover {
  background: #f1dad7;
  color: #e20e80;
}


/* ================= */
/* Styles MOBILE ONLY */
/* ================= */

@media (max-width: 768px) {

  .logo-area {
    padding: 1rem 0 5em;
  }

  .logo-area > img:first-of-type {
    height: clamp(70px, 25vw, 100px); 
    position: relative;
    right: clamp(20px, 6vw, 50px);    
    bottom: clamp(-20px, -5vh, -40px);
  }

  .search-inline {
    position: absolute !important;
    padding: 0.1rem 0.5rem 0.1rem 1rem; 
    top: calc(100% + 1.5rem + clamp(8px, 2vh, 15px));
    transform: translateX(-50%);
    width: clamp(80px, 25vw, 100px);
    margin-top: clamp(0px, 0.2vh, 1px);
    margin-bottom: clamp(5px, 1.3vh, 10px);
    border-radius: 20px; 
  }

  .search-inline input {
    font-size: clamp(0.6rem, 1.5vw, 0.8rem); 
  }

  .search-inline .search-icon-inside {
    position: absolute;
    left: 1rem;
    color: #e20e80;
    font-size: clamp(0.6rem, 1.5vw, 0.9rem); 
  }

  .top-nav {
    padding: 0.1em 0;
  }

  .nav-links {
    gap: 1.5rem;
    font-size: clamp(0.7rem, 2.5vw, 0.9rem);
    font-weight: 550;
  }

  .nav-links a {
    padding: 0.3rem 0.6rem;
  }

  .cart-icon { 
    position: relative;
    width: clamp(50px, 9.5vw, 60px);   
    height: clamp(50px, 9.5vw, 60px); 
  }

  .cart-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .cart-badge {
    position: absolute;
    top: clamp(5px, 1.3vh, 8px);
    right: clamp(3px, 1vw, 6px);
    font-size: clamp(0.55rem, 1.2vw, 0.65rem); 
    padding: clamp(1px, 0.3vw, 2px) clamp(3px, 0.6vw, 5px); 
    border-radius: 50%;
    background: #000;
    color: #fff;
  }
}



</style>
