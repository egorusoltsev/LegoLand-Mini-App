import { installDebugOverlay } from "./debugOverlay"
installDebugOverlay()

window.addEventListener("error", (e) => {
  var msg = ""
  try {
    msg = (e && e.message) ? e.message : String(e)
  } catch (err) {
    msg = "Unknown error"
  }

  document.body.innerHTML =
    "<pre style='white-space:pre-wrap;padding:20px;font-size:14px;color:red'>" +
    "JS ERROR:\n" + msg +
    "</pre>"
})

window.addEventListener("unhandledrejection", (e) => {
  var msg = ""
  try {
    msg = (e && e.reason) ? String(e.reason) : String(e)
  } catch (err) {
    msg = "Unknown rejection"
  }

  document.body.innerHTML =
    "<pre style='white-space:pre-wrap;padding:20px;font-size:14px;color:red'>" +
    "PROMISE ERROR:\n" + msg +
    "</pre>"
})

import { createApp } from "vue"
import "./style.css"
import App from "./App.vue"
import router from "./router"

const app = createApp(App)
app.use(router)
app.mount("#app")