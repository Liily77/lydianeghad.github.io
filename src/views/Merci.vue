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
        Statut : <span :class="['badge', badgeClass]">{{ statusLabel }}</span>
      </p>

      <p class="tip" v-if="isPending">
        Vous venez de revenir depuis SumUp. Si l’écran reste en “en cours”, patientez quelques secondes puis
        <button class="linklike" @click="checkStatus">rafraîchissez le statut</button>.
      </p>

      <div class="actions">
        <button class="primary" @click="goHome">← Revenir à la boutique</button>
        <a class="secondary" href="mailto:contact@exemple.com?subject=Commande%20Arc%20En%20Ciel%20{{ref}}">
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
      // Ton backend renvoie "PAID" (ou met à jour via /merci POST ping).
      // On accepte aussi SUCCESSFUL par prudence.
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
    // Juste une vérification ponctuelle (pas de polling en Mode B)
    this.checkStatus();
  }
};
</script>

<style scoped>
.merci {
  min-height: 60vh;
  display: grid;
  place-items: center;
  padding: 24px;
}
.card {
  width: min(720px, 92vw);
  background: #fff;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}
.icon-wrap { font-size: 44px; }
h1 { margin: 10px 0 6px; font-size: 22px; }
.ref { margin: 6px 0 10px; }
.status { margin: 6px 0 10px; }
.tip { margin: 8px 0 14px; opacity: 0.9; }
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.9rem;
  border: 1px solid #ddd;
}
.badge.ok { background: #e9f8ef; border-color: #bfe8cd; }
.badge.pending { background: #fff4e5; border-color: #ffe0b2; }
.badge.neutral { background: #f3f5f7; border-color: #e6eaee; }
.actions {
  margin-top: 16px;
  display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;
}
.primary {
  background: #e21583b6; color: #fff; border: 0; border-radius: 10px;
  padding: 10px 16px; cursor: pointer;
}
.primary:hover { background: #e20e7f; }
.secondary {
  text-decoration: none; border: 1px solid #ddd; border-radius: 10px;
  padding: 10px 16px; color: #333;
}
.linklike {
  background: none; border: 0; color: #e20e7f; cursor: pointer; margin-left: 6px;
}
.details { margin-top: 10px; text-align: left; }
.muted { opacity: .75; }
</style>
