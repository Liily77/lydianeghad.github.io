<template>
  <div class="admin-page">
    <!-- Login -->
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

    <!-- Admin UI -->
    <div v-else>
      <!-- Header: titre + boutons -->
      <div class="admin-header">
        <h1 class="titre-centre">Gestion des produits 🛍️</h1>
        <div class="admin-header-buttons">
          <button @click="connectSumUp" class="connect-btn">Connecter SumUp</button>
          <button @click="seDeconnecter" class="logout-btn">Déconnexion</button>
        </div>
      </div>

      <!-- ... le reste de ton template reste inchangé ... -->
    </div>
  </div>
</template>

<script>
// ton script inchangé
</script>

<style scoped>
/* ===== Container ===== */
.admin-page {
  padding: 2rem;
  font-family: 'Raleway', sans-serif;
  background: #f1dad7;
  min-height: 100vh;
}

/* ===== Login ===== */
.login-form {
  max-width: 360px;
  margin: 3rem auto;
  padding: 1.5rem;
  background: #fafafae0;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.login-form h1 {
  text-align: center;
  margin-bottom: 1.5rem;
}
.login-form label {
  display: block;
  margin-bottom: 1rem;
  font-weight: 600;
}
.login-form input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  margin-top: 0.3rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.login-form button {
  width: 100%;
  padding: 0.6rem;
  margin-top: 1rem;
  background: #98babb;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.login-form button:hover:not(:disabled) {
  background: #8c6da2;
  color: #fff;
}
.error-msg {
  color: #d9534f;
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

/* ===== Header ===== */
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.titre-centre {
  font-size: 2rem;
  margin: 0;
}
.admin-header-buttons {
  display: flex;
  gap: 0.8rem;
}
.connect-btn,
.logout-btn {
  padding: 0.6rem 0.9rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.connect-btn {
  background: #007bff;
  color: #fff;
}
.connect-btn:hover {
  background: #0056b3;
}
.logout-btn {
  background: #e20e0e;
  color: #fff;
}
.logout-btn:hover {
  background: #9b0404;
}

/* ===== Media Queries Mobile ===== */
@media (max-width: 480px) {
  /* Centre le login haut de page */
  .admin-page {
    padding: 0;
  }
  .login-form {
    margin: 2rem auto !important;
  }

  /* Empile header */
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .admin-header-buttons {
    flex-direction: column;
    width: 100%;
    margin: 1rem 0;
  }
  .connect-btn,
  .logout-btn {
    width: 100%;
  }

  /* Espace autour du titre */
  .titre-centre {
    font-size: 1.5rem;
    margin: 1.5rem 0;
    width: 100%;
  }
}
</style>
