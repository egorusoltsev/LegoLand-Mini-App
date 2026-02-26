<template>
  <div class="container track-page">
    <h2 class="section-title">Проверка статуса заказа</h2>

    <div v-if="loading" class="surface-card box">Загрузка...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="order" class="surface-card box">
      <p><b>Номер:</b> {{ order.id }}</p>
      <p><b>Статус:</b> {{ order.status }}</p>
      <p><b>Дата:</b> {{ formatDate(order.created_at) }}</p>
      <p><b>Сумма:</b> {{ order.total }} ₽</p>

      <h4>Товары:</h4>
      <ul>
        <li v-for="(item, idx) in (order.items || [])" :key="item.id || idx">
          {{ item.title }} × {{ item.quantity }} ({{ item.price }} ₽)
        </li>
      </ul>

      <button class="btn btnSecondary" @click="order = null">Проверить другой заказ</button>
    </div>

    <div v-else class="surface-card box checker">
      <input v-model="orderId" placeholder="Введите номер заказа" class="input" />
      <button class="btn btnPrimary" @click="fetchOrder">Проверить</button>
    </div>
  </div>
</template>

<script>
import { getToken } from '../authToken'

export default {
  name: 'Track',

  data() {
    return {
      orderId: '',
      order: null,
      loading: false,
      error: ''
    }
  },

  mounted() {
    const token = getToken()
    if (!token) {
      this.$router.replace('/account')
      return
    }
    const id = this.$route.query.order
    if (id) {
      this.orderId = id
      this.fetchOrder()
    }
  },

  methods: {
    async fetchOrder() {
      const raw = String(this.orderId || '').trim()

      if (!raw) {
        this.error = 'Введите номер заказа'
        return
      }
      if (isNaN(Number(raw))) {
        this.error = 'Некорректный номер заказа'
        return
      }

      this.loading = true
      this.error = ''
      this.order = null

      const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
      const url = API_URL + '/public/orders/' + encodeURIComponent(raw)

      const controller = new AbortController()
      const timeout = setTimeout(function () { controller.abort() }, 8000)

      try {
        const res = await fetch(url, {
          method: 'GET',
          signal: controller.signal,
          cache: 'no-store'
        })

        if (!res.ok) {
          this.error = 'Заказ не найден (HTTP ' + res.status + ')'
          return
        }

        const data = await res.json()

        if (!data || !data.id) {
          this.error = 'Сервер вернул некорректный ответ'
          return
        }

        this.order = data
      } catch (e) {
        if (String(e).includes('AbortError')) {
          this.error = 'Сервер долго отвечает. Попробуйте ещё раз.'
        } else {
          this.error = 'Ошибка соединения (возможно, блокируется в браузере/вебвью)'
        }
      } finally {
        clearTimeout(timeout)
        this.loading = false
      }
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
.track-page { padding-top: 24px; }
.box { padding: 16px; }
.checker { display: flex; gap: 10px; }
.error { color: #b00020; }
@media (max-width: 680px) {
  .checker { flex-direction: column; }
}
</style>
