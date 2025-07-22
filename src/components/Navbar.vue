<template>
  <header>
    <!-- Logo principal -->
    <div class="logo-area">
      <img src="/assets/images/logo-gif.gif" alt="Logo Arc En Ciel" />

      <!-- Groupe des icônes + barre de recherche -->
      <div class="icon-group">
        <!-- Barre de recherche -->
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

        <!-- Panier -->
        <router-link to="/panier" class="cart-icon" aria-label="Panier">
          <img src="@/assets/images/logo_panier.png" alt="Panier" />
          <span class="cart-badge" v-if="totalArticles > 0">{{ totalArticles }}</span>
        </router-link>
      </div>
    </div>

    <!-- Navigation -->
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
import { getTotalQuantite } from '../utils/panier.js';

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
/* STRUCTURE */
header {
  width: 100%;
  position: relative;
  overflow-x: hidden;
}

.logo-area {
  background-color: #f1dad7;
  text-align: center;
  padding: 1rem 0;
  margin-bottom: 0.3rem;
  position: relative;
}

.logo-area img {
  height: 140px;
}

/* ICÔNES + BARRE DE RECHERCHE */
.icon-group {
  position: absolute;
  top: 60px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 14px;
}

/* BARRE DE RECHERCHE INLINE */
.search-inline {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  padding-left: 2rem;
  padding-right: 0.8rem;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
  border-radius: 30px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transform: scale(0.88); /* ✅ Réduction globale de la taille */
}



.search-icon-inside {
  position: absolute;
  left: 0.8rem;
  color: #e20e80;
  font-size: 1.2rem;
  pointer-events: none;
}

.search-inline input {
  border: none;
  outline: none;
  background: transparent;
  width: 170px;
  font-family: 'Raleway', sans-serif;
  font-size: 0.95rem;
  color: #333;

  /* ✅ Nouvelle ligne pour décaler le curseur */
  margin-left: 1.2rem;
}


/* PANIER */
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
  top: -8px;
  right: -5px;
  background-color: #000;
  color: #fff;
  font-size: 0.72rem;
  font-weight: bold;
  font-family: 'Lucida Sans', sans-serif;
  padding: 2px 6px;
  border-radius: 50%;
}

/* NAVIGATION */
.top-nav {
  background-color: rgba(255, 255, 255, 0.676);
  padding: 0.7rem 0;
  width: 100%;
  z-index: 9999;
  position: relative;
}

.nav-links {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 3rem;
  font-family: 'Raleway', sans-serif;
  font-size: 1.3rem;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  background-color: #f1dad7;
  color: #e20e80;
}

/* RESPONSIVE */
@media screen and (max-width: 768px) {
  .logo-area img {
    height: 100px;
  }

  .icon-group {
    top: 10px;
    right: 15px;
    flex-direction: column;
    align-items: flex-end;
  }

  .search-inline {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    max-width: 240px;
    padding-left: 2.2rem;
  }

  .search-inline input {
    width: 100%;
  }

  .cart-icon {
    width: 40px;
    height: 40px;
  }

  .cart-icon img {
    width: 100%;
    height: 100%;
  }

  .cart-badge {
    font-size: 0.65rem;
    padding: 1px 4px;
  }

  .nav-links {
    flex-direction: column;
    gap: 1rem;
    font-size: 1.2rem;
    padding: 1rem 0;
  }

  .top-nav {
    padding: 0.5rem;
  }
}

/* ANIMATION */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
