<template>
  <div class="account">
    <h2>Аккаунт</h2>

    <div v-if="loading">
      Загрузка...
    </div>

    <div v-else>
      <!-- НЕ ЗАЛОГИНЕН -->
      <div v-if="!user">
        <p>Войдите через Telegram, чтобы видеть свои заказы.</p>
        <div ref="telegramWidget"></div>
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
              <a :href="`/track?order=${order.id}`">Открыть трекинг</a>
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
      botUsername: import.meta.env.VITE_TG_BOT_USERNAME
    }
  },

  mounted() {
    console.log("BOT USERNAME:", this.botUsername)
    // ВАЖНО: стартуем через init()
    this.init()
  },

  
  methods: {
    async init() {
      const token = getToken()

      if (token) {
        await this.loadMe()
        if (this.user) {
          await this.loadOrders()
        }
        this.loading = false
        return
      }

      // нет токена → показываем виджет
      this.loading = false
      this.$nextTick(() => {
        this.renderTelegramWidget()
      })
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
      this.loading = false

      this.$nextTick(() => {
        this.renderTelegramWidget()
      })
    },

    async onTelegramAuth(tgUser) {
      const r = await apiFetch("/auth/telegram", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ data: tgUser })
      })

      if (!r.ok) {
        alert("Ошибка входа через Telegram")
        return
      }

      const data = await r.json()
      setToken(data.token)

      await this.loadMe()
      if (this.user) {
        await this.loadOrders()
      }
    },

    renderTelegramWidget() {
      // если username не задан — виджет не появится
      if (!this.botUsername) {
        console.error("VITE_TG_BOT_USERNAME is missing")
        return
      }

      const container = this.$refs.telegramWidget
      if (!container) return

      container.innerHTML = ""

      // глобальная функция для telegram-widget
      window.onTelegramAuth = (user) => {
        this.onTelegramAuth(user)
      }

      const script = document.createElement("script")
      script.src = "https://telegram.org/js/telegram-widget.js?22"
      script.async = true
      script.setAttribute("data-telegram-login", this.botUsername)
      script.setAttribute("data-size", "large")
      script.setAttribute("data-onauth", "onTelegramAuth(user)")
      script.setAttribute("data-request-access", "write")

      container.appendChild(script)
    },


    formatDate(ts) {
      const d = new Date(ts * 1000)
      return d.toLocaleString()
    }
  }
}
</script>
