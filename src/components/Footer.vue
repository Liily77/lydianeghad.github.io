<template>
  <footer class="site-footer">
    <div class="footer-content">
      <p class="footer-text">
        © {{ new Date().getFullYear() }}  Arc en Ciel – Tous droits réservés.  
        <span class="footer-links"> Mentions légales | CGV | Politique de confidentialité </span>
      </p>
    </div>
  </footer>
</template>

<script>
export default { name: 'SiteFooter' }
</script>

<style scoped>
.site-footer {
  background-color: #6c5b82;
  color: #fff;
  font-family: 'Raleway', sans-serif;
  padding: 1rem 1rem;
  text-align: center;
  margin-top: 0 !important; 
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-text {
  margin: 0;
  line-height: 1.5;
  font-size: 0.9rem;
}

/* ================= */
/* Styles MOBILE ONLY */
/* ================= */

@media (max-width: 600px) {
  .site-footer {
    padding: clamp(0.3rem, 1.8vw, 0.6rem) clamp(0.3rem, 2.5vw, 0.8rem);
  }

  .footer-text {
    font-size: clamp(0.6rem, 1.8vw, 0.8rem);
    line-height: clamp(1.2, 2vw, 1.35);
    padding: 0 clamp(0.2rem, 1vw, 0.5rem);
  }

  .footer-links {
    display: block;
    margin-top: 0.2rem;
  }
}
</style>
