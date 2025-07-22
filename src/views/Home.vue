<template>
  <div class="home">
    <!-- BANNIÈRE -->
    <div class="banner">
      <img src="/assets/images/banner-pagegarde.png" alt="Bannière Arc En Ciel" class="banner-img" />
      <div class="banner-text">
        <div class="banner-text-box">
          <p>Découvrez des bijoux spirituels façonnés à la main, où chaque pierre naturelle porte en elle une énergie unique.</p>
          <p>Créations artisanales et uniques, elles sont conçues pour harmoniser corps et esprit.</p>
        </div>
      </div>
    </div>

    <!-- CATÉGORIES -->

  <div id="categories" class="categories-container">

  <router-link to="/bagues#bagues-cards" class="category-item">
  <img src="/assets/images/BAGUES.png" alt="Bagues" class="category-image" />
  </router-link>

  <router-link to="/colliers#colliers-cards" class="category-item">
  <img src="/assets/images/COLLIERS.png" alt="Colliers" class="category-image" />
  </router-link>

  <router-link to="/bracelets#bracelets-cards" class="category-item">
  <img src="/assets/images/BRACELETS.png" alt="Bracelets" class="category-image" />
  </router-link>

  <router-link to="boucles#boucles-cards" class="category-item">
  <img src="/assets/images/BOUCLES.jpg" alt="Boucles" class="category-image" />
  </router-link>

  <router-link to="/chapelets#chapelets-cards" class="category-item">
  <img src="/assets/images/CHAPELETS.png" alt="Chapelets" class="category-image" />
  </router-link>

  <router-link to="/bijouxchev#bijouxchev-cards" class="category-item">
  <img src="/assets/images/BIJOUXCHEV.png" alt="Bijoux de cheville" class="category-image" />
  </router-link>

  <router-link to="/portescles#portecles-cards" class="category-item">
  <img src="/assets/images/PORTECLES.png" alt="Porte-clés" class="category-image" />
  </router-link>

  <router-link to="/malas#malas-cards" class="category-item">
  <img src="/assets/images/MALAS.png" alt="Malas" class="category-image" />
  </router-link>

  <router-link to="/parures#parures-cards" class="category-item">
  <img src="/assets/images/PARURES.png" alt="Parures" class="category-image" />
  </router-link>

  <router-link to="/cartesdiv#cartesdiv-cards" class="category-item">
  <img src="/assets/images/CARTESDIV.png" alt="Cartes divinatoires" class="category-image" />
  </router-link>

  <router-link to="/pendules#pendule-cards" class="category-item">
  <img src="/assets/images/PENDULES.png" alt="Pendules" class="category-image" />
  </router-link>

</div>

  </div>
</template>

<script>
export default {
  name: 'Home',
}
</script>

<style scoped>
.home {
  background-color: #f9f4f0;
  padding: 0;
  margin: 0;
}

.banner {
  position: relative;
  width: 100%;
  height: 50vh;
  z-index: 1; /* 🔽 assure que la bannière est en dessous */
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
  font-size: 1.2rem;
  line-height: 1.6;
  text-shadow: none;
}

.categories-container {
  display: flex;
  justify-content: center;
  gap: 4rem;
  flex-wrap: wrap;
  margin: 3rem 0;
}

.category-item {
  width: 220px;
  text-align: center;
}



.category-image {
  width: 220px;
  height: 220px;
  object-fit: cover;
  cursor: pointer;
  border-radius: 50%;
  transition: transform 0.3s ease-in-out;
}


.category-item:hover .category-image {
  transform: scale(1.3); /* effet de zoom */
}


</style>

  