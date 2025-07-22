<template>
  <div class="contact-page">
    <div class="contact-header">
      <h1>Contactez-nous</h1>
      <p>Une question ? Besoin d'aide sur une commande ? Écrivez-nous ! ❤️</p>
    </div>

    <div class="contact-form">
      <form @submit.prevent="envoyerMessage">
        <div class="form-group">
          <label for="nom">Nom</label>
          <input type="text" id="nom" v-model="form.nom" required />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="form.email" required />
        </div>

        <div class="form-group">
          <label for="message">Message</label>
          <textarea id="message" v-model="form.message" required></textarea>
        </div>

        <button type="submit">Envoyer</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Contact',
  data() {
    return {
      form: {
        nom: '',
        email: '',
        message: ''
      }
    };
  },
  methods: {
    async envoyerMessage() {
      try {
        const res = await fetch('/send-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });
        const { success, message } = await res.json();
        if (success) {
          alert('✅ Message envoyé avec succès !');
          this.form.nom = '';
          this.form.email = '';
          this.form.message = '';
        } else {
          throw new Error(message || 'Erreur inconnue');
        }
      } catch (err) {
        console.error(err);
        alert('❌ Impossible d’envoyer le message. Réessayez plus tard.');
      }
    }
  }
};
</script>


<style scoped>
.contact-page {
  font-family: 'Raleway', sans-serif;
  background-color: #f9f4f0;
  min-height: 100vh;
  padding-top: 2rem; /* ✅ espace avec la navbar */
}

.contact-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.contact-header h1 {
  font-size: 2.3rem;
  color: #a074ae;
  margin-bottom: 0.6rem;
}

.contact-header p {
  color: #444;
  font-size: 1.1rem;
}

.contact-form {
  background-color: #fff; /* ✅ fond blanc comme la navbar */
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  width: 70%;
  margin: 0 auto 4rem auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

form {
  display: flex;
  flex-direction: column;
}

form label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  color: #222;
}

form input,
form textarea {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ccc;
  border-radius: 10px;
  font-size: 1rem;
  font-family: 'Raleway', sans-serif;
  background-color: #fdfdfd;
}

form textarea {
  min-height: 150px;
  resize: vertical;
}

form button {
  align-self: flex-end; /* ✅ Bouton reste à droite, mais dans le flux normal */
  background-color: #edc6c1;
  color: #000;
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1.5rem;
  transition: background-color 0.2s ease, color 0.2s ease;
}

form button:hover {
  background-color: #e20e7f;
  color: #fff;
}
</style>
