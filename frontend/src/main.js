import { installDebugOverlay } from "./debugOverlay"
installDebugOverlay()

import { createApp } from "vue"
import "./style.css"
import App from "./App.vue"
import router from "./router"

function showFatal(title, err, info) {
  var msg = ""
  try {
    msg = (err && err.stack) ? err.stack : String(err)
  } catch (e) {
    msg = "Unknown error"
  }

  var extra = info ? ("\n\nINFO:\n" + String(info)) : ""
  document.body.innerHTML =
    "<pre style='white-space:pre-wrap;padding:20px;font-size:14px;color:#b00020'>" +
    title + "\n\n" + msg + extra +
    "</pre>"
}

window.addEventListener("error", function (e) {
  showFatal("WINDOW ERROR", e && e.message ? e.message : e, "")
})

window.addEventListener("unhandledrejection", function (e) {
  showFatal("UNHANDLED PROMISE", e && e.reason ? e.reason : e, "")
})

const app = createApp(App)

// ✅ ВОТ ЭТО главное: ловим ошибки Vue, которые не уходят в window
app.config.errorHandler = function (err, instance, info) {
  showFatal("VUE ERROR", err, info)
}

// ✅ Ловим ошибки роутера
router.onError(function (err) {
  showFatal("ROUTER ERROR", err, "")
})

app.use(router)

// иногда полезно монтировать после готовности роутера
router.isReady().then(function () {
  app.mount("#app")
}).catch(function (err) {
  showFatal("ROUTER ISREADY ERROR", err, "")
})