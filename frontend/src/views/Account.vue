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
        <button @click="startTelegramAuth">
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
              <router-link 
              :to="{ path: '/track', query: { order: order.id } }"
              >
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
    this.init()
  },

  beforeUnmount() {
    this.stopPolling()
  },

  methods: {
    async init() {
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

    async startTelegramAuth() {
        this.stopPolling()
        this.manualTelegramUrl = ""

        if (!this.botUsername) {
            this.authError = "Не настроен Telegram-бот. Добавьте VITE_TG_BOT_USERNAME в переменные окружения фронтенда."
            return
        }

        let r
        try {
          r = await apiFetch("/auth/telegram/init", {
            method: "POST"
          })
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

        // На мобильных безопаснее открывать бота в новой вкладке/приложении,
        // иначе внутри webview можно получить белый экран.
        if (window.Telegram?.WebApp?.openTelegramLink) {
          window.Telegram.WebApp.openTelegramLink(telegramUrl)
        } else {
          const openedWindow = window.open(telegramUrl, "_blank", "noopener,noreferrer")
          if (!openedWindow) {
            this.authError = "Браузер заблокировал автоматическое открытие Telegram. Нажмите ссылку ниже."
          }
        }

        // начинаем polling
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
        const maxAttempts = 30 // ~60 сек, потому что интервал 2 сек

        this.pollIntervalId = setInterval(async () => {
            attempts++

            let r
            try {
              r = await apiFetch(`/auth/telegram/check?code=${code}`)
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
            }

            if (attempts >= maxAttempts) {
            this.stopPolling()
            this.authError = "Не видим подтверждение. Откройте Telegram → нажмите Start у бота → нажмите кнопку входа ещё раз."
            }
        }, 2000)
      }
  }
}
</script>
