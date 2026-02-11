<template>
  <div class="admin">
    <h2>Админка</h2>

    <div v-if="!adminKey" class="login-box">
        <p>Введите ключ админа:</p>
        <input v-model="adminKeyInput" placeholder="Admin key" />
        <button @click="login">Войти</button>
    </div>

    <div v-else>
        <button class="logout" @click="logout">Выйти</button>

        <!-- ДАЛЬШЕ ОСТАВЛЯЕШЬ ТВОЙ ТЕКУЩИЙ КОД АДМИНКИ: заказы/товары/кнопки -->
        <!-- то есть твой v-for orders/products, формы добавления и т.д. -->
    </div>
    <hr />

    <h3>Товары</h3>

    <div class="add-product">
    <input v-model="newTitle" class="input" placeholder="Название" />
    <input v-model.number="newPrice" class="input" type="number" placeholder="Цена" />
    <input v-model="newImage" class="input" placeholder="image (например xwing.jpg)" />
    <button @click="addProduct">Добавить</button>
    <input type="file" @change="onFileChange" />
    <button @click="uploadImage">Загрузить фото</button>
    </div>

    <div v-if="products.length === 0">Товаров пока нет</div>

    <div v-for="p in products" :key="p.id" class="product-row">
    <span>#{{ p.id }} — {{ p.title }} — {{ p.price }} ₽ — {{ p.image }}</span>
    <button @click="deleteProduct(p.id)">Удалить</button>
    </div>

    <hr />

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
      products: [],

      adminKey: '',          // ключ хранится тут
      adminKeyInput: '',     // поле ввода ключа

      loading: false,
      error: '',

      newTitle: '',
      newPrice: 0,
      newImage: '',

      selectedFile: null
    }
  },

  mounted() {
    const savedKey = localStorage.getItem('ADMIN_KEY')
    if (savedKey) {
      this.adminKey = savedKey
      this.loadAll()
    }
  },

  methods: {
    login() {
      const key = this.adminKeyInput.trim()
      if (!key) return alert('Введите ключ')

      this.adminKey = key
      localStorage.setItem('ADMIN_KEY', key)
      this.adminKeyInput = ''

      this.loadAll()
    },

    logout() {
      this.adminKey = ''
      localStorage.removeItem('ADMIN_KEY')
      this.orders = []
      this.products = []
    },

    async loadAll() {
      await this.fetchOrders()
      await this.loadProducts()
    },

    async fetchOrders() {
      try {
        const API_URL = import.meta.env.VITE_API_URL
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

    async setStatus(orderId, newStatus) {
      try {
        const API_URL = import.meta.env.VITE_API_URL

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
        const API_URL = import.meta.env.VITE_API_URL
        const res = await fetch(`${API_URL}/products`)
        this.products = await res.json()
      } catch (e) {
        console.error('Ошибка загрузки товаров', e)
      }
    },

    onFileChange(e) {
      this.selectedFile = e.target.files?.[0] || null
    },

    async uploadImage() {
      if (!this.selectedFile) return alert('Выбери файл')

      try {
        const API_URL = import.meta.env.VITE_API_URL
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
        const API_URL = import.meta.env.VITE_API_URL
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
        const API_URL = import.meta.env.VITE_API_URL
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
  margin-bottom: 6px;
}
</style>