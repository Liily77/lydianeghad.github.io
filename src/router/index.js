// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// Vues statiques
import Home from '../views/Home.vue'
import Bagues from '../views/Bagues.vue'
import Colliers from '../views/Colliers.vue'
import Bracelets from '../views/Bracelets.vue'
import Boucles from '../views/Boucles.vue'
import Chapelets from '../views/Chapelets.vue'
import Bijouxchev from '../views/Bijouxchev.vue'
import Portescles from '../views/Portescles.vue'
import Malas from '../views/Malas.vue'
import Parures from '../views/Parures.vue'
import Cartesdiv from '../views/Cartesdiv.vue'
import Pendules from '../views/Pendules.vue'
import Produit from '../views/Produit.vue'
import Admin from '../views/Admin.vue'
import Nouveautes from '../views/Nouveautes.vue'
import Rechercher from '../components/Rechercher.vue'
import Contact from '../views/Contact.vue'
import Merci from '../views/Merci.vue' 

// Routes
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/bagues', name: 'Bagues', component: Bagues },
  { path: '/colliers', name: 'Colliers', component: Colliers },
  { path: '/bracelets', name: 'Bracelets', component: Bracelets },
  { path: '/boucles', name: 'Boucles', component: Boucles },
  { path: '/chapelets', name: 'Chapelets', component: Chapelets },
  { path: '/bijouxchev', name: 'Bijouxchev', component: Bijouxchev },
  { path: '/portescles', name: 'Portescles', component: Portescles },
  { path: '/malas', name: 'Malas', component: Malas },
  { path: '/parures', name: 'Parures', component: Parures },
  { path: '/cartesdiv', name: 'Cartesdiv', component: Cartesdiv },
  { path: '/pendules', name: 'Pendules', component: Pendules },
  { path: '/produit/:id', name: 'Produit', component: Produit },
  { path: '/admin', name: 'Admin', component: Admin },
  { path: '/panier', name: 'Panier', component: () => import('../views/Panier.vue') },
  { path: '/nouveautes', name: 'Nouveautes', component: Nouveautes },
  { path: '/recherche', name: 'Rechercher', component: Rechercher },
  { path: '/contact', name: 'Contact', component: Contact },
  { path: '/merci', name: 'Merci', component: Merci }
]

// Router
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            el: to.hash,
            behavior: 'smooth'
          })
        }, 300)
      })
    }
    return { top: 0 }
  }
})

export default router
