<template>
  <div class="track">
    <h2>Проверка статуса заказа</h2>

    <div v-if="!order">
      <input
        v-model="orderId"
        placeholder="Введите номер заказа"
        class="input"
      />
      <button @click="fetchOrder">Проверить</button>
    </div>

    <div v-if="loading">Загрузка...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="order" class="order-box">
      <p><b>Номер:</b> {{ order.id }}</p>
      <p><b>Статус:</b> {{ order.status }}</p>
      <p><b>Дата:</b> {{ formatDate(order.created_at) }}</p>
      <p><b>Сумма:</b> {{ order.total }} ₽</p>

      <h4>Товары:</h4>
      <ul>
        <li v-for="item in order.items" :key="item.title">
          {{ item.title }} × {{ item.quantity }} ({{ item.price }} ₽)
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "Track",

  data() {
    return {
      orderId: "",
      order: null,
      loading: false,
      error: ""
    }
  },

  mounted() {
    const params = new URLSearchParams(window.location.search)
    const id = params.get("order")

    if (!id || id === "undefined" || id === "null") {
        return
    }

    this.orderId = id
    this.fetchOrder()
    },

  methods: {
    async fetchOrder() {
        if (!this.orderId || isNaN(this.orderId)) {
            this.error = "Некорректный номер заказа"
            return
        }

        this.loading = true
        this.error = ""
        this.order = null

        try {
            const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')

            const controller = new AbortController()
            const timeout = setTimeout(() => controller.abort(), 8000)

            const res = await fetch(
            `${API_URL}/public/orders/${this.orderId}`,
            { signal: controller.signal }
            )

            clearTimeout(timeout)

            if (!res.ok) {
            this.error = "Заказ не найден"
            this.loading = false
            return
            }

            const data = await res.json()
            this.order = data

        } catch (e) {
            console.error("Track error:", e)
            this.error = "Ошибка соединения"
        }

        this.loading = false
    },

    formatDate(ts) {
      if (!ts) return "-"
      return new Date(ts * 1000).toLocaleString()
    }
  }
}
</script>

<style>
.track {
  padding: 20px;
}

.input {
  padding: 8px;
  margin-right: 8px;
}

.order-box {
  margin-top: 20px;
  border: 1px solid #ccc;
  padding: 15px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
