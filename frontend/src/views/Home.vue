<template>
  <div class="app">
    <Header />
    <router-link to="/account">Аккаунт</router-link>
    <main class="content">
      <h2>Каталог</h2>
      <div v-if="loading">Загрузка товаров...</div>
      <div class="catalog">
        <ProductCard
          v-for="product in products"
          :key="product.id"
          :title="product.title"
          :price="product.price"
          :image="getImageUrl(product.image)"
          @buy="addToCart(product)"
        />
      </div>
      <div class="cart-info">
        <h3>Корзина</h3>
        <div v-if="cart.length === 0">Корзина пуста</div>
        <div v-else>
          <div v-for="item in cart" :key="item.id" class="cart-item">
            <span>{{ item.title }} x {{ item.quantity }} = {{ item.price * item.quantity }} ₽</span>
            <button @click="increaseQuantity(item)">+</button>
            <button @click="decreaseQuantity(item)">-</button>
            <button @click="removeFromCart(item)">❌</button>
          </div>
          <p>Итого товаров: {{ totalItems }} | Сумма: {{ totalPrice }} ₽</p>
        </div>
      </div>
      <div v-if="cart.length" class="order-form">
        <h3>Данные для заказа</h3>

        <label class="label">
            Имя
            <input v-model="customerName" class="input" type="text" placeholder="Иван" />
        </label>

        <label class="label">
            Телефон
            <input v-model="customerPhone" class="input" type="text" placeholder="+7 999 123-45-67" />
        </label>

        <label class="label">
            Адрес (необязательно)
            <input v-model="customerAddress" class="input" type="text" placeholder="Москва, улица..., дом..." />
        </label>
    </div>
      <button 
        v-if="cart.length"
        class="order-btn"
        @click="sendOrder"
      >
        {{ submitting ? 'Оформляем...' : 'Оформить заказ' }}
      </button>
    </main>
  </div>
</template>

<script>
import Header from '../components/Header.vue'
import ProductCard from '../components/ProductCard.vue'
import { apiFetch } from "../api"
import { getToken } from "../authToken"

export default {
  name: 'App',

  components: {
    Header,
    ProductCard
  },

  data() {
    return {
      products: [],  // пока пустой массив, данные придут с backend
      cart: [],       // текущая корзина
      loading: true,
      submitting: false,
      customerName: '',
      customerPhone: '',
      customerAddress: ''
    }
  },

  computed: {
    totalItems() {
      return this.cart.reduce((sum, item) => sum + item.quantity, 0)
    },
    totalPrice() {
      return this.cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
    }
  },

  methods: {
    addToCart(product) {
      const item = this.cart.find(p => p.id === product.id)
      if(item) item.quantity++
      else this.cart.push({ ...product, quantity: 1 })

      alert('Товар добавлен в корзину')
    },
    increaseQuantity(product) {
      const item = this.cart.find(p => p.id === product.id)
      if(item) item.quantity++
    },
    decreaseQuantity(product) {
      const item = this.cart.find(p => p.id === product.id)
      if(item) {
        item.quantity--
        if(item.quantity === 0) this.removeFromCart(product)
      }
    },
    removeFromCart(product) {
      this.cart = this.cart.filter(p => p.id !== product.id)
    },
    async fetchProducts() {
      try {
        const res = await apiFetch("/products")
        this.products = await res.json()
      } catch (e) {
        console.error('Ошибка загрузки товаров', e)
      } finally {
        this.loading = false
        this.submitting = false
      }
    },

    getImageUrl(image) {
      const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
        // если уже полный URL — возвращаем как есть
      if (image && (image.startsWith('http://') || image.startsWith('https://'))) {
            return image
      }
        // иначе считаем, что это имя файла
      return `${API_URL}/images/${image}`
    },

    async sendOrder() {
      if (this.submitting) return
      this.submitting = true

      const token = getToken()

      // 🚨 ЕСЛИ НЕ АВТОРИЗОВАН
      if (!token) {
        this.submitting = false
        this.$router.push({ path: "/account", query: { startAuth: "1", from: "checkout" } })
        return
      }

      if (!this.customerName.trim()) {
        alert('Введите имя')
        this.submitting = false
        return
      }

      if (!this.customerPhone.trim()) {
        alert('Введите телефон')
        this.submitting = false
        return
      }

      const order = {
        name: this.customerName,
        phone: this.customerPhone,
        address: this.customerAddress,
        items: this.cart.map(item => ({
          id: item.id,
          title: item.title,
          price: item.price,
          quantity: item.quantity
        })),
        total: this.totalPrice
      }

      try {
        const res = await apiFetch("/order", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(order)
        })

        // 🚨 если 401 — токен очищен, ведём пользователя в авторизацию
        if (!res.ok) {
          alert("Не удалось оформить заказ. Войдите через Telegram.")
          this.submitting = false
          return
        }

        const data = await res.json()

        const id = data.order_id

        this.cart = []
        this.customerName = ''
        this.customerPhone = ''
        this.customerAddress = ''

        localStorage.setItem("last_order_id", id)
        this.$router.push({ path: "/account", query: { startAuth: "1", from: "checkout" } })
      } catch (e) {
        console.error('Ошибка заказа', e)
        alert("Ошибка соединения")
      } finally {
        this.submitting = false
      }
    },
  },

  mounted() {
    this.fetchProducts()
  }
}
</script>



<style>
.app {
  font-family: Arial, sans-serif;
}

.content {
  padding: 16px;
}

.catalog {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.cart-info {
  padding: 12px;
  border: 1px solid #ddd;
  margin-bottom: 16px;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.cart-item button {
  padding: 4px 8px;
  cursor: pointer;
}

.order-form {
  border: 1px solid #ddd;
  padding: 12px;
  margin-top: 16px;
  margin-bottom: 12px;
}

.label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
}

.input {
  width: 100%;
  padding: 8px;
  margin-top: 6px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
</style>
