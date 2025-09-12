<template>
  <div class="contact-page">
    <div class="contact-header">
      <h1>Contactez-nous</h1>
      <p>Une question ? Besoin d'aide sur une commande ? <span class="break-mobile">Écrivez-nous ❤️</span></p>
    </div>

    <div class="contact-form">
      <form @submit.prevent="envoyerMessage" novalidate>
        <div class="form-group">
          <label for="nom">Nom</label>
          <input
            type="text"
            id="nom"
            v-model.trim="form.nom"
            :class="{ invalid: errors.nom }"
            required
          />
          <span v-if="errors.nom" class="error-msg">{{ errors.nom }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model.trim="form.email"
            :class="{ invalid: errors.email }"
            required
          />
          <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="message">Message</label>
          <textarea
            id="message"
            v-model.trim="form.message"
            :class="{ invalid: errors.message }"
            required
            rows="5"
          ></textarea>
          <span v-if="errors.message" class="error-msg">{{ errors.message }}</span>
        </div>

        <button type="submit" :disabled="sending">
          {{ sending ? 'Envoi en cours...' : 'Envoyer' }}
        </button>
      </form>

      <!-- Message toast -->
      <div v-if="toastMessage" :class="['toast', toastSuccess ? 'success' : 'error']">
        {{ toastMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/utils/api'

export default {
  name: 'Contact',
  data() {
    return {
      form: {
        nom: '',
        email: '',
        message: ''
      },
      errors: {},
      sending: false,
      toastMessage: '',
      toastSuccess: false,
    }
  },
  methods: {
    validateForm() {
      this.errors = {}

      const nom = (this.form.nom || '').trim()
      const email = (this.form.email || '').trim()
      const message = (this.form.message || '').trim()

      if (!nom) {
        this.errors.nom = 'Le nom est obligatoire.'
      }
      if (!email) {
        this.errors.email = 'L’email est obligatoire.'
      } else if (!this.isValidEmail(email)) {
        this.errors.email = 'Format d’email invalide.'
      }
      if (!message) {
        this.errors.message = 'Le message est obligatoire.'
      } else if (message.length < 10) {
        this.errors.message = 'Le message doit contenir au moins 10 caractères.'
      }

      return Object.keys(this.errors).length === 0
    },
    isValidEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    async envoyerMessage() {
      if (this.sending) return
      if (!this.validateForm()) return

      this.sending = true
      this.toastMessage = ''

      try {
        const payload = {
          nom: this.form.nom.trim(),
          email: this.form.email.trim(),
          message: this.form.message.trim(),
        }

        const { success, message } = await api('/api/send-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })

        if (success) {
          this.toastMessage = '✅ Message envoyé avec succès !'
          this.toastSuccess = true
          this.form.nom = ''
          this.form.email = ''
          this.form.message = ''
        } else {
          this.toastMessage = message || 'Erreur inconnue lors de l’envoi.'
          this.toastSuccess = false
        }
      } catch (err) {
        console.error(err)
        this.toastMessage = 'Impossible d’envoyer le message. Réessayez plus tard.'
        this.toastSuccess = false
      } finally {
        this.sending = false
        setTimeout(() => { this.toastMessage = '' }, 4000)
      }
    }
  }
}
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
  transition: border-color 0.3s ease;
}

form input.invalid,
form textarea.invalid {
  border-color: #e20e7f;
}

.error-msg {
  color: #e20e7f;
  font-size: 0.85rem;
  margin-top: 0.3rem;
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

form button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

form button:hover:enabled {
  background-color: #e20e7f;
  color: #fff;
}

/* Toast message */
.toast {
  margin-top: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  text-align: center;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  user-select: none;
  transition: opacity 0.3s ease;
}

.toast.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.toast.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* ================= */
/* Styles MOBILE ONLY */
/* ================= */

@media (max-width: 768px) {
  .contact-page {
    padding-top: clamp(2rem, 5vw, 3rem);
  }

  .contact-header {
    margin-top: clamp(1rem, 4vw, 2rem);
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
