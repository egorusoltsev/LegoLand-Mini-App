import { installDebugOverlay } from "./debugOverlay"
installDebugOverlay()

window.addEventListener("error", (e) => {
  document.body.innerHTML =
    "<pre style='white-space:pre-wrap;padding:20px;font-size:14px;color:red'>" +
    "JS ERROR:\n" + (e?.message || e) +
    "</pre>"
})

window.addEventListener("unhandledrejection", (e) => {
  document.body.innerHTML =
    "<pre style='white-space:pre-wrap;padding:20px;font-size:14px;color:red'>" +
    "PROMISE ERROR:\n" + (e?.reason || e) +
    "</pre>"
})


import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')