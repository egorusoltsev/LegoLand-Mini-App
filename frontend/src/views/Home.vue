<template>
  <div>
    <Header />
    <main class="container home-page">
      <section class="hero surface-card">
        <p class="pill">Оригинальные LEGO наборы</p>
        <h1>LEGOland — оригинальные наборы LEGO по ценам ниже рынка</h1>
        <p class="muted">Подборка редких и популярных наборов с быстрой доставкой по РФ.</p>
        <button class="btn-primary" type="button" @click="scrollToCatalog">Перейти в каталог</button>
      </section>

      <section id="catalog" class="catalog-section">
        <div class="section-head">
          <h2 class="section-title">Каталог</h2>
          <p class="muted">Найдено: {{ filteredProducts.length }} товаров</p>
        </div>

        <div class="catalog-layout">
          <aside class="filters surface-card">
            <h3>Фильтры</h3>
            <label>
              Категория
              <select v-model="selectedCategory">
                <option value="all">Все</option>
                <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
              </select>
            </label>

            <label>
              Цена от
              <input v-model="minPrice" type="number" min="0" placeholder="0" />
            </label>
            <label>
              Цена до
              <input v-model="maxPrice" type="number" min="0" placeholder="150000" />
            </label>

            <label>
              Сортировка
              <select v-model="sortBy">
                <option value="popular">По популярности</option>
                <option value="price-asc">Сначала дешевле</option>
                <option value="price-desc">Сначала дороже</option>
              </select>
            </label>
          </aside>

          <div>
            <div v-if="loading" class="surface-card loading">Загрузка товаров...</div>
            <div v-else class="catalog-grid">
              <ProductCard
                v-for="product in filteredProducts"
                :key="product.id"
                :product="product"
                @buy="addToCart"
              />
            </div>
          </div>
        </div>
      </section>

      <section class="surface-card cart-panel" v-if="cart.length">
        <h2 class="section-title">Корзина</h2>
        <div class="cart-row" v-for="item in cart" :key="item.id">
          <div>
            <strong>{{ item.title }}</strong>
            <p class="muted">{{ formatPrice(item.price) }} ₽ × {{ item.quantity }}</p>
          </div>
          <div class="cart-actions">
            <button type="button" class="btn-secondary" @click="decreaseQuantity(item)">−</button>
            <button type="button" class="btn-secondary" @click="increaseQuantity(item)">+</button>
            <button type="button" class="btn-secondary" @click="removeFromCart(item)">Удалить</button>
          </div>
        </div>
        <p class="cart-total">Итого: <strong>{{ totalItems }}</strong> шт. на <strong>{{ formatPrice(totalPrice) }} ₽</strong></p>
      </section>

      <section class="surface-card order-panel" v-if="cart.length">
        <h2 class="section-title">Данные для заказа</h2>
        <div class="order-grid">
          <label>
            Имя
            <input v-model="customerName" type="text" placeholder="Иван" />
          </label>
          <label>
            Телефон
            <input v-model="customerPhone" type="text" placeholder="+7 999 123-45-67" />
          </label>
          <label class="wide">
            Адрес (необязательно)
            <input v-model="customerAddress" type="text" placeholder="Москва, улица..., дом..." />
          </label>
        </div>

        <label class="policy">
          <input v-model="agreePolicy" type="checkbox" />
          <span>Согласен с <a href="#" @click.prevent>политикой обработки данных</a></span>
        </label>

        <button class="btn-primary desktop-order-btn" type="button" @click="sendOrder">
          {{ submitting ? 'Оформляем...' : 'Оформить заказ' }}
        </button>
      </section>

      <button v-if="cart.length" class="btn-primary fixed-order-btn" type="button" @click="sendOrder">
        {{ submitting ? 'Оформляем...' : 'Оформить заказ • ' + formatPrice(totalPrice) + ' ₽' }}
      </button>

      <section class="options">
        <h2 class="section-title">Опции</h2>
        <div class="options-grid">
          <article class="surface-card option-card">
            <div class="option-icon">🎁</div>
            <h3>Подарочная упаковка</h3>
            <p class="muted">Оформим набор как готовый подарок с карточкой и лентой.</p>
          </article>
          <article class="surface-card option-card">
            <div class="option-icon">🧱</div>
            <h3>Сборка конструктора</h3>
            <p class="muted">Можно заказать профессиональную сборку перед вручением.</p>
          </article>
        </div>
      </section>

      <section class="faq">
        <h2 class="section-title">FAQ</h2>
        <div class="faq-list">
          <article v-for="(item, index) in faqItems" :key="item.question" class="surface-card faq-item">
            <button class="faq-toggle" type="button" @click="toggleFaq(index)">
              {{ item.question }}
              <span>{{ openFaqIndex === index ? '−' : '+' }}</span>
            </button>
            <p v-if="openFaqIndex === index" class="muted">{{ item.answer }}</p>
          </article>
        </div>
      </section>

      <section class="surface-card contacts">
        <h2 class="section-title">Связаться с нами</h2>
        <div class="contact-grid">
          <label>
            Имя
            <input v-model="contactName" type="text" placeholder="Ваше имя" />
          </label>
          <label>
            Телефон
            <input v-model="contactPhone" type="text" placeholder="+7 900 000-00-00" />
          </label>
        </div>
        <a class="btn-primary tg-link" :href="telegramContactUrl" target="_blank" rel="noopener noreferrer">Написать в Telegram</a>
      </section>

      <footer class="footer muted">© LEGOland Mini App</footer>

      <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
    </main>
  </div>
</template>

<script>
import Header from '../components/Header.vue'
import ProductCard from '../components/ProductCard.vue'
import { apiFetch } from '../api'
import { getToken } from '../authToken'
import { getCart, saveCart } from '../cartStore'

export default {
  name: 'HomeView',
  components: { Header, ProductCard },
  data() {
    return {
      products: [],
      cart: [],
      loading: true,
      submitting: false,
      customerName: '',
      customerPhone: '',
      customerAddress: '',
      agreePolicy: false,
      selectedCategory: 'all',
      minPrice: '',
      maxPrice: '',
      sortBy: 'popular',
      openFaqIndex: null,
      toastMessage: '',
      toastTimer: null,
      contactName: '',
      contactPhone: '',
      telegramContactUrl: 'https://t.me/your_telegram_placeholder',
      faqItems: [
        { question: 'Это оригинальные LEGO?', answer: 'Да, мы продаём только оригинальные наборы LEGO в заводской упаковке.' },
        { question: 'Какие сроки доставки?', answer: 'По Москве — от 1 дня, по РФ обычно 2–6 дней в зависимости от региона.' },
        { question: 'Можно ли сделать подарочную упаковку?', answer: 'Да, добавим подарочную упаковку и открытку по вашему пожеланию.' },
        { question: 'Как оформить заказ в Telegram?', answer: 'Добавьте товары в корзину, заполните форму и нажмите «Оформить заказ».' },
        { question: 'Можно ли вернуть товар?', answer: 'Да, возврат возможен по правилам дистанционной торговли при сохранении вида товара.' },
        { question: 'Есть ли самовывоз?', answer: 'Пока нет, работаем с доставкой.' }
      ]
    }
  },
  computed: {
    categories() {
      return ['Star Wars', 'Technic', 'City', 'Icons']
    },
    preparedProducts() {
      return this.products.map((product) => {
        return {
          ...product,
          image: this.getImageUrl(product.image)
        }
      })
    },
    filteredProducts() {
      let result = this.preparedProducts.slice()
      const min = Number(this.minPrice)
      const max = Number(this.maxPrice)

      if (!isNaN(min) && min > 0) {
        result = result.filter(function (product) {
          return Number(product.price) >= min
        })
      }
      if (!isNaN(max) && max > 0) {
        result = result.filter(function (product) {
          return Number(product.price) <= max
        })
      }

      if (this.sortBy === 'price-asc') {
        result.sort(function (a, b) { return Number(a.price) - Number(b.price) })
      }
      if (this.sortBy === 'price-desc') {
        result.sort(function (a, b) { return Number(b.price) - Number(a.price) })
      }

      return result
    },
    totalItems() {
      return this.cart.reduce(function (sum, item) {
        return sum + item.quantity
      }, 0)
    },
    totalPrice() {
      return this.cart.reduce(function (sum, item) {
        return sum + item.price * item.quantity
      }, 0)
    }
  },
  methods: {
    formatPrice(value) {
      return new Intl.NumberFormat('ru-RU').format(value)
    },
    showToast(message) {
      this.toastMessage = message
      if (this.toastTimer) clearTimeout(this.toastTimer)
      this.toastTimer = setTimeout(() => {
        this.toastMessage = ''
      }, 2000)
    },
    toggleFaq(index) {
      this.openFaqIndex = this.openFaqIndex === index ? null : index
    },
    scrollToCatalog() {
      const section = document.getElementById('catalog')
      if (section && section.scrollIntoView) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },
    persistCart() {
      saveCart(this.cart)
    },
    addToCart(product) {
      const item = this.cart.find(function (entry) {
        return entry.id === product.id
      })
      if (item) item.quantity += 1
      else this.cart.push({ ...product, quantity: 1 })
      this.persistCart()
      this.showToast('Добавлено в корзину')
    },
    increaseQuantity(product) {
      const item = this.cart.find(function (entry) {
        return entry.id === product.id
      })
      if (item) item.quantity += 1
      this.persistCart()
    },
    decreaseQuantity(product) {
      const item = this.cart.find(function (entry) {
        return entry.id === product.id
      })
      if (item) {
        item.quantity -= 1
        if (item.quantity <= 0) this.removeFromCart(product)
      }
      this.persistCart()
    },
    removeFromCart(product) {
      this.cart = this.cart.filter(function (entry) {
        return entry.id !== product.id
      })
      this.persistCart()
    },
    async fetchProducts() {
      try {
        const res = await apiFetch('/products')
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
      if (image && (image.startsWith('http://') || image.startsWith('https://'))) {
        return image
      }
      return API_URL + '/images/' + image
    },
    async sendOrder() {
      if (this.submitting) return
      this.submitting = true

      const token = getToken()
      if (!token) {
        this.submitting = false
        this.$router.push('/account')
        return
      }

      if (!this.customerName.trim()) {
        this.showToast('Введите имя')
        this.submitting = false
        return
      }
      if (!this.customerPhone.trim()) {
        this.showToast('Введите телефон')
        this.submitting = false
        return
      }
      if (!this.agreePolicy) {
        this.showToast('Подтвердите согласие с политикой')
        this.submitting = false
        return
      }

      const order = {
        name: this.customerName,
        phone: this.customerPhone,
        address: this.customerAddress,
        items: this.cart.map(function (item) {
          return {
            id: item.id,
            title: item.title,
            price: item.price,
            quantity: item.quantity
          }
        }),
        total: this.totalPrice
      }

      try {
        const res = await apiFetch('/order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(order)
        })

        if (!res.ok) {
          this.showToast('Не удалось оформить заказ. Войдите через Telegram.')
          this.submitting = false
          return
        }

        const data = await res.json()
        const id = data.order_id

        this.cart = []
        this.customerName = ''
        this.customerPhone = ''
        this.customerAddress = ''
        this.agreePolicy = false
        this.persistCart()

        localStorage.setItem('last_order_id', id)
        this.$router.push('/account')
      } catch (e) {
        console.error('Ошибка заказа', e)
        this.showToast('Ошибка соединения')
      } finally {
        this.submitting = false
      }
    }
  },
  mounted() {
    this.cart = getCart()
    this.fetchProducts()
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer)
      this.toastTimer = null
    }
  }
}
</script>

<style scoped>
.home-page { padding-top: 22px; padding-bottom: 70px; }
.hero { padding: clamp(22px, 4vw, 42px); background: linear-gradient(135deg, #fff7cc, #ffd6d6 55%, #ffffff); margin-bottom: 26px; }
.hero .pill { margin-bottom: 12px; }
.hero p { max-width: 600px; }
.hero button { margin-top: 8px; }
.section-head { display: flex; justify-content: space-between; gap: 10px; align-items: end; margin-bottom: 14px; }
.catalog-layout { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
.filters { padding: 16px; height: fit-content; position: sticky; top: 86px; }
.filters h3 { margin-bottom: 10px; }
.filters label { display: block; margin-bottom: 10px; font-size: 14px; }
.catalog-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.loading { padding: 18px; }
.cart-panel, .order-panel, .contacts { margin-top: 22px; padding: 18px; }
.cart-row { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #efefef; padding: 10px 0; }
.cart-actions { display: flex; gap: 6px; }
.cart-total { margin-top: 14px; font-size: 18px; }
.order-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.wide { grid-column: 1 / -1; }
.policy { margin-top: 10px; display: inline-flex; align-items: center; gap: 8px; }
.policy input { width: auto; }
.desktop-order-btn { margin-top: 14px; min-width: 220px; }
.fixed-order-btn { position: fixed; left: 12px; right: 12px; bottom: 10px; z-index: 60; box-shadow: var(--shadow); display: none; }
.options, .faq { margin-top: 28px; }
.options-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.option-card { padding: 20px; }
.option-icon { width: 46px; height: 46px; border-radius: 12px; background: #fff4d0; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 12px; }
.faq-list { display: grid; gap: 10px; }
.faq-item { padding: 14px; }
.faq-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; background: transparent; border: 0; padding: 0; font-weight: 600; text-align: left; }
.contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.tg-link { display: inline-flex; }
.footer { padding: 28px 0 12px; text-align: center; }
.toast { position: fixed; right: 14px; bottom: 18px; background: #111; color: #fff; padding: 10px 14px; border-radius: 12px; z-index: 100; box-shadow: var(--shadow); }

@media (max-width: 980px) {
  .catalog-layout { grid-template-columns: 1fr; }
  .filters { position: static; }
  .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 700px) {
  .section-head { flex-direction: column; align-items: start; }
  .catalog-grid { grid-template-columns: 1fr; }
  .options-grid, .contact-grid, .order-grid { grid-template-columns: 1fr; }
  .cart-row { flex-direction: column; }
  .desktop-order-btn { display: none; }
  .fixed-order-btn { display: block; }
}
</style>
