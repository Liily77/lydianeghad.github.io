// src/main.js

import { BASE } from './utils/api.js'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { api } from './utils/api.js'



const _fetch = window.fetch.bind(window)
window.fetch = (input, init) => {
  let url = input
  if (typeof url === 'string' && url.startsWith('/')) {
    url = BASE + url
  }
  if (
    import.meta.env.MODE === 'production' &&
    typeof url === 'string' &&
    url.startsWith('http://localhost:3001')
  ) {
    url = url.replace('http://localhost:3001', BASE)
  }
  console.log('[patched fetch] →', url)  // ← ajoute ce log
  return _fetch(url, init)
}

const app = createApp(App)
app.use(router)
app.config.globalProperties.$api = api
app.mount('#app')
