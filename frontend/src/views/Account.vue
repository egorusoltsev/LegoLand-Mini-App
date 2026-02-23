<template>
  <div class="account">
    <h2>Аккаунт</h2>

    <div v-if="loading">
      Загрузка...
    </div>

    <div v-else>
      <!-- НЕ ЗАЛОГИНЕН -->
      <div v-if="!user">
        <p>Чтобы оформить заказ, войдите через Telegram.</p>
        <button @click="startTelegramAuth(true)">
          Войти через Telegram
        </button>

        <p v-if="authError" style="margin-top:10px; color:#b00020;">
          {{ authError }}
        </p>

        <p v-if="manualTelegramUrl" style="margin-top:10px;">
          <a :href="manualTelegramUrl" target="_blank" rel="noopener noreferrer">
            Открыть Telegram-бота вручную
          </a>
        </p>
      </div>

      <!-- ЗАЛОГИНЕН -->
      <div v-else>
        <p>
          <strong>Привет, {{ user.first_name || user.username }} 👋</strong>
        </p>

        <button @click="logout">Выйти</button>

        <h3 style="margin-top:20px;">Мои заказы</h3>

        <div v-if="ordersLoading">
          Загрузка заказов...
        </div>

        <div v-else-if="orders.length === 0">
          У вас пока нет заказов.
        </div>

        <div v-else>
          <div
            v-for="order in orders"
            :key="order.id"
            style="border:1px solid #ddd; padding:10px; margin:10px 0; border-radius:10px;"
          >
            <div><b>ID:</b> {{ order.id }}</div>
            <div><b>Статус:</b> {{ order.status }}</div>
            <div><b>Сумма:</b> {{ order.total }} ₽</div>
            <div><b>Дата:</b> {{ formatDate(order.created_at) }}</div>
            <div>
              <router-link :to="{ path: '/track', query: { order: order.id } }">
                Открыть трекинг
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { setToken, getToken, clearToken } from "../authToken"
import { apiFetch } from "../api"

console.log("ACCOUNT FILE LOADED")
export default {
  name: "Account",

  data() {
    return {
      loading: true,
      user: null,
      orders: [],
      ordersLoading: false,
      authError: "",
      botUsername: (import.meta.env.VITE_TG_BOT_USERNAME || "").replace(/^@/, ""),
      autoAuthStarted: false,
      manualTelegramUrl: "",
      pollIntervalId: null
    }
  },

  mounted() {
    console.log("ACCOUNT MOUNTED")

    try {
        this.init()
    } catch (e) {
        alert("INIT ERROR: " + e)
        console.error(e)
    }
  },

  beforeUnmount() {
    this.stopPolling()
  },

  methods: {
    async init() {
        try {
            const token = getToken()

            if (token) {
            await this.loadMe()
            if (this.user) {
                await this.loadOrders()
            }
            }

            this.loading = false

            if (!this.user && this.$route?.query?.startAuth === "1" && !this.autoAuthStarted) {
            this.autoAuthStarted = true
            await this.startTelegramAuth()
            }
        } catch (e) {
            alert("INIT CRASH: " + e)
            console.error(e)
        }
    },

    async loadMe() {
      const r = await apiFetch("/me")
      if (r.ok) {
        const data = await r.json()
        this.user = data.user
      } else {
        clearToken()
        this.user = null
      }
    },

    async loadOrders() {
      this.ordersLoading = true
      const r = await apiFetch("/my/orders")
      if (r.ok) {
        const data = await r.json()
        this.orders = data.orders || []
      } else {
        this.orders = []
      }
      this.ordersLoading = false
    },

    async logout() {
      clearToken()
      this.user = null
      this.orders = []
      this.authError = ""
    },

    // autoOpen=true -> пытаемся открыть TG
    async startTelegramAuth(autoOpen) {
      this.stopPolling()
      this.manualTelegramUrl = ""
      this.authError = ""

      if (!this.botUsername) {
        this.authError = "Не настроен Telegram-бот. Добавьте VITE_TG_BOT_USERNAME в переменные окружения фронтенда."
        return
      }

      let r
      try {
        r = await apiFetch("/auth/telegram/init", { method: "POST" })
      } catch (e) {
        console.error("Ошибка запуска Telegram-авторизации", e)
        this.authError = "Не удалось запустить авторизацию. Проверьте соединение и попробуйте снова."
        return
      }

      if (!r.ok) {
        this.authError = "Ошибка запуска авторизации. Попробуйте ещё раз."
        return
      }

      const data = await r.json()
      const code = data.code

      const telegramUrl = `https://t.me/${this.botUsername}?start=web_${code}`
      this.manualTelegramUrl = telegramUrl

      // ⚠️ без optional chaining, + максимально безопасно для мобилок
      if (autoOpen) {
        try {
          if (
            window.Telegram &&
            window.Telegram.WebApp &&
            typeof window.Telegram.WebApp.openTelegramLink === "function"
          ) {
            window.Telegram.WebApp.openTelegramLink(telegramUrl)
          } else {
            // На некоторых мобильных webview window.open = белый экран/блок
            // Поэтому не насилуем. Пусть юзер тапнет по ссылке, если не TG WebApp.
            const opened = window.open(telegramUrl, "_blank", "noopener,noreferrer")
            if (!opened) {
              this.authError = "Браузер заблокировал автоматическое открытие Telegram. Нажмите ссылку ниже."
            }
          }
        } catch (e) {
          // если что-то пошло не так — просто оставляем ручную ссылку
          console.warn("Не удалось автоматически открыть Telegram", e)
        }
      }

      // запускаем polling сразу (юзер может подтвердить чуть позже)
      this.pollAuth(code)
    },

    stopPolling() {
      if (this.pollIntervalId) {
        clearInterval(this.pollIntervalId)
        this.pollIntervalId = null
      }
    },

    pollAuth(code) {
      this.authError = ""

      let attempts = 0
      const maxAttempts = 30 // ~60 сек (2 сек интервал)

      this.pollIntervalId = setInterval(async () => {
        attempts++

        let r
        try {
          r = await apiFetch(`/auth/telegram/check?code=${encodeURIComponent(code)}`)
        } catch (e) {
          this.stopPolling()
          console.error("Ошибка polling авторизации", e)
          this.authError = "Проблема с соединением при проверке входа."
          return
        }

        if (!r.ok) {
          this.stopPolling()
          this.authError = "Ошибка проверки авторизации. Попробуйте ещё раз."
          return
        }

        const data = await r.json()

        if (data.status === "ok") {
          this.stopPolling()
          setToken(data.token)
          this.manualTelegramUrl = ""

          await this.loadMe()
          if (this.user) await this.loadOrders()
          return
        }

        if (attempts >= maxAttempts) {
          this.stopPolling()
          this.authError = "Не видим подтверждение. Откройте Telegram → нажмите Start у бота → попробуйте ещё раз."
        }
      }, 2000)
    },

    formatDate(ts) {
      const n = Number(ts)
      if (!n || isNaN(n)) return "-"
      return new Date(n * 1000).toLocaleString()
    }
  }
}
</script>