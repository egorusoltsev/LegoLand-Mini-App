<template>
  <div class="container admin">
    <h2 class="section-title">Админка</h2>

    <div v-if="!adminKey" class="login-box surface-card">
        <p>Введите ключ админа:</p>
        <input v-model="adminKeyInput" placeholder="Admin key" class="input" />
        <button class="btn-primary" @click="login">Войти</button>
    </div>

    <div v-else>
        <button class="btn-secondary logout" @click="logout">Выйти</button>

        <!-- ДАЛЬШЕ ОСТАВЛЯЕШЬ ТВОЙ ТЕКУЩИЙ КОД АДМИНКИ: заказы/товары/кнопки -->
        <!-- то есть твой v-for orders/products, формы добавления и т.д. -->
    </div>
    <hr />

    <h3>Товары</h3>

    <div class="add-product">
    <input v-model="newTitle" class="input" placeholder="Название" />
    <input v-model.number="newPrice" class="input" type="number" placeholder="Цена" />
    <input v-model="newImage" class="input" placeholder="image (например xwing.jpg)" />
    <button
      class="btn-primary"
      @click="addProduct"
      :disabled="!newTitle.trim() || !newImage"
    >
      Добавить
    </button>

    <input type="file" @change="onFileChange" />
    <button class="btn-secondary" @click="uploadImage">Загрузить фото</button>
    </div>

    <div v-if="products.length === 0">Товаров пока нет</div>

    <div v-for="p in products" :key="p.id" class="product-row">
    <span>#{{ p.id }} — {{ p.title }} — {{ p.price }} ₽ — {{ p.image }}</span>
    <button class="btn-secondary" @click="deleteProduct(p.id)">Удалить</button>
    </div>

    <hr />

    <div v-if="orders.length === 0">
      Заказов пока нет
    </div>

    <div v-else>
      <div
        v-for="order in sortedOrders"
        :key="order.id"
        class="order-card"
        :class="{
          focus: focusOrderId && Number(order.id) === Number(focusOrderId),
          fresh: Number(order.id) > Number(lastSeenOrderId || 0)
        }"
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
        <p v-if="order.created_at">
          <b>Дата:</b> {{ formatDate(order.created_at) }}
        </p>
        <div class="status-buttons" v-if="order.id">
          <button class="btn-secondary" @click="setStatus(order.id, 'new')">new</button>
          <button class="btn-secondary" @click="setStatus(order.id, 'confirmed')">confirmed</button>
          <button class="btn-secondary" @click="setStatus(order.id, 'shipped')">shipped</button>
          <button class="btn-secondary" @click="setStatus(order.id, 'done')">done</button>
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
      products: [],

      adminKey: '',          // ключ хранится тут
      adminKeyInput: '',     // поле ввода ключа

      loading: false,
      error: '',

      newTitle: '',
      newPrice: 0,
      newImage: '',

      selectedFile: null,
      lastSeenOrderId: 0,
      focusOrderId: null,
      refreshTimer: null
    }
  },

  mounted() {
    const savedKey = localStorage.getItem('ADMIN_KEY')
    if (savedKey) {
      this.adminKey = savedKey
      this.loadAll()
      this.startAutoRefresh()
    }
          // 1) фокус на заказ из ссылки Telegram
      const params = new URLSearchParams(window.location.search)
      const oid = params.get('order')
      if (oid) this.focusOrderId = Number(oid)

      // 2) lastSeen для подсветки новых
      const saved = localStorage.getItem('LAST_SEEN_ORDER_ID')
      if (saved) this.lastSeenOrderId = Number(saved)
  },

  computed: {
    sortedOrders() {
      // новые сверху. если created_at нет (старые заказы) — считаем как 0
      return [...this.orders].sort((a, b) => (b.created_at || 0) - (a.created_at || 0))
    },
    displayedOrders() {
    // если пришли по ссылке ?order=ID — показываем этот заказ первым
    if (!this.focusOrderId) return this.sortedOrders

    const top = this.sortedOrders.filter(o => Number(o.id) === this.focusOrderId)
    const rest = this.sortedOrders.filter(o => Number(o.id) !== this.focusOrderId)
    return [...top, ...rest]
  }
  },


  methods: {
    formatDate(ts) {
      // ts в секундах
      return new Date(ts * 1000).toLocaleString()
    },

    login() {
      const key = this.adminKeyInput.trim()
      if (!key) return alert('Введите ключ')

      this.adminKey = key
      localStorage.setItem('ADMIN_KEY', key)
      this.adminKeyInput = ''

      this.loadAll()
      this.startAutoRefresh()
    },

    logout() {
      this.adminKey = ''
      localStorage.removeItem('ADMIN_KEY')
      this.orders = []
      this.products = []

      this.stopAutoRefresh()
    },

    startAutoRefresh() {
      this.stopAutoRefresh()
      this.refreshTimer = setInterval(() => {
        this.fetchOrdersAndMarkNew()
      }, 10000)
    },

    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer)
        this.refreshTimer = null
      }
    },

    async loadAll() {
      await this.fetchOrders()
      await this.loadProducts()
    },

    async fetchOrders() {
      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const res = await fetch(`${API_URL}/orders`, {
          headers: {
            'X-Admin-Key': this.adminKey
          }
        })

        if (!res.ok) {
          const text = await res.text()
          console.error('fetchOrders error:', res.status, text)
          return
        }

        this.orders = await res.json()
      } catch (e) {
        console.error('Ошибка загрузки заказов', e)
      }
    },

    async fetchOrdersAndMarkNew() {
      await this.fetchOrders()

      // обновим lastSeen до максимального id, который уже есть (чтобы новые подсвечивались корректно)
      const maxId = Math.max(0, ...this.orders.map(o => Number(o.id || 0)))
      if (maxId > (this.lastSeenOrderId || 0)) {
        this.lastSeenOrderId = maxId
        localStorage.setItem('LAST_SEEN_ORDER_ID', String(maxId))
      }
    },


    async setStatus(orderId, newStatus) {
      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const patchRes = await fetch(`${API_URL}/orders/${orderId}/status`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-Admin-Key': this.adminKey
          },
          body: JSON.stringify({ status: newStatus })
        })

        if (!patchRes.ok) {
          const text = await patchRes.text()
          console.error('setStatus error:', patchRes.status, text)
          return
        }

        // обновляем список заказов правильно (с ключом)
        await this.fetchOrders()
      } catch (e) {
        console.error('Ошибка смены статуса', e)
      }
    },

    async loadProducts() {
      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const res = await fetch(`${API_URL}/products`)
        this.products = await res.json()
      } catch (e) {
        console.error('Ошибка загрузки товаров', e)
      }
    },

    onFileChange(e) {
      const files = e && e.target ? e.target.files : null
      this.selectedFile = files && files[0] ? files[0] : null
    },

    async uploadImage() {
      if (!this.selectedFile) return alert('Выбери файл')

      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const formData = new FormData()
        formData.append('file', this.selectedFile)

        const res = await fetch(`${API_URL}/admin/upload`, {
          method: 'POST',
          headers: {
            'X-Admin-Key': this.adminKey
          },
          body: formData
        })

        const data = await res.json()

        if (!res.ok) {
          console.error(data)
          return alert('Ошибка загрузки файла')
        }

        // сохраняем filename
        this.newImage = data.filename
        alert('Фото загружено, теперь можно добавить товар')
      } catch (e) {
        console.error('Ошибка upload', e)
      }
    },

    async addProduct() {
      if (!this.newTitle.trim()) return alert('Введите название')
      if (!this.newImage.trim()) return alert('Сначала загрузите фото (upload)')

      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const res = await fetch(`${API_URL}/admin/products`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Admin-Key': this.adminKey
          },
          body: JSON.stringify({
            title: this.newTitle,
            price: this.newPrice,
            image: this.newImage
          })
        })

        if (!res.ok) {
          const text = await res.text()
          console.error('addProduct error:', res.status, text)
          return alert('Ошибка добавления товара')
        }

        this.newTitle = ''
        this.newPrice = 0
        this.newImage = ''
        this.selectedFile = null

        await this.loadProducts()
      } catch (e) {
        console.error('Ошибка добавления товара', e)
      }
    },

    async deleteProduct(id) {
      if (!confirm('Удалить товар?')) return

      try {
        const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        const res = await fetch(`${API_URL}/admin/products/${id}`, {
          method: 'DELETE',
          headers: {
            'X-Admin-Key': this.adminKey
          }
        })

        if (!res.ok) {
          const text = await res.text()
          console.error('deleteProduct error:', res.status, text)
          return alert('Ошибка удаления товара')
        }

        await this.loadProducts()
      } catch (e) {
        console.error('Ошибка удаления товара', e)
      }
    }
  }
}
</script>


<style>
.admin {
  padding-top: 24px;
  padding-bottom: 28px;
}

.login-box {
  padding: 16px;
  display: grid;
  gap: 10px;
}

.order-card {
  border: 1px solid #ececec;
  border-radius: 16px;
  background: #fff;
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

.add-product {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.product-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fff;
  margin-bottom: 6px;
}

.order-card.focus {
  border: 2px solid #000;
}

.order-card.fresh {
  box-shadow: 0 0 0 3px rgba(0,0,0,0.08);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

</style>
