<template>
  <div class="merci-page">
    <div class="card">
      <h1>🙏 Merci pour votre commande !</h1>
      <p>Nous avons bien reçu votre paiement.</p>
      <p>
        Référence commande : 
        <span class="ref">{{ ref }}</span>
      </p>
      <router-link class="btn" to="/">Retour à la boutique</router-link>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const ref = route.query.ref || 'inconnue'
</script>

<style scoped>
.merci-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
.card {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 6px 24px rgba(0,0,0,.08);
}
h1 {
  margin-bottom: 1rem;
}
.ref {
  font-family: monospace;
  background: #f2f2f2;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}
.btn {
  display: inline-block;
  margin-top: 1.25rem;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  text-decoration: none;
  background: #222;
  color: #fff;
}
</style>
