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
      ordersLoading: false
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
      }
        this.loading = false
                
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

    async startTelegramAuth() {
        const r = await apiFetch("/auth/telegram/init", {
            method: "POST"
        })

        if (!r.ok) {
            alert("Ошибка запуска авторизации")
            return
        }

        const data = await r.json()
        const code = data.code

        // открываем бота
        window.open(
            `https://t.me/legoland_orders_bot?start=web_${code}`,
            "_blank"
        )

        // начинаем polling
        this.pollAuth(code)
        },

        pollAuth(code) {
        const interval = setInterval(async () => {
            const r = await apiFetch(`/auth/telegram/check?code=${code}`)
            const data = await r.json()

            if (data.status === "ok") {
            clearInterval(interval)
            setToken(data.token)
            window.location.reload()
            }
        }, 2000)
    }
  }
}
</script>
