<template>
  <div class="admin">
    <h2>Админка — заказы</h2>

    <div v-if="orders.length === 0">
      Заказов пока нет
    </div>

    <div v-else>
      <div
        v-for="(order, index) in orders"
        :key="index"
        class="order-card"
      >
        <p><b>Имя:</b> {{ order.name }}</p>
        <p><b>Телефон:</b> {{ order.phone }}</p>

        <p><b>Товары:</b></p>
        <ul>
          <li v-for="item in order.items" :key="item.id">
            {{ item.title }} × {{ item.quantity }} ({{ item.price }} ₽)
          </li>
        </ul>

        <p><b>Итого:</b> {{ order.total }} ₽</p>
        <p><b>Статус:</b> {{ order.status || 'старый заказ' }}</p>
        <div class="status-buttons" v-if="order.id">
          <button @click="setStatus(order.id, 'new')">new</button>
          <button @click="setStatus(order.id, 'confirmed')">confirmed</button>
          <button @click="setStatus(order.id, 'shipped')">shipped</button>
          <button @click="setStatus(order.id, 'done')">done</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Admin',

  data() {
    return {
      orders: [],
      adminKey: '12345'
    }
  },

  async mounted() {
    try {
      const res = await fetch('http://localhost:8000/orders', {
                          headers: {
                            'X-Admin-Key': this.adminKey
                          }
                        })
      this.orders = await res.json()
    } catch (e) {
      console.error('Ошибка загрузки заказов', e)
    }
  },

  methods: {
    async setStatus(orderId, newStatus) {
        try {
            await fetch(`http://localhost:8000/orders/${orderId}/status`, {
                method: 'PATCH',
                headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': this.adminKey
                },
                body: JSON.stringify({ status: newStatus })
            })

            // обновляем список заказов
            const res = await fetch('http://localhost:8000/orders')
            this.orders = await res.json()
            } catch (e) {
            console.error('Ошибка смены статуса', e)
            }
        }
    }
}
</script>

<style>
.admin {
  padding: 20px;
}

.order-card {
  border: 1px solid #ccc;
  padding: 12px;
  margin-bottom: 16px;
}

.status-buttons {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.status-buttons button {
  padding: 6px 10px;
  cursor: pointer;
}
</style>