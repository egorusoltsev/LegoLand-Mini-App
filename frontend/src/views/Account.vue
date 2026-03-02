<template>
  <div class="container account-page">
    <button class="btn btnSecondary back-btn" type="button" @click="$router.push('/')">← Назад</button>
    <h2 class="section-title">Аккаунт</h2>

    <div v-if="loading" class="surface-card state-card">Загрузка...</div>

    <div v-else>
      <div v-if="fatalError" class="error">{{ fatalError }}</div>

      <div v-if="showAuthChoices && !user" class="surface-card state-card">
        <p>Чтобы оформить заказ, войдите через Telegram.</p>
        <div class="auth-row">
          <button class="btn btnSecondary" @click="startTelegramAuth('login')">Войти</button>
          <button class="btn btnPrimary" @click="startTelegramAuth('register')">Зарегистрироваться</button>
        </div>
        <p v-if="authError" class="error">{{ authError }}</p>
      </div>

      <div v-if="user">
        <div class="surface-card state-card">
          <p><strong>{{ greetingLine }} 👋</strong></p>
          <p class="muted" v-if="profile.full_name">{{ profile.full_name }} · {{ profile.phone }}</p>
          <button class="btn btnSecondary" @click="logout">Выйти</button>
        </div>

        <div v-if="needsProfile" class="surface-card state-card profile-form">
          <h3>Заполните профиль</h3>
          <label>ФИО<input class="input" v-model="profileForm.full_name" type="text" /></label>
          <label>Телефон<input class="input" v-model="profileForm.phone" type="tel" placeholder="+7 999 123-45-67" /></label>
          <button class="btn btnPrimary" @click="saveProfile">Сохранить</button>
          <p v-if="profileError" class="error">{{ profileError }}</p>
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

      <p v-if="showDebugLine" class="debug-line">{{ debugLine }}</p>
    </div>
  </div>
</template>

<script>
import { setToken, getToken, clearToken } from '../authToken'
import { apiFetch, API_URL } from '../api'
import { UI_EVENTS } from '../constants'

export default {
  name: 'Account',

  data() {
    return {
      loading: true,
      user: null,
      profile: { full_name: '', phone: '' },
      profileForm: { full_name: '', phone: '' },
      orders: [],
      ordersLoading: false,
      authError: '',
      profileError: '',
      fatalError: '',
      authMode: 'login',
      debugLine: '',
      botUsername: (import.meta.env.VITE_TG_BOT_USERNAME || '').replace(/^@/, '')
    }
  },

  computed: {
    needsProfile() {
      return !this.profile.full_name || !this.profile.phone
    },
    showAuthChoices() {
      return !this.user
    },
    showDebugLine() {
      return import.meta.env.DEV || this.$route.query.debug === '1'
    },
    displayName() {
      const profileName = this.profile && this.profile.full_name ? String(this.profile.full_name).trim() : ''
      if (profileName) return profileName
      const userName = this.user && this.user.first_name ? String(this.user.first_name).trim() : ''
      if (userName) return userName
      const username = this.user && this.user.username ? String(this.user.username).trim() : ''
      if (username) return username
      const localName = localStorage.getItem('legoland_profile_name')
      if (localName && String(localName).trim()) return String(localName).trim()
      return ''
    },
    greetingLine() {
      if (this.displayName) return 'Привет, ' + this.displayName
      return 'Привет'
    }
  },

  mounted() {
    window.addEventListener(UI_EVENTS.OPEN_AUTH_CHOOSER, this.onAuthChooser)
    if (this.$route.query.mode === 'register') {
      this.authMode = 'register'
    }
    this.safeInit()
  },

  beforeUnmount() {
    window.removeEventListener(UI_EVENTS.OPEN_AUTH_CHOOSER, this.onAuthChooser)
  },

  methods: {
    onAuthChooser(event) {
      if (event && event.detail) this.authMode = String(event.detail)
    },
    setDebug(endpoint, status, message) {
      this.debugLine = 'API_URL=' + API_URL + ' | endpoint=' + endpoint + ' | status=' + status + ' | message=' + message
    },
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
        if (this.needsProfile && this.authMode === 'register') {
          this.profileForm.full_name = this.user.first_name || ''
          this.profileForm.phone = ''
        }
        await this.loadOrders()
      }
    },

    async loadMe() {
      const endpoint = '/me'
      try {
        const r = await apiFetch(endpoint)
        if (r.ok) {
          const data = await r.json()
          this.user = data.user
          this.profile = data.profile || { full_name: '', phone: '' }
          if (this.profile && this.profile.full_name) localStorage.setItem('legoland_profile_name', String(this.profile.full_name))
          this.setDebug(endpoint, r.status, 'ok')
        } else {
          const message = await r.text()
          this.setDebug(endpoint, r.status, message)
          clearToken()
          this.user = null
        }
      } catch (e) {
        console.error('loadMe error', e)
        this.setDebug(endpoint, 'network_error', e && e.message ? e.message : 'unknown')
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
      this.profile = { full_name: '', phone: '' }
      this.profileForm = { full_name: '', phone: '' }
    },

    async startTelegramAuth(mode) {
      this.authMode = mode || 'login'
      if (!this.botUsername) {
        this.authError = 'Не настроен Telegram-бот. Добавьте VITE_TG_BOT_USERNAME в переменные окружения фронтенда.'
        return
      }

      let r
      const endpoint = '/auth/telegram/init'
      try {
        r = await apiFetch(endpoint, { method: 'POST' })
      } catch (e) {
        console.error('Ошибка запуска Telegram-авторизации', e)
        this.setDebug(endpoint, 'network_error', e && e.message ? e.message : 'unknown')
        this.authError = 'Не удалось запустить авторизацию. Проверьте соединение и попробуйте снова.'
        return
      }

      if (!r.ok) {
        const message = await r.text()
        this.setDebug(endpoint, r.status, message)
        this.authError = 'Ошибка запуска авторизации.'
        return
      }

      const data = await r.json()
      this.setDebug(endpoint, r.status, 'ok')
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
      const endpoint = '/auth/telegram/check'
      let attempts = 0
      const maxAttempts = 30

      const interval = setInterval(async () => {
        attempts += 1

        let r
        try {
          r = await apiFetch(endpoint + '?code=' + code)
        } catch (e) {
          clearInterval(interval)
          console.error('Ошибка polling авторизации', e)
          this.setDebug(endpoint, 'network_error', e && e.message ? e.message : 'unknown')
          this.authError = 'Проблема с соединением при проверке входа.'
          return
        }

        if (!r.ok) {
          const message = await r.text()
          clearInterval(interval)
          this.setDebug(endpoint, r.status, message)
          this.authError = 'Ошибка проверки авторизации.'
          return
        }

        const data = await r.json()
        this.setDebug(endpoint, r.status, data.status)

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

    async saveProfile() {
      this.profileError = ''
      const fullName = String(this.profileForm.full_name || '').trim()
      const phone = String(this.profileForm.phone || '').trim()
      if (!fullName) {
        this.profileError = 'Укажите ФИО.'
        return
      }
      if (!/^\+?[0-9\-()\s]{10,18}$/.test(phone)) {
        this.profileError = 'Укажите корректный телефон.'
        return
      }
      const endpoint = '/me'
      const response = await apiFetch(endpoint, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, phone })
      })
      if (!response.ok) {
        this.profileError = 'Не удалось сохранить профиль.'
        return
      }
      const data = await response.json()
      this.profile = data.profile
      if (this.profile && this.profile.full_name) localStorage.setItem('legoland_profile_name', String(this.profile.full_name))
      this.profileForm = { full_name: '', phone: '' }
      this.authMode = 'login'
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
.back-btn { margin-bottom: 12px; }
.state-card { padding: 16px; }
.auth-row { display: flex; gap: 8px; margin-top: 10px; }
.profile-form { margin-top: 14px; display: grid; gap: 10px; }
.error { margin: 10px 0; color: #b00020; }
.debug-line { margin-top: 12px; font-size: 12px; color: #4b5563; word-break: break-word; }
.orders-title { margin: 20px 0 12px; }
.orders-list { display: grid; gap: 10px; }
.order-card { padding: 14px; display: grid; gap: 6px; }
</style>
