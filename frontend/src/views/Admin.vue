<template>
  <div class="admin">
    <h2>Админка — заказы</h2>
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
      adminKey: '12345',
      loading: false,
      error: '',
      
      newTitle: '',
      newPrice: 0,
      newImage: '',
      selectedFile: null
    }
  },

  async mounted() {
    try {
        const API_URL = import.meta.env.VITE_API_URL

        // загружаем заказы
        const ordersRes = await fetch(`${API_URL}/orders`)
        this.orders = await ordersRes.json()

        // загружаем товары
        this.loadProducts()

    } catch (e) {
        console.error('Ошибка загрузки админки', e)
    }
  },

  methods: {
    async setStatus(orderId, newStatus) {
        try {
            const API_URL = import.meta.env.VITE_API_URL

            await fetch(`${API_URL}/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': this.adminKey
            },
            body: JSON.stringify({ status: newStatus })
            })

            // обновляем список заказов
            const res = await fetch(`${API_URL}/orders`)
            this.orders = await res.json()

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
        this.selectedFile = e.target.files[0] || null
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

            // 👇 ВАЖНО: сюда подставляем filename, а не полный URL
            this.newImage = data.filename
            alert('Фото загружено, теперь можно добавить товар')

        } catch (e) {
            console.error('Ошибка upload', e)
        }
      },
    async addProduct() {
        if (!this.newTitle.trim()) return alert('Введите название')
        if (!this.newImage.trim()) return alert('Введите image')

        try {
            const API_URL = import.meta.env.VITE_API_URL
            await fetch(`${API_URL}/admin/products`, {
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

            this.newTitle = ''
            this.newPrice = 0
            this.newImage = ''

            this.loadProducts()
        } catch (e) {
            console.error('Ошибка добавления товара', e)
        }
      },
    async deleteProduct(id) {
        if (!confirm('Удалить товар?')) return

        try {
            const API_URL = import.meta.env.VITE_API_URL
            await fetch(`${API_URL}/admin/products/${id}`, {
            method: 'DELETE',
            headers: {
                'X-Admin-Key': this.adminKey
            }
            })

            this.loadProducts()
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