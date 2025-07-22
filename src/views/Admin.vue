<template>
  <div class="admin-page">
    <h1 class="titre-centre">Gestion des produits</h1>

    <!-- Filtres -->
    <div class="filters">
      <label>Filtrer par catégorie :
        <select v-model="filtreCategorie">
          <option value="">Toutes</option>
          <option v-for="cat in categoriesDisponibles" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </label>

      <label>Recherche :
        <input type="text" v-model="rechercheTexte" placeholder="Nom ou description" />
      </label>
    </div>

    <div class="admin-layout">
      <!-- FORMULAIRE -->
      <form @submit.prevent="ajouterProduit" class="formulaire-ajout">
        <h2>➕ Ajouter un produit</h2>

        <label>Nom :
          <input type="text" v-model="nouveauProduit.nom" required />
        </label>

        <label>Description :
          <textarea v-model="nouveauProduit.description" required></textarea>
        </label>

        <label>Prix (€) :
          <input type="number" v-model.number="nouveauProduit.prix" required />
        </label>

        <label>Catégorie :
          <select v-model="categorieChoisie" required>
            <option disabled value="">-- Choisir une catégorie --</option>
            <option v-for="cat in categoriesDisponibles" :key="cat" :value="cat">{{ cat }}</option>
            <option value="autre">Autre (à préciser)</option>
          </select>
        </label>

        <label v-if="categorieChoisie === 'autre'">Nouvelle catégorie :
          <input type="text" v-model="nouvelleCategorie" placeholder="ex: pendules" required />
        </label>

        <label v-for="(file, index) in fichiersImages" :key="index">
          Image {{ index + 1 }} :
          <input
            type="file"
            :ref="'fichierImage' + index"
            @change="onFileChange($event, index)"
            accept="image/*"
          />
        </label>

        <button type="submit" class="ajouter-btn">Ajouter le produit</button>
      </form>

      <!-- TABLEAU -->
      <div class="tableau-produits" v-if="produitsFiltres.length">
        <h2>📦 Produits filtrés ({{ produitsFiltres.length }})</h2>
        <div v-for="produit in produitsFiltres" :key="produit._id || produit.id" class="produit-item">
          <input v-model="produit.nom" />
          <input v-model="produit.description" />
          <input type="number" v-model.number="produit.prix" />
          <input v-model="produit.categorie" />

          <div class="img-preview" v-if="produit.images?.length">
            <img
              v-for="(img, i) in produit.images"
              :key="i"
              :src="img.startsWith('http') ? img : 'http://localhost:3001' + img"
              alt="Image produit"
            />
          </div>

          <div class="btn-droite">
            <button @click="modifierProduit(produit)">💾 Modifier</button>
            <button @click="supprimerProduit(produit._id || produit.id)">🗑 Supprimer</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Admin',
  data() {
    return {
      nouveauProduit: { nom: '', description: '', prix: null },
      categorieChoisie: '',
      nouvelleCategorie: '',
      fichiersImages: [null, null, null, null, null],
      produits: [],
      filtreCategorie: '',
      rechercheTexte: '',
      categoriesFixes: [
        'bague', 'collier', 'bracelet', 'chapelet', 'boucles doreilles',
        'bijoux de cheville', 'malas', 'parures', 'portecles', 'cartesdiv', 'pendule'
      ]
    };
  },
  computed: {
    produitsFiltres() {
      return this.produits.filter(p => {
        const matchCat = !this.filtreCategorie || p.categorie?.toLowerCase() === this.filtreCategorie.toLowerCase();
        const texte = this.rechercheTexte.toLowerCase();
        return p.nom.toLowerCase().includes(texte) || p.description.toLowerCase().includes(texte);
      });
    },
    categoriesDisponibles() {
      const dynCats = [...new Set(this.produits.map(p => p.categorie?.toLowerCase()))].filter(Boolean);
      return dynCats.length ? dynCats : this.categoriesFixes;
    }
  },
  mounted() {
    this.chargerProduits();
  },
  methods: {
    onFileChange(event, index) {
      this.fichiersImages[index] = event.target.files[0];
    },
    async chargerProduits() {
      try {
        const res = await fetch('http://localhost:3001/produits');
        this.produits = await res.json();
      } catch (err) {
        console.error('❌ Erreur chargement produits :', err);
      }
    },
    async ajouterProduit() {
      const formData = new FormData();
      const categorieFinale = this.categorieChoisie === 'autre'
        ? this.nouvelleCategorie.toLowerCase()
        : this.categorieChoisie.toLowerCase();

      formData.append('nom', this.nouveauProduit.nom);
      formData.append('description', this.nouveauProduit.description);
      formData.append('prix', this.nouveauProduit.prix);
      formData.append('categorie', categorieFinale);

      this.fichiersImages.forEach(file => {
        if (file) formData.append('images', file);
      });

      try {
        const res = await fetch('http://localhost:3001/produits', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          this.produits.push(data.produit);
          alert('✅ Produit ajouté !');
          this.resetFormulaire();
        } else {
          throw new Error(data.message || 'Erreur inconnue');
        }
      } catch (err) {
        alert('❌ Erreur ajout produit');
        console.error(err);
      }
    },
    resetFormulaire() {
      this.nouveauProduit = { nom: '', description: '', prix: null };
      this.categorieChoisie = '';
      this.nouvelleCategorie = '';
      this.fichiersImages = [null, null, null, null, null];

      for (let i = 0; i < 5; i++) {
        const ref = this.$refs['fichierImage' + i];
        if (ref && ref.length) ref[0].value = '';
      }
    },
    async supprimerProduit(id) {
      if (!confirm('❓ Supprimer ce produit ?')) return;
      try {
        const res = await fetch(`http://localhost:3001/produits/${id}`, { method: 'DELETE' });
        if (res.ok) {
          this.produits = this.produits.filter(p => (p._id || p.id) !== id);
        }
      } catch (err) {
        alert('❌ Erreur suppression');
        console.error(err);
      }
    },
    async modifierProduit(produit) {
      const id = produit._id || produit.id;
      try {
        const res = await fetch(`http://localhost:3001/produits/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(produit)
        });
        if (res.ok) {
          alert('✔ Produit modifié !');
        }
      } catch (err) {
        alert('❌ Erreur modification');
        console.error(err);
      }
    }
  }
};
</script>



<style scoped>
.admin-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background: #fff;
  max-width: 1300px;
  margin: auto;
}

.titre-centre {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
}

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

.filters input,
.filters select {
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

.admin-layout {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.formulaire-ajout {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 1.5rem;
  background: #fafafa;
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

.ajouter-btn:hover {
  background-color: #8c6da2;
  color: white;
}

.tableau-produits {
  flex: 2;
  min-width: 400px;
}

.produit-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1.2rem;
  border-radius: 10px;
  background-color: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.produit-item input {
  width: 100%;
  margin-bottom: 0.4rem;
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
</style>

