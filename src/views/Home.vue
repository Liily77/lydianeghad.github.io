<template>
  <div class="home">
    <!-- BANNIÈRE -->
    <div class="banner">
      <img
        src="/assets/images/banner-pagegarde.png"
        alt="Bannière Arc En Ciel"
        class="banner-img"
      />
      <div class="banner-text">
        <div class="banner-text-box">
          <p>Des essentiels faciles à vivre, sélectionnés pour durer et vous accompagner tous les jours.</p>
          <p>Des vêtements que l’on aime porter et quelques bijoux pour compléter l’ensemble.</p>
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
      <router-link to="/boucles#boucles-cards" class="category-item">
        <img src="/assets/images/BOUCLES.jpg" alt="Boucles" class="category-image" />
      </router-link>
      <router-link to="/chapelets#chapelets-cards" class="category-item">
        <img src="/assets/images/CHAPELETS.png" alt="Chapelets" class="category-image" />
      </router-link>
      <router-link to="/bijouxchev#bijouxchev-cards" class="category-item">
        <img src="/assets/images/BIJOUXCHEV.png" alt="Bijoux de cheville" class="category-image" />
      </router-link>
      <router-link to="/portescles#portecles-cards" class="category-item">
        <img src="/assets/images/PORTECLES.png" alt="Porte‑clés" class="category-image" />
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
      <router-link to="/pendules#pendules-cards" class="category-item">
        <img src="/assets/images/PENDULES.png" alt="Pendules" class="category-image" />
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  background-color: #f9f4f0;
  margin: 0;
  padding: 0;
}

/* BANNIÈRE — voir toute l’image */

.banner {
  position: relative;
  width: 100%;
  height: 56vh;               /* ta hauteur habituelle */
  overflow: hidden;
  background-color: #f1dad7;  /* ⬅︎ rose du bandeau (adapte si besoin) */
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: contain;        /* montre toute l’image */
  object-position: center;
  display: block;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
}

/* Bloc texte centré + remonté */
.banner-text {
  position: absolute;
  top: 45%;                 /* ↑ remonte (ajuste 38–44% si besoin) */
  left: 50%;
  transform: translate(-50%, -50%); /* centre vraiment (plus de décalage) */
  width: 100%;
  text-align: center;
}

/* Cartouche + lignes sur une seule ligne */
.banner-text-box {
  display: inline-block;    /* s’adapte au contenu */
  background-color: rgba(245, 237, 224, 0.9);
  font-family: 'Raleway', sans-serif;
  padding: 1rem 2rem;
  border-radius: 10px;
  color: #333;
  font-size: 1.2rem;
  line-height: 1.4;
  max-width: 90vw;          /* évite de dépasser l’écran */
}

/* Chaque phrase sur une seule ligne (desktop) */
.banner-text-box p {
  margin: 0.25rem 0;
  white-space: nowrap;      /* pas de retour à la ligne */
}




/* Mobile */
@media (max-width: 768px) {
  .banner { height: 62vh; }        /* un peu plus haut sur mobile */
  .banner-text { bottom: 6%; }      /* remonte légèrement si besoin */
}

/* CATÉGORIES */
.categories-container {
  display: flex;
  justify-content: center;
  gap: 4rem;
  flex-wrap: wrap;
  margin: 3rem 0;
  padding: 0 1rem;
}
.category-item {
  width: 220px;
  text-align: center;
}
.category-image {
  width: 220px;
  height: 220px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.3s ease-in-out;
}
.category-item:hover .category-image {
  transform: scale(1.3);
}

/* ================= */
/* Styles MOBILE ONLY */
/* ================= */
@media (max-width: 768px) {
  .banner {
    height: clamp(25vh, 30vh, 35vh);
    border-bottom-left-radius: clamp(10px, 2vw, 20px);
    border-bottom-right-radius: clamp(10px, 2vw, 20px);
  }

  /* centre et limite la largeur du cartouche sur mobile */
  .banner-text {
    position: absolute;
    top: 52%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 92%;
    max-width: 340px;
    text-align: center;
  }

  .banner-text-box {
    padding: clamp(0.5rem, 2vw, 0.8rem) clamp(0.8rem, 3vw, 1rem);
    font-size: clamp(0.85rem, 2.5vw, 1rem);
    border-radius: clamp(5px, 1vw, 10px);
  }

  .banner-text-box p { white-space: normal; }
}

/* ======================== */
/* Laptops (769–1366 px)    */
/* ======================== */
@media (min-width: 769px) and (max-width: 1366px) {
  .banner-text {
    position: absolute;
    top: 46%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    text-align: center;
  }

  .banner-text-box {
    max-width: min(48vw, 680px);  /* évite de dépasser l'image (contain) */
    font-size: 1rem;
    padding: .75rem 1.2rem;
    white-space: normal;
    overflow-wrap: anywhere;
  }
}

/* Ajustement petits laptops (769–1024 px) */
@media (min-width: 769px) and (max-width: 1024px) {
  .banner-text { top: 48%; }
  .banner-text-box {
    max-width: min(46vw, 600px);
    font-size: .95rem;
  }
}

/* ======================== */
/* Grands écrans (≥1600 px) */
/* ======================== */
@media (min-width: 1600px) {
  .banner-text {
    position: absolute;
    top: 42%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  .banner-text-box {
    max-width: min(62vw, 900px);
  }

  .banner-text-box p { white-space: nowrap; } /* 1 ligne par phrase si possible */
}



</style>
