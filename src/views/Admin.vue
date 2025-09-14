<template>
  <div class="admin-page">
    <!-- ===== Connexion ===== -->
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

    <!-- ===== Interface admin ===== -->
    <div v-else>
      <div class="admin-header">
        <h1 class="titre-centre">Gestion des produits 🛍️</h1>
        <div class="admin-header-buttons">
          <button @click="connectSumUp" class="connect-btn">Connecter SumUp</button>
          <button @click="seDeconnecter" class="logout-btn">Déconnexion</button>
        </div>
      </div>

      <!-- Filtres -->
      <div class="filters">
        <label>Filtrer par catégorie :
          <select v-model="filtreCategorie">
            <option value="">Toutes</option>
            <option v-for="cat in categoriesDisponibles" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </label>

        <label>Recherche :
          <input type="text" v-model="rechercheTexte" placeholder="Nom ou description" />
        </label>
      </div>

      <div class="admin-layout">
        <!-- ===== Formulaire ajout ===== -->
        <form @submit.prevent="ajouterProduit" class="formulaire-ajout" novalidate>
          <h2>Ajouter un produit 🛒</h2>

          <label>Nom :
            <input type="text" v-model="nouveauProduit.nom" :class="{ 'input-error': errors.nom }" required />
            <span v-if="errors.nom" class="error-msg">{{ errors.nom }}</span>
          </label>

          <label>Description :
            <textarea v-model="nouveauProduit.description" :class="{ 'input-error': errors.description }" required></textarea>
            <span v-if="errors.description" class="error-msg">{{ errors.description }}</span>
          </label>

          <label>Prix (€) :
            <input type="number" v-model.number="nouveauProduit.prix" :class="{ 'input-error': errors.prix }" min="0.01" step="0.01" required />
            <span v-if="errors.prix" class="error-msg">{{ errors.prix }}</span>
          </label>

          <!-- Couleurs (CSV) -->
          <label>Couleurs (séparées par des virgules) :
            <input type="text" v-model="nouveauProduit.couleurs" placeholder="ex: beige, bleu, noir" />
          </label>

          <label>Catégorie :
            <select v-model="categorieChoisie" :class="{ 'input-error': errors.categorie }" required>
              <option disabled value="">-- Choisir une catégorie --</option>
              <option v-for="cat in categoriesDisponibles" :key="cat" :value="cat">
                {{ cat }}
              </option>
              <option value="autre">Autre (à préciser)</option>
            </select>
            <span v-if="errors.categorie" class="error-msg">{{ errors.categorie }}</span>
          </label>

          <label v-if="categorieChoisie === 'autre'">Nouvelle catégorie :
            <input type="text" v-model="nouvelleCategorie" :class="{ 'input-error': errors.nouvelleCategorie }" placeholder="ex: pendules" required />
            <span v-if="errors.nouvelleCategorie" class="error-msg">{{ errors.nouvelleCategorie }}</span>
          </label>

          <label v-for="(file, index) in fichiersImages" :key="index">
            Image {{ index + 1 }} :
            <input type="file" :ref="'fichierImage' + index" @change="onFileChange($event, index)" accept="image/*" />
          </label>

          <button type="submit" class="ajouter-btn" :disabled="isLoading">
            <span v-if="isLoading">⏳ Ajout en cours...</span>
            <span v-else>Ajouter le produit</span>
          </button>

          <p v-if="formMessage" :class="{'error-msg': formError, 'success-msg': !formError}">
            {{ formMessage }}
          </p>
        </form>

        <!-- ===== Tableau produits ===== -->
        <div class="tableau-produits" v-if="produitsFiltres.length">
          <h2>📦 Produits filtrés ({{ produitsFiltres.length }})</h2>

          <div v-for="produit in produitsFiltres" :key="produit._id || produit.id" class="produit-item">
            <input v-model="produit.nom" />
            <input v-model="produit.description" />
            <input type="number" v-model.number="produit.prix" />
            <input v-model="produit.categorie" />

            <!-- Édition couleurs -->
            <input
              :value="toCSV(produit.couleurs)"
              @input="onCouleursInput(produit, $event.target.value)"
              placeholder="couleurs: beige, bleu"
            />

            <div class="color-badges" v-if="toCSV(produit.couleurs)">
              <span
                v-for="(c,i) in toCSV(produit.couleurs).split(',')"
                :key="i"
                class="color-chip"
                :title="c.trim()"
              >{{ c.trim() }}</span>
            </div>

            <div class="img-preview" v-if="produit.images?.length">
              <img v-for="(img, i) in produit.images" :key="i" :src="img" alt="Image produit" />
            </div>

            <div class="btn-droite">
              <button @click="modifierProduit(produit)">💾 Modifier</button>
              <button @click="supprimerProduit(produit._id || produit.id)">🗑 Supprimer</button>
            </div>
          </div>
        </div>
      </div> <!-- /admin-layout -->
    </div> <!-- /v-else -->
  </div>
</template>

<script>
import { api } from '@/utils/api'

const INACTIVITY_MIN = 30 // minutes

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

      // Produits
      produits: [],
      filtreCategorie: '',
      rechercheTexte: '',

      // Ajout produit
      nouveauProduit: { nom: '', description: '', prix: null, couleurs: '' },
      categorieChoisie: '',
      nouvelleCategorie: '',
      fichiersImages: [null, null, null, null, null],
      errors: {},
      formMessage: '',
      formError: false,

      categoriesFixes: [
        'hauts','collier','bracelet','chapelet',
        'boucles doreilles','bijoux de cheville',
        'malas','parures','portecles','cartesdiv','pendule'
      ],

      // Inactivité
      _idleTimer: null,
    }
  },
  computed: {
    categoriesDisponibles() {
      const dyn = [...new Set(this.produits.map(p => p.categorie?.toLowerCase()))].filter(Boolean)
      return dyn.length ? dyn : this.categoriesFixes
    },
    produitsFiltres() {
      const txt = this.rechercheTexte.toLowerCase()
      return this.produits.filter(p =>
        (!this.filtreCategorie || p.categorie?.toLowerCase() === this.filtreCategorie.toLowerCase()) &&
        (p.nom.toLowerCase().includes(txt) || p.description.toLowerCase().includes(txt))
      )
    }
  },
  async mounted() {
    const token = sessionStorage.getItem('admin_token')
    if (token) {
      this.isLoggedIn = true
      await this.chargerProduits()
      this._startIdleWatch()
    }
    window.addEventListener('mousemove', this._resetIdleWatch)
    window.addEventListener('keydown', this._resetIdleWatch)
    window.addEventListener('click', this._resetIdleWatch)
    window.addEventListener('scroll', this._resetIdleWatch)
  },
  beforeUnmount() {
    this._clearIdleWatch()
    window.removeEventListener('mousemove', this._resetIdleWatch)
    window.removeEventListener('keydown', this._resetIdleWatch)
    window.removeEventListener('click', this._resetIdleWatch)
    window.removeEventListener('scroll', this._resetIdleWatch)
  },
  methods: {
    /* ===== Helpers couleurs ===== */
    toCSV(val) {
      if (!val) return ''
      if (Array.isArray(val)) return val.join(', ')
      return String(val)
    },
    csvToArray(csv) {
      if (!csv) return []
      return csv.split(',').map(s => s.trim()).filter(Boolean)
    },
    onCouleursInput(produit, csv) {
      produit.couleurs = this.csvToArray(csv)
    },

    /* ===== Auth ===== */
    async seConnecter() {
      this.loginError = ''
      this.isLoading = true
      try {
        const { token } = await api('/api/login', {
          method: 'POST',
          body: JSON.stringify({ username: this.loginUser, password: this.loginPass })
        })
        sessionStorage.setItem('admin_token', token)
        this.isLoggedIn = true
        await this.chargerProduits()
        this._startIdleWatch()
      } catch (err) {
        this.loginError = err.message || 'Erreur serveur, réessayez plus tard'
      } finally {
        this.isLoading = false
      }
    },
    seDeconnecter() {
      sessionStorage.removeItem('admin_token')
      this.isLoggedIn = false
      this.loginUser = ''
      this.loginPass = ''
      this.produits = []
      this._clearIdleWatch()
    },

    /* ===== SumUp ===== */
    connectSumUp() {
      const base = import.meta.env.VITE_BACKEND_URL || ''
      window.location.href = base + '/auth/connect'
    },

    /* ===== Fichiers ===== */
    onFileChange(event, index) {
      this.fichiersImages[index] = event.target.files[0]
    },

    /* ===== Produits CRUD ===== */
    async chargerProduits() {
      try {
        this.produits = await api('/api/produits', {
          headers: { Authorization: 'Bearer ' + sessionStorage.getItem('admin_token') }
        })
      } catch (err) {
        if ((err.message || '').includes('401') || (err.message || '').includes('403')) {
          this.seDeconnecter()
        } else {
          this.formMessage = '❌ Erreur de chargement produits'
          this.formError = true
        }
      }
    },

    validateForm() {
      this.errors = {}
      if (!this.nouveauProduit.nom) this.errors.nom = 'Le nom est requis'
      if (!this.nouveauProduit.description) this.errors.description = 'La description est requise'
      if (!this.nouveauProduit.prix || this.nouveauProduit.prix <= 0) this.errors.prix = 'Le prix doit être > 0'
      if (!this.categorieChoisie) this.errors.categorie = 'La catégorie est requise'
      if (this.categorieChoisie === 'autre' && !this.nouvelleCategorie) this.errors.nouvelleCategorie = 'Veuillez préciser la catégorie'
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
          ? (this.nouvelleCategorie || '').toLowerCase()
          : (this.categorieChoisie || '').toLowerCase()

        formData.append('nom', this.nouveauProduit.nom)
        formData.append('description', this.nouveauProduit.description)
        formData.append('prix', this.nouveauProduit.prix)
        formData.append('categorie', catFinale)
        formData.append('couleurs', (this.nouveauProduit.couleurs || '').trim())
        this.fichiersImages.forEach(f => f && formData.append('images', f))

        const data = await api('/api/produits', {
          method: 'POST',
          headers: { Authorization: 'Bearer ' + sessionStorage.getItem('admin_token') },
          body: formData
        })
        this.produits.push(data)
        this.formMessage = '✅ Produit ajouté !'
        this.formError = false
        this.resetFormulaire()
      } catch {
        this.formMessage = '❌ Erreur ajout produit'
        this.formError = true
      } finally {
        this.isLoading = false
      }
    },

    resetFormulaire() {
      this.nouveauProduit = { nom: '', description: '', prix: null, couleurs: '' }
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

    async modifierProduit(produit) {
      const id = produit._id || produit.id
      const payload = {
        ...produit,
        couleurs: Array.isArray(produit.couleurs) ? produit.couleurs : this.csvToArray(produit.couleurs)
      }
      try {
        const updated = await api(`/api/produits/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + sessionStorage.getItem('admin_token')
          },
          body: JSON.stringify(payload)
        })
        const idx = this.produits.findIndex(p => (p._id || p.id) === id)
        if (idx !== -1) this.$set ? this.$set(this.produits, idx, updated) : (this.produits[idx] = updated)
        this.formMessage = '✔ Produit modifié !'
        this.formError = false
      } catch {
        this.formMessage = '❌ Erreur modification'
        this.formError = true
      }
    },

    async supprimerProduit(id) {
      if (!confirm('❓ Supprimer ce produit ?')) return
      try {
        await api(`/api/produits/${id}`, {
          method: 'DELETE',
          headers: { Authorization: 'Bearer ' + sessionStorage.getItem('admin_token') }
        })
        this.produits = this.produits.filter(p => (p._id || p.id) !== id)
      } catch {
        alert('❌ Erreur suppression')
      }
    },

    /* ===== Inactivité ===== */
    _startIdleWatch() {
      this._clearIdleWatch()
      this._idleTimer = setTimeout(() => {
        this.seDeconnecter()
        alert('Session expirée pour inactivité.')
      }, INACTIVITY_MIN * 60 * 1000)
    },
    _resetIdleWatch() {
      if (!this.isLoggedIn) return
      this._startIdleWatch()
    },
    _clearIdleWatch() {
      if (this._idleTimer) {
        clearTimeout(this._idleTimer)
        this._idleTimer = null
      }
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 1.5rem;
  font-family: 'Raleway', sans-serif;
  background: #f1dad7;
  min-height: 100vh;
  box-sizing: border-box;
}

/* Header */
.titre-centre { font-size: 1.8rem; margin: 1.5rem 0 !important; }
.admin-header {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; margin-bottom: 1rem;
}
.admin-header-buttons { display: flex; gap: 0.6rem; }
.connect-btn, .logout-btn {
  padding: 0.5rem 0.8rem; font-size: 0.9rem; border: none; border-radius: 6px;
  font-weight: 600; cursor: pointer;
}
.connect-btn { background: #007bff; color: #fff; }
.connect-btn:hover { background: #0056b3; }
.logout-btn { background: #e20e0e; color: #fff; }
.logout-btn:hover { background: #9b0404; }

/* Login */
.login-form {
  max-width: 320px; margin: 2rem auto; padding: 1rem; background: #fafafae0;
  border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;
}
.login-form h1 { text-align: center; margin-bottom: 1rem; font-size: 1.5rem; }
.login-form label { display: block; margin-bottom: 0.8rem; font-weight: 600; }
.login-form input {
  width: 100%; padding: 0.3rem 0.5rem; margin-top: 0.2rem;
  border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;
}
.login-form button {
  width: 100%; padding: 0.5rem; margin-top: 1rem; background: #98babb;
  border-radius: 6px; font-weight: bold; cursor: pointer; border: none;
}
.login-form button:hover:not(:disabled) { background: #8c6da2; color: #fff; }
.error-msg { color: #d9534f; margin-top: 0.5rem; font-size: 0.85rem; }
.success-msg { color: #0a7a46; margin-top: 0.5rem; font-weight: 600; }

/* Filtres */
.filters { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filters label { flex: 1; min-width: 140px; font-weight: bold; }
.filters select, .filters input {
  width: 100%; padding: 0.3rem; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box;
}

/* Layout */
.admin-layout { display: flex; gap: 1rem; flex-wrap: wrap; }
.formulaire-ajout, .tableau-produits { flex: 1 1 320px; box-sizing: border-box; }

/* Formulaire ajout */
.formulaire-ajout {
  background: #fff; border: 1px solid #ddd; border-radius: 8px;
  padding: 1rem; margin-bottom: 1rem;
}
.formulaire-ajout h2 { font-size: 1.2rem; margin-bottom: 1rem; }
.formulaire-ajout label { display: block; margin-bottom: 0.8rem; font-weight: 600; }
.formulaire-ajout input, .formulaire-ajout textarea, .formulaire-ajout select {
  width: 100%; padding: 0.4rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
}
.input-error { border-color: #d9534f; }
.ajouter-btn {
  width: 100%; padding: 0.5rem; background: #98babb; border: none;
  border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 1rem;
}
.ajouter-btn:hover:not(:disabled) { background: #8c6da2; color: #fff; }

/* Tableau produits */
.tableau-produits h2 { font-size: 1.1rem; margin-bottom: 0.8rem; }
.produit-item {
  background: #fff; border: 1px solid #ddd; border-radius: 8px;
  padding: 0.8rem; margin-bottom: 1rem; box-sizing: border-box;
}
.produit-item input {
  width: 100%; padding: 0.3rem; margin-bottom: 0.6rem;
  border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
}

/* Badges couleurs */
.color-badges { display: flex; flex-wrap: wrap; gap: .3rem; margin: .2rem 0 .6rem; }
.color-chip { background: #f1dad7; border-radius: 999px; padding: .15rem .5rem; font-size: .8rem; }

/* Images */
.img-preview { display: flex; gap: 0.4rem; margin: 0.5rem 0; flex-wrap: wrap; }
.img-preview img {
  width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;
}

/* Boutons ligne */
.btn-droite { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-droite button {
  flex: 1 1 auto; padding: 0.4rem; border-radius: 4px; border: none;
  cursor: pointer; font-weight: bold;
}
.btn-droite button:hover { background: #8c6da2; color: #fff; }

/* Responsive */
@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .admin-layout { flex-direction: column; }
  .formulaire-ajout, .tableau-produits { flex: 1 1 100%; }
  .titre-centre { margin: 1.5rem 0 !important; }
}
</style>
