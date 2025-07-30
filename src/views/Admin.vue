<template>
  <div class="admin-page">
    <!-- Si pas connecté, afficher formulaire login -->
    <div v-if="!isLoggedIn" class="login-form">
      <h1>Connexion Admin</h1>
      <form @submit.prevent="seConnecter">
        <label>Utilisateur :
          <input type="text" v-model="loginUser" required />
        </label>
        <label>Mot de passe :
          <input type="password" v-model="loginPass" required />
        </label>
        <button type="submit" :disabled="isLoading">
          <span v-if="isLoading">Connexion...</span>
          <span v-else>Se connecter</span>
        </button>
        <p v-if="loginError" class="error-msg">{{ loginError }}</p>
      </form>
    </div>

    <!-- Sinon, afficher interface admin -->
    <div v-else>
      <h1 class="titre-centre">Gestion des produits 🛍️</h1>
      <button @click="seDeconnecter" class="logout-btn">Déconnexion</button>

      <!-- Filtres -->
      <div class="filters">
        <label>Filtrer par catégorie :
          <select v-model="filtreCategorie">
            <option value="">Toutes</option>
            <option
              v-for="cat in categoriesDisponibles"
              :key="cat"
              :value="cat"
            >
              {{ cat }}
            </option>
          </select>
        </label>

        <label>Recherche :
          <input
            type="text"
            v-model="rechercheTexte"
            placeholder="Nom ou description"
          />
        </label>
      </div>

      <div class="admin-layout">
        <!-- FORMULAIRE -->
        <form @submit.prevent="ajouterProduit" class="formulaire-ajout" novalidate>
          <h2>Ajouter un produit 🛒</h2>

          <label>Nom :
            <input
              type="text"
              v-model="nouveauProduit.nom"
              :class="{ 'input-error': errors.nom }"
              required
            />
            <span v-if="errors.nom" class="error-msg">{{ errors.nom }}</span>
          </label>

          <label>Description :
            <textarea
              v-model="nouveauProduit.description"
              :class="{ 'input-error': errors.description }"
              required
            ></textarea>
            <span v-if="errors.description" class="error-msg">{{ errors.description }}</span>
          </label>

          <label>Prix (€) :
            <input
              type="number"
              v-model.number="nouveauProduit.prix"
              :class="{ 'input-error': errors.prix }"
              min="0.01"
              step="0.01"
              required
            />
            <span v-if="errors.prix" class="error-msg">{{ errors.prix }}</span>
          </label>

          <label>Catégorie :
            <select
              v-model="categorieChoisie"
              :class="{ 'input-error': errors.categorie }"
              required
            >
              <option disabled value="">-- Choisir une catégorie --</option>
              <option
                v-for="cat in categoriesDisponibles"
                :key="cat"
                :value="cat"
              >
                {{ cat }}
              </option>
              <option value="autre">Autre (à préciser)</option>
            </select>
            <span v-if="errors.categorie" class="error-msg">{{ errors.categorie }}</span>
          </label>

          <label v-if="categorieChoisie === 'autre'">Nouvelle catégorie :
            <input
              type="text"
              v-model="nouvelleCategorie"
              :class="{ 'input-error': errors.nouvelleCategorie }"
              placeholder="ex: pendules"
              required
            />
            <span v-if="errors.nouvelleCategorie" class="error-msg">{{ errors.nouvelleCategorie }}</span>
          </label>

          <label
            v-for="(file, index) in fichiersImages"
            :key="index"
          >
            Image {{ index + 1 }} :
            <input
              type="file"
              :ref="'fichierImage' + index"
              @change="onFileChange($event, index)"
              accept="image/*"
            />
          </label>

          <button
            type="submit"
            class="ajouter-btn"
            :disabled="isLoading"
          >
            <span v-if="isLoading">⏳ Ajout en cours...</span>
            <span v-else>Ajouter le produit</span>
          </button>

          <p v-if="formMessage" :class="{'error-msg': formError, 'success-msg': !formError}">
            {{ formMessage }}
          </p>
        </form>

        <!-- TABLEAU -->
        <div class="tableau-produits" v-if="produitsFiltres.length">
          <h2>📦 Produits filtrés ({{ produitsFiltres.length }})</h2>
          <div
            v-for="produit in produitsFiltres"
            :key="produit._id || produit.id"
            class="produit-item"
          >
            <input v-model="produit.nom" />
            <input v-model="produit.description" />
            <input type="number" v-model.number="produit.prix" />
            <input v-model="produit.categorie" />

            <div class="img-preview" v-if="produit.images?.length">
              <img
                v-for="(img, i) in produit.images"
                :key="i"
                :src="img"
                alt="Image produit"
              />
            </div>

            <div class="btn-droite">
              <button @click="modifierProduit(produit)">💾 Modifier</button>
              <button @click="supprimerProduit(produit._id || produit.id)">
                🗑 Supprimer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/utils/api'

export default {
  name: 'Admin',
  data() {
    return {
      // Login
      loginUser: '',
      loginPass: '',
      isLoggedIn: false,
      loginError: '',
      isLoading: false,

      // Formulaire produits
      nouveauProduit: { nom: '', description: '', prix: null },
      categorieChoisie: '',
      nouvelleCategorie: '',
      fichiersImages: [null, null, null, null, null],

      produits: [],
      filtreCategorie: '',
      rechercheTexte: '',
      formMessage: '',
      formError: false,
      errors: {},

      categoriesFixes: [
        'bague', 'collier', 'bracelet', 'chapelet',
        'boucles doreilles', 'bijoux de cheville',
        'malas', 'parures', 'portecles',
        'cartesdiv', 'pendule'
      ]
    }
  },
  computed: {
    produitsFiltres() {
      return this.produits.filter(p => {
        const matchCat = !this.filtreCategorie ||
          p.categorie?.toLowerCase() === this.filtreCategorie.toLowerCase()
        const texte = this.rechercheTexte.toLowerCase()
        return p.nom.toLowerCase().includes(texte)
            || p.description.toLowerCase().includes(texte)
      })
    },
    categoriesDisponibles() {
      const dyn = [...new Set(this.produits.map(p => p.categorie?.toLowerCase()))].filter(Boolean)
      return dyn.length ? dyn : this.categoriesFixes
    }
  },
  async mounted() {
    const token = localStorage.getItem('admin_token')
    if (token) {
      this.isLoggedIn = true
      await this.chargerProduits()
    }
  },
  methods: {
    async seConnecter() {
      this.loginError = ''
      this.isLoading = true
      try {
        const { token } = await api('/api/login', {
          method: 'POST',
          body: JSON.stringify({
            username: this.loginUser,
            password: this.loginPass
          })
        })
        localStorage.setItem('admin_token', token)
        this.isLoggedIn = true
        await this.chargerProduits()
      } catch (err) {
        this.loginError = err.message || 'Erreur serveur, réessayez plus tard'
      } finally {
        this.isLoading = false
      }
    },

    seDeconnecter() {
      localStorage.removeItem('admin_token')
      this.isLoggedIn = false
      this.loginUser = ''
      this.loginPass = ''
      this.produits = []
    },

    onFileChange(event, index) {
      this.fichiersImages[index] = event.target.files[0]
    },

    async chargerProduits() {
      try {
        this.produits = await api('/api/produits', {
          headers: { Authorization: 'Bearer ' + localStorage.getItem('admin_token') }
        })
      } catch (err) {
        if (err.message.includes('401')) return this.seDeconnecter()
        console.error('❌ Erreur chargement produits :', err)
      }
    },

    validateForm() {
      this.errors = {}
      if (!this.nouveauProduit.nom) this.errors.nom = 'Le nom est requis'
      if (!this.nouveauProduit.description) this.errors.description = 'La description est requise'
      if (!this.nouveauProduit.prix || this.nouveauProduit.prix <= 0)
        this.errors.prix = 'Le prix doit être supérieur à 0'
      if (!this.categorieChoisie) this.errors.categorie = 'La catégorie est requise'
      if (this.categorieChoisie === 'autre' && !this.nouvelleCategorie)
        this.errors.nouvelleCategorie = 'Veuillez préciser la nouvelle catégorie'
      return Object.keys(this.errors).length === 0
    },

    async ajouterProduit() {
      if (!this.validateForm()) {
        this.formMessage = 'Veuillez corriger les erreurs avant de soumettre.'
        this.formError = true
        return
      }
      this.isLoading = true
      this.formMessage = ''
      try {
        const formData = new FormData()
        const catFinale = this.categorieChoisie === 'autre'
          ? this.nouvelleCategorie.toLowerCase()
          : this.categorieChoisie.toLowerCase()

        formData.append('nom', this.nouveauProduit.nom)
        formData.append('description', this.nouveauProduit.description)
        formData.append('prix', this.nouveauProduit.prix)
        formData.append('categorie', catFinale)
        this.fichiersImages.forEach(f => f && formData.append('images', f))

        const data = await api('/api/produits', {
          method: 'POST',
          headers: { Authorization: 'Bearer ' + localStorage.getItem('admin_token') },
          body: formData
        })
        this.produits.push(data)
        this.formMessage = '✅ Produit ajouté !'
        this.formError = false
        this.resetFormulaire()
      } catch (err) {
        this.formMessage = '❌ Erreur ajout produit'
        this.formError = true
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    resetFormulaire() {
      this.nouveauProduit = { nom: '', description: '', prix: null }
      this.categorieChoisie = ''
      this.nouvelleCategorie = ''
      this.fichiersImages = [null, null, null, null, null]
      for (let i = 0; i < 5; i++) {
        const ref = this.$refs['fichierImage' + i]
        if (ref) {
          if (Array.isArray(ref)) ref[0].value = ''
          else ref.value = ''
        }
      }
    },

    async supprimerProduit(id) {
      if (!confirm('❓ Supprimer ce produit ?')) return
      try {
        await api(`/api/produits/${id}`, {
          method: 'DELETE',
          headers: { Authorization: 'Bearer ' + localStorage.getItem('admin_token') }
        })
        this.produits = this.produits.filter(p => (p._id||p.id) !== id)
      } catch (err) {
        alert('❌ Erreur suppression')
        console.error(err)
      }
    },

    async modifierProduit(produit) {
      const id = produit._id || produit.id
      try {
        const updated = await api(`/api/produits/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + localStorage.getItem('admin_token')
          },
          body: JSON.stringify(produit)
        })
        const idx = this.produits.findIndex(p => (p._id||p.id) === id)
        if (idx !== -1) this.$set(this.produits, idx, updated)
        this.formMessage = '✔ Produit modifié !'
        this.formError = false
      } catch (err) {
        this.formMessage = '❌ Erreur modification'
        this.formError = true
        console.error(err)
      }
    }
  }
}
</script>



<style scoped>
.admin-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background: #f1dad7;
  max-width: 1300px;
  margin: auto;
}

/* ===== Login ===== */
.login-form {
  max-width: 320px;
  margin: 3rem auto;
  padding: 1.5rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fafafae0;
}

.login-form h1 {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-form label {
  display: block;
  font-weight: 600;
  margin-bottom: 1rem;
}

.login-form input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  margin-top: 0.3rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.login-form button {
  display: block;
  width: 100%;
  padding: 0.6rem;
  margin-top: 1rem;
  background: #98babb;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s ease;
}

.login-form button:hover:not(:disabled) {
  background: #8c6da2;
  color: #fff;
}

.error-msg {
  color: #d9534f;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* ===== Admin ===== */
.titre-centre {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}

.logout-btn {
  display: block;
  margin: 1rem 0 1rem auto;
  background: #e20e0e;
  color: #fff;
  padding: 0.6rem 0.9rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}


.logout-btn:hover {
  background: #9b0404;   
}


/* Filtres */
.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filters label {
  font-weight: bold;
  display: flex;
  flex-direction: column;
}

.filters select,
.filters input {
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
  margin-top: 0.3rem;
}

/* Layout général */
.admin-layout {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

/* Formulaire ajout */
.formulaire-ajout {
  background-color: #ffffffb7;               
  border: 1px solid #ddd;               
  border-radius: 10px;                  
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;                      
  margin-bottom: 1.5rem;                
}

.formulaire-ajout h2 {
  margin: 2rem 0 2rem; 
  font-size: 1.25rem;
}

.formulaire-ajout label {
  font-weight: 600;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.formulaire-ajout input,
.formulaire-ajout textarea,
.formulaire-ajout select {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.input-error {
  border-color: #d9534f !important;
}

.ajouter-btn {
  margin-top: 1rem;
  background: #98babb;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 8px;
  cursor: pointer;
  color: black;
  font-weight: bold;
  align-self: center;
  transition: background 0.2s ease;
}

.ajouter-btn:hover:not(:disabled) {
  background: #8c6da2;
  color: #fff;
}

/* Feedback form */
.success-msg {
  color: #28a745;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* Tableau produits */
.tableau-produits {
  flex: 2;
  min-width: 400px;
}

.tableau-produits h2 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.produit-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1.2rem;
  border-radius: 10px;
  background-color: #ffffffc8;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.produit-item input {
  width: 100%;
  margin-bottom: 0.6rem;
  padding: 0.4rem;
  font-size: 0.95rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.img-preview {
  display: flex;
  gap: 0.5rem;
  margin: 0.5rem 0;
  flex-wrap: wrap;
}

.img-preview img {
  width: 70px;
  height: 70px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.btn-droite {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.6rem;
}

.btn-droite button {
  background: #98babb;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.btn-droite button:hover {
  background-color: #8c6da2;
  color: white;
}



@media (max-width: 480px) {
  /* Container principal */
  .admin-page {
    padding: 1rem;
    max-width: 100%;
    box-sizing: border-box;
  }

  /* Titre */
  .titre-centre {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }

  /* Bouton Déconnexion */
  .logout-btn {
    display: block;
    margin: 2rem 1rem 2rem auto; /* 2rem haut/bas, 1rem gauche, auto à droite */
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  /* Filtres empilés */
  .filters {
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    width: 100%;
  }
  .filters label {
    font-size: 0.9rem;
  }
  .filters select,
  .filters input {
    width: 100%;
  }

  /* Passage en colonne pour le layout */
  .admin-layout {
    flex-direction: column;
    gap: 1rem;
  }

  /* Formulaire ajout */
  .formulaire-ajout {
  background-color: #fff;               /* même fond blanc */
  border: 1px solid #ddd;              /* même bordure grise claire */
  border-radius: 10px;                 /* mêmes coins arrondis */
  box-shadow: 0 2px 6px rgba(0,0,0,0.05); /* même ombre légère */
  padding: 1.5rem;                     /* généreux padding interne */
  margin-bottom: 1.5rem;               /* espace sous le bloc */
}

/* Facultatif : uniformiser le gap avec tes produit-items */
.formulaire-ajout label {
  margin-bottom: 1rem;
}
  .formulaire-ajout h2 {
    font-size: 1.2rem;
  }

  .formulaire-ajout input,
  .formulaire-ajout textarea,
  .formulaire-ajout select {
    width: calc(100% - 1rem) !important; 
    margin: 0.5rem auto;                 
    box-sizing: border-box;
  }
  .ajouter-btn {
    width: 100%;
    font-size: 0.95rem;
    padding: 0.6rem;
  }

  /* Tableau produits */
  .tableau-produits {
    width: 100% !important;
    min-width: auto !important;
    margin-top: 1rem;
  }
  .tableau-produits h2 {
    font-size: 1rem;
    margin-bottom: 0.8rem;
  }

  /* Items et inputs */
  .produit-item {
    padding: 0.8rem;
    margin-bottom: 1rem;
  }
  .produit-item input {
    width: 100%;
    font-size: 0.9rem;
    padding: 0.4rem;
    box-sizing: border-box;
  }

  /* Aperçu images plus petit */
  .img-preview img {
    width: 50px;
    height: 50px;
  }

  /* Boutons modifier/supprimer */
  .btn-droite {
    justify-content: flex-end;
  }
  .btn-droite button {
    font-size: 0.85rem;
    padding: 0.4rem 0.6rem;
  }
}


</style>
