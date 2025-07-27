<template>
  <div class="contact-page">
    <div class="contact-header">
      <h1>Contactez-nous</h1>
      <p>Une question ? Besoin d'aide sur une commande ? <span class="break-mobile">Écrivez-nous ❤️</span></p>
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
  padding-top: 2rem; 
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
  background-color: #fff; 
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
  align-self: flex-end; 
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

/* ================= */
/* Styles MOBILE ONLY */
/* ================= */


/* ================= */
/* Styles MOBILE ONLY */
/* ================= */

@media (max-width: 768px) {

  .contact-page {
    padding-top: clamp(2rem, 5vw, 3rem); /* ✅ plus d’espace avec la navbar */
  }

  .contact-header {
    margin-top: clamp(1rem, 4vw, 2rem);  /* ✅ ajoute un espace supplémentaire */
    margin-bottom: clamp(1.2rem, 3.5vw, 2rem);
    padding: 0 clamp(0.5rem, 3vw, 1rem);
  }

  .contact-header h1 {
    font-size: clamp(1.2rem, 4.5vw, 1.6rem);
    margin-bottom: clamp(0.3rem, 1.5vw, 0.5rem);
  }

  .contact-header p {
    font-size: clamp(0.75rem, 2vw, 0.9rem);
  }

  .break-mobile {
    display: block;
    margin-top: 0.3rem;
  }

  .contact-form {
    width: 85%; 
    padding: clamp(0.8rem, 3vw, 1.5rem);
    margin: 0 auto clamp(1.5rem, 5vw, 2.5rem);
    border-radius: clamp(8px, 2vw, 12px);
  }

  .form-group {
    margin-bottom: clamp(0.6rem, 2.5vw, 1rem);
  }

  form label {
    font-size: clamp(0.7rem, 1.7vw, 0.85rem);
    margin-bottom: clamp(0.2rem, 1vw, 0.4rem);
  }

  form input,
  form textarea {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    font-size: clamp(0.7rem, 1.9vw, 0.85rem);
    padding: clamp(0.5rem, 2vw, 0.7rem);
    border-radius: clamp(5px, 1.5vw, 8px);
  }

  form textarea {
    min-height: clamp(80px, 20vh, 120px);
  }

  form button {
    font-size: clamp(0.7rem, 1.7vw, 0.85rem);
    padding: clamp(0.4rem, 2vw, 0.6rem) clamp(0.8rem, 3vw, 1.2rem);
    border-radius: clamp(5px, 1.5vw, 8px);
    margin-top: clamp(0.8rem, 2.5vw, 1.2rem);
    font-weight: 700;
  }
}
</style>
