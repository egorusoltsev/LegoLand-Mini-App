<template>
  <div class="account">
    <h2>Аккаунт</h2>

    <div v-if="loading">
      Загрузка...
    </div>

    <div v-else>
      <div v-if="fatalError" style="margin:10px 0; color:#b00020;">
        {{ fatalError }}
      </div>

      <!-- НЕ ЗАЛОГИНЕН -->
      <div v-if="!user">
        <p>Чтобы оформить заказ, войдите через Telegram.</p>
        <button @click="startTelegramAuth">
          Войти через Telegram
        </button>
        <p v-if="authError" style="margin-top:10px; color:#b00020;">
          {{ authError }}
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
          this.authError = 'Ошибка проверки авторизации. Попробуйте ещё раз.'
          return
        }

        try {
          const data = await r.json()

          if (data.status === 'ok') {
            clearInterval(interval)
            setToken(data.token)

            await this.loadMe()
            if (this.user) {
              await this.loadOrders()
            }
          }
        } catch (e) {
          clearInterval(interval)
          console.error('Ошибка чтения ответа авторизации', e)
          this.authError = 'Получен некорректный ответ сервера при входе.'
          return
        }

        if (attempts >= maxAttempts) {
          clearInterval(interval)
          this.authError = 'Не видим подтверждение. Откройте Telegram → нажмите Start у бота → нажмите кнопку входа ещё раз.'
        }
      }, 2000)
    },

    formatDate(ts) {
      return new Date(ts * 1000).toLocaleString()
    }
  }
}
</script>
