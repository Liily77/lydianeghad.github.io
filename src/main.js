// src/main.js

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  // <-- importe ton système de routes


createApp(App)
  .use(router)   // injecte le router dans ton appli Vue
  .mount('#app') // monte l'app dans l'élément HTML avec l'id "app"
