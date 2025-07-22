<template>
  <div class="product-card">
    <!-- CARROUSEL -->
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

    <!-- Infos produit -->
    <div class="product-info">
      <h2 class="product-title">{{ produit.nom }}</h2>
      <p class="product-description">{{ produit.description }}</p>
      <div class="cart-actions">
        <p class="product-price">{{ produit.prix.toFixed(2) }} €</p>
        <router-link
        :to="{
          path: `/produit/${produit._id || produit.id}`,
          query: { from: 'bijouxchev' }  // ← adapte le nom de catégorie ici
        }"
        class="add-to-cart"
      >
        VOIR
      </router-link>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BijouxchevProduit',
  props: {
    produit: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      currentIndex: 0,
      direction: 'right'
    };
  },
  computed: {
    images() {
      return this.produit.images;
    },
    transitionName() {
      return this.direction === 'right' ? 'slide-right' : 'slide-left';
    }
  },
  methods: {
    nextImage() {
      if (this.currentIndex < this.images.length - 1) {
        this.direction = 'right';
        this.currentIndex++;
      }
    },
    prevImage() {
      if (this.currentIndex > 0) {
        this.direction = 'left';
        this.currentIndex--;
      }
    }
  }
};
</script>


<style scoped>
/* === SLIDE ANIMATIONS === */
.slide-right-enter-active, .slide-right-leave-active,
.slide-left-enter-active, .slide-left-leave-active {
  transition: all 0.4s ease;
  position: absolute;
  width: 100%;
}
.slide-right-enter-from { transform: translateX(100%); opacity: 0; }
.slide-right-leave-to { transform: translateX(-100%); opacity: 0; }
.slide-left-enter-from { transform: translateX(-100%); opacity: 0; }
.slide-left-leave-to { transform: translateX(100%); opacity: 0; }

/* === PRODUCT CARD === */
.product-card {
  background-color: #fff;
  border-radius: 20px;
  overflow: hidden;
  width: 260px;
  margin: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Lucida Sans', sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.product-card:hover {
  transform: scale(1.03);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

/* === CAROUSEL === */

.carousel {
  position: relative;
  width: 100%;
  height: 240px;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* === ARROWS === */
.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #333;
  transition: color 0.3s ease;
  z-index: 1;
}
.arrow:hover { color: #8c6da2; }
.arrow.left { left: 8px; }
.arrow.right { right: 8px; }

/* === PRODUCT INFO === */
.product-info {
  padding: 1.2rem;
  text-align: left;
}
.product-title {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.4rem;
}
.product-description {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 0.8rem;
}
.cart-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}
.product-price {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin: 0;
  padding-left: 0.6rem;
}
.add-to-cart {
  background-color: #98babb;
  color: black;
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1rem;
  font-size: 0.86rem;
  cursor: pointer;
  text-decoration: none;
  margin-right: 0.6rem;
  transition: background-color 0.3s ease;
}
.add-to-cart:hover {
  background-color: #8c6da2;
  color: whitesmoke;
}
</style>
