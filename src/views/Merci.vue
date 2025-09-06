<template>
  <section class="merci">
    <div class="card">
      <div class="icon-wrap">
        <span v-if="isPaid" class="icon">✅</span>
        <span v-else-if="isPending" class="icon">⏳</span>
        <span v-else class="icon">ℹ️</span>
      </div>

      <h1 v-if="isPaid">Paiement reçu, merci !</h1>
      <h1 v-else-if="isPending">Paiement en cours de confirmation…</h1>
      <h1 v-else>Nous avons bien reçu votre retour</h1>

      <p class="ref" v-if="ref">
        Référence de votre commande :
        <strong>{{ ref }}</strong>
        <button class="linklike" @click="copyRef" :disabled="copied">
          {{ copied ? 'Copié ✔' : 'Copier' }}
        </button>
      </p>
      <p v-else class="muted">
        (Référence manquante dans l’URL)
      </p>

      <p class="status" v-if="loading">Vérification du statut…</p>
      <p class="status" v-else>
        Statut :
        <span :class="['badge', badgeClass]">{{ statusLabel }}</span>
      </p>

      <p class="tip" v-if="isPending">
        Vous venez de revenir depuis SumUp. Si l’écran reste en “en cours”, patientez quelques secondes puis
        <button class="linklike" @click="checkStatus">rafraîchissez le statut</button>.
      </p>

      <div class="actions">
        <button class="primary" @click="goHome">← Revenir à la boutique</button>
        <a
          class="secondary"
          :href="`mailto:contact@exemple.com?subject=Commande%20Arc%20En%20Ciel%20${encodeURIComponent(ref)}`"
        >
          Besoin d’aide ?
        </a>
      </div>

      <details class="details">
        <summary>Que se passe-t-il ensuite ?</summary>
        <ul>
          <li>Vous recevez un email récapitulatif (si configuré).</li>
          <li>La créatrice prépare votre commande.</li>
          <li>Vous serez notifié(e) lors de l’expédition.</li>
        </ul>
      </details>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Merci',
  data() {
    return {
      ref: this.$route.query.ref || '',
      status: 'UNKNOWN', // PENDING | PAID | FAILED | CANCELED | UNKNOWN
      loading: true,
      copied: false
    };
  },
  computed: {
    isPaid() {
      return this.status === 'PAID' || this.status === 'SUCCESSFUL' || this.status === 'SUCCESS';
    },
    isPending() {
      return this.status === 'PENDING';
    },
    badgeClass() {
      return this.isPaid ? 'ok' : (this.isPending ? 'pending' : 'neutral');
    },
    statusLabel() {
      if (this.isPaid) return 'Payé';
      if (this.isPending) return 'En cours';
      if (this.status === 'FAILED') return 'Échec';
      if (this.status === 'CANCELED') return 'Annulé';
      return 'Inconnu';
    }
  },
  methods: {
    async checkStatus() {
      if (!this.ref) { this.loading = false; return; }
      try {
        this.loading = true;
        const res = await fetch(`/api/orders/${encodeURIComponent(this.ref)}/status`, {
          headers: { 'Cache-Control': 'no-cache' }
        });
        if (res.ok) {
          const data = await res.json();
          this.status = data.status || 'UNKNOWN';
        } else {
          this.status = 'UNKNOWN';
        }
      } catch (_e) {
        this.status = 'UNKNOWN';
      } finally {
        this.loading = false;
        document.title = this.isPaid
          ? '✅ Paiement validé – Arc En Ciel'
          : 'Merci – Arc En Ciel';
      }
    },
    goHome() {
      this.$router.push('/');
    },
    async copyRef() {
      try {
        await navigator.clipboard.writeText(this.ref);
        this.copied = true;
        setTimeout(() => (this.copied = false), 1500);
      } catch (_) {}
    }
  },
  mounted() {
    document.title = 'Merci – Arc En Ciel';
    this.checkStatus();
  }
};
</script>

<style scoped>
/* ——— Police partout : Lucida ——— */
.merci, .merci * {
  font-family: "Lucida Sans", "Lucida Grande", "Lucida Sans Unicode",
               Geneva, Verdana, sans-serif;
}

/* ——— Layout ——— */
.merci {
  min-height: 70vh;
  display: grid;
  place-items: center;
  padding: 32px;
  background: #fafafa;
}

.card {
  width: min(880px, 96vw);
  background: #fff;
  border: 2px solid #e6e6e6;           /* cadre plus visible */
  border-radius: 22px;
  padding: 40px 32px;                   /* plus d’air */
  text-align: center;
  box-shadow: 0 12px 32px rgba(0,0,0,0.08);
}

/* ——— Typo XXL ——— */
.icon-wrap { font-size: 72px; line-height: 1; margin-bottom: 12px; }
h1 { margin: 12px 0 12px; font-size: 34px; font-weight: 700; }
.ref, .status, .tip, .details, .actions, .muted {
  font-size: 18px;                      /* texte plus grand */
  line-height: 1.6;
}
.ref { margin: 10px 0 16px; }
.status { margin: 8px 0 16px; }
.tip { margin: 10px 0 18px; opacity: .95; }

/* ——— Badges ——— */
.badge {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 1.1rem;
  border: 2px solid #ddd;
  font-weight: 700;
}
.badge.ok { background: #e9f8ef; border-color: #bfe8cd; }
.badge.pending { background: #fff4e5; border-color: #ffd7a1; }
.badge.neutral { background: #f3f5f7; border-color: #e6eaee; }

/* ——— Actions ——— */
.actions {
  margin-top: 22px;
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary {
  background: #e21583; color: #fff; border: 0; border-radius: 14px;
  padding: 14px 22px; cursor: pointer; font-size: 18px; font-weight: 700;
  transition: transform .06s ease, box-shadow .2s ease;
  box-shadow: 0 6px 14px rgba(226, 21, 131, .25);
}
.primary:disabled { opacity: .6; cursor: not-allowed; }
.primary:hover { transform: translateY(-1px); }

.secondary {
  text-decoration: none; border: 2px solid #ddd; border-radius: 14px;
  padding: 12px 20px; color: #333; font-weight: 700; font-size: 18px;
  background: #fff;
}

/* ——— Liens style bouton ——— */
.linklike {
  background: none; border: 0; color: #e21583; cursor: pointer; margin-left: 8px;
  font-weight: 700; text-decoration: underline; font-size: 18px;
}

/* ——— Détails ——— */
.details { margin-top: 16px; text-align: left; }
.details summary { cursor: pointer; font-weight: 700; margin-bottom: 8px; }
.details ul { margin: 8px 0 0 18px; }

/* ——— État ——— */
.muted { opacity: .75; }

/* ——— Responsive petit écran ——— */
@media (max-width: 420px) {
  .card { padding: 28px 20px; border-radius: 18px; }
  h1 { font-size: 28px; }
  .icon-wrap { font-size: 60px; }
  .ref, .status, .tip, .details, .actions, .muted,
  .primary, .secondary, .linklike { font-size: 17px; }
}
</style>
