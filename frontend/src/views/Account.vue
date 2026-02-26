<template>
  <div class="container account-page">
    <h2 class="section-title">Аккаунт</h2>

    <div v-if="loading" class="surface-card state-card">Загрузка...</div>

    <div v-else>
      <div v-if="fatalError" class="error">{{ fatalError }}</div>

      <div v-if="!user" class="surface-card state-card">
        <p>Чтобы оформить заказ, войдите через Telegram.</p>
        <button class="btn-primary" @click="startTelegramAuth">Войти через Telegram</button>
        <p v-if="authError" class="error">{{ authError }}</p>
      </div>

      <div v-else>
        <div class="surface-card state-card">
          <p><strong>Привет, {{ user.first_name || user.username }} 👋</strong></p>
          <button class="btn-secondary" @click="logout">Выйти</button>
        </div>

        <h3 class="orders-title">Мои заказы</h3>

        <div v-if="ordersLoading" class="surface-card state-card">Загрузка заказов...</div>
        <div v-else-if="orders.length === 0" class="surface-card state-card">У вас пока нет заказов.</div>

        <div v-else class="orders-list">
          <article v-for="order in orders" :key="order.id" class="surface-card order-card">
            <div><b>ID:</b> {{ order.id }}</div>
            <div><b>Статус:</b> {{ order.status }}</div>
            <div><b>Сумма:</b> {{ order.total }} ₽</div>
            <div><b>Дата:</b> {{ formatDate(order.created_at) }}</div>
            <router-link :to="{ path: '/track', query: { order: order.id } }" class="pill">Открыть трекинг</router-link>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { setToken, getToken, clearToken } from '../authToken'
import { apiFetch } from '../api'

export default {
  name: 'Account',

  data() {
    return {
      loading: true,
      user: null,
      orders: [],
      ordersLoading: false,
      authError: '',
      fatalError: '',
      botUsername: (import.meta.env.VITE_TG_BOT_USERNAME || '').replace(/^@/, '')
    }
  },

  mounted() {
    this.safeInit()
  },

  methods: {
    async safeInit() {
      try {
        await this.init()
      } catch (e) {
        console.error('Account init failed', e)
        this.fatalError = 'Не удалось открыть аккаунт. Попробуйте обновить страницу.'
      } finally {
        this.loading = false
      }
    },

    async init() {
      const token = getToken()

      if (!token) {
        return
      }

      await this.loadMe()
      if (this.user) {
        await this.loadOrders()
      }
    },

    async loadMe() {
      try {
        const r = await apiFetch('/me')

        if (r.ok) {
          const data = await r.json()
          this.user = data.user
        } else {
          clearToken()
          this.user = null
        }
      } catch (e) {
        console.error('loadMe error', e)
        clearToken()
        this.user = null
      }
    },

    async loadOrders() {
      this.ordersLoading = true

      try {
        const r = await apiFetch('/my/orders')

        if (r.ok) {
          const data = await r.json()
          this.orders = data.orders || []
        } else {
          this.orders = []
        }
      } catch (e) {
        console.error('loadOrders error', e)
        this.orders = []
      } finally {
        this.ordersLoading = false
      }
    },

    async logout() {
      clearToken()
      this.user = null
      this.orders = []
      this.authError = ''
      this.fatalError = ''
    },

    async startTelegramAuth() {
      if (!this.botUsername) {
        this.authError = 'Не настроен Telegram-бот. Добавьте VITE_TG_BOT_USERNAME в переменные окружения фронтенда.'
        return
      }

      let r
      try {
        r = await apiFetch('/auth/telegram/init', {
          method: 'POST'
        })
      } catch (e) {
        console.error('Ошибка запуска Telegram-авторизации', e)
        this.authError = 'Не удалось запустить авторизацию. Проверьте соединение и попробуйте снова.'
        return
      }

      if (!r.ok) {
        this.authError = 'Ошибка запуска авторизации.'
        return
      }

      const data = await r.json()
      const code = data.code

      const telegramUrl = 'https://t.me/' + this.botUsername + '?start=web_' + code

      const hasTelegram = typeof window !== 'undefined' && window.Telegram
      const hasWebApp = hasTelegram && window.Telegram.WebApp
      const canOpenTelegramLink = hasWebApp && typeof window.Telegram.WebApp.openTelegramLink === 'function'

      if (canOpenTelegramLink) {
        window.Telegram.WebApp.openTelegramLink(telegramUrl)
      } else {
        const openedWindow = window.open(telegramUrl, '_blank', 'noopener,noreferrer')
        if (!openedWindow) {
          window.location.href = telegramUrl
        }
      }

      this.pollAuth(code)
    },

    pollAuth(code) {
      this.authError = ''

      let attempts = 0
      const maxAttempts = 30

      const interval = setInterval(async () => {
        attempts += 1

        let r
        try {
          r = await apiFetch('/auth/telegram/check?code=' + code)
        } catch (e) {
          clearInterval(interval)
          console.error('Ошибка polling авторизации', e)
          this.authError = 'Проблема с соединением при проверке входа.'
          return
        }

        if (!r.ok) {
          clearInterval(interval)
          this.authError = 'Ошибка проверки авторизации.'
          return
        }

        const data = await r.json()

        if (data.status === 'pending') {
          if (attempts >= maxAttempts) {
            clearInterval(interval)
            this.authError = 'Время ожидания истекло. Нажмите «Войти через Telegram» ещё раз.'
          }
          return
        }

        clearInterval(interval)

        if (data.status === 'ok' && data.token) {
          setToken(data.token)
          this.loading = true
          await this.safeInit()
        } else {
          this.authError = 'Авторизация не завершена.'
        }
      }, 2500)
    },

    formatDate(ts) {
      const n = Number(ts)
      if (!n || isNaN(n)) return '-'
      return new Date(n * 1000).toLocaleString()
    }
  }
}
</script>

<style scoped>
.account-page { padding-top: 24px; padding-bottom: 30px; }
.state-card { padding: 16px; }
.error { margin: 10px 0; color: #b00020; }
.orders-title { margin: 20px 0 12px; }
.orders-list { display: grid; gap: 10px; }
.order-card { padding: 14px; display: grid; gap: 6px; }
</style>
