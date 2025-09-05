<template>
  <section class="attente">
    <h1>Redirection vers SumUp…</h1>
    <p v-if="error" class="err">{{ error }}</p>
    <p v-else-if="isPending">⏳ Paiement en cours… vérification toutes les 3 secondes.</p>
    <p v-else-if="isPaid">✅ Paiement validé, redirection…</p>
    <p v-else>Statut : {{ status }}</p>

    <button v-if="checkoutUrl" @click="openCheckoutAgain">
      Ouvrir la page de paiement
    </button>
  </section>
</template>

<script>
export default {
  name: "AttentePaiement",
  data() {
    return {
      ref: this.$route.query.ref || "",
      checkoutUrl: this.$route.query.checkoutUrl || "",
      status: "PENDING",
      error: "",
      intervalId: null,
      openedOnce: false,
      paidStatuses: ["PAID", "SUCCESSFUL", "SUCCESS"] // ← accepte les statuts SumUp
    };
  },
  computed: {
    isPaid() {
      return this.paidStatuses.includes(this.status);
    },
    isPending() {
      return !this.isPaid && this.status === "PENDING";
    }
  },
  mounted() {
    // Sécurité : ref obligatoire
    if (!this.ref) {
      this.error = "Référence de commande manquante.";
      return;
    }

    // Ouvre SumUp dans un NOUVEL onglet (une seule fois)
    if (this.checkoutUrl && !this.openedOnce) {
      window.open(this.checkoutUrl, "_blank");
      this.openedOnce = true;
    }

    // Lance le polling toutes les 3 secondes
    this.intervalId = setInterval(this.checkStatus, 3000);
    // Vérifie tout de suite une première fois
    this.checkStatus();
  },
  beforeUnmount() {
    if (this.intervalId) clearInterval(this.intervalId);
  },
  methods: {
    async checkStatus() {
      try {
        const res = await fetch(`/api/orders/${encodeURIComponent(this.ref)}/status`);
        if (!res.ok) throw new Error("Impossible de récupérer le statut.");
        const data = await res.json();
        this.status = data.status || "PENDING";

        // Si payé → stop polling + redirection vers /merci
        if (this.isPaid) {
          clearInterval(this.intervalId);
          window.location.href = `/merci?ref=${encodeURIComponent(this.ref)}`;
        }
      } catch (e) {
        this.error = e.message;
      }
    },
    openCheckoutAgain() {
      if (this.checkoutUrl) window.open(this.checkoutUrl, "_blank");
    }
  }
};
</script>

<style scoped>
.attente {
  max-width: 720px;
  margin: 60px auto;
  text-align: center;
  padding: 24px;
}
.err { color: #b00020; }
button {
  margin-top: 16px;
  padding: 10px 16px;
  border: 0;
  border-radius: 10px;
  cursor: pointer;
}
</style>
