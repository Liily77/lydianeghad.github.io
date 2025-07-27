<template>
  <div id="app">
    <Navbar />
    <router-view />
    <SiteFooter />
  </div>
</template>

<script>
import Navbar    from '@/components/Navbar.vue'
import SiteFooter from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    SiteFooter
  }
}
</script>

<style>
/* Appliquer le fond beige clair à toute la page */
html, body, #app {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background-color: #f9f4f0;
}

</style>

