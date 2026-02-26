import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.config.errorHandler = function (err, instance, info) {
  console.error('Vue global error:', err, info, instance)
}

window.addEventListener('error', function (event) {
  console.error('Window error:', event.error || event.message)
})

window.addEventListener('unhandledrejection', function (event) {
  console.error('Unhandled promise rejection:', event.reason)
})

app.use(router)
app.mount('#app')
