<template>
  <div>
    <Header />
    <main class="container home-page">
      <section class="hero surface-card">
        <div class="hero-dots" aria-hidden="true"></div>
        <p class="pill">Оригинальные LEGO наборы</p>
        <h1><LogoText /> — оригинальные наборы LEGO по ценам ниже рынка</h1>
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
            <label>Категория<select v-model="selectedCategory"><option value="all">Все</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option></select></label>
            <label>Цена от<input v-model="minPrice" type="number" min="0" placeholder="0" /></label>
            <label>Цена до<input v-model="maxPrice" type="number" min="0" placeholder="150000" /></label>
            <label>Сортировка<select v-model="sortBy"><option value="popular">По популярности</option><option value="price-asc">Сначала дешевле</option><option value="price-desc">Сначала дороже</option></select></label>
          </aside>

          <div>
            <div v-if="loading" class="surface-card loading">Загрузка товаров...</div>
            <div v-else class="catalog-grid">
              <ProductCard v-for="product in filteredProducts" :key="product.id" :product="product" :favorite="isFavorite(product.id)" @buy="addToCart" @toggle-favorite="toggleFavorite" />
            </div>
          </div>
        </div>
      </section>

      <section class="surface-card cart-panel" v-if="cart.length" id="cart-section">
        <h2 class="section-title">Корзина</h2>
        <div class="cart-row" v-for="item in cart" :key="item.id">
          <div><strong>{{ item.title }}</strong><p class="muted">{{ formatPrice(item.price) }} ₽ × {{ item.quantity }}</p></div>
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
          <label>Имя<input v-model="customerName" type="text" placeholder="Иван" /></label>
          <label>Телефон<input v-model="customerPhone" type="text" placeholder="+7 999 123-45-67" /></label>
          <label class="wide">Адрес (необязательно)<input v-model="customerAddress" type="text" placeholder="Москва, улица..., дом..." /></label>
        </div>
        <label class="policy"><input v-model="agreePolicy" type="checkbox" /><span>Согласен с <a href="#" @click.prevent>политикой обработки данных</a></span></label>
        <button class="btn-primary desktop-order-btn" type="button" @click="sendOrder">{{ submitting ? 'Оформляем...' : 'Оформить заказ' }}</button>
      </section>

      <button v-if="cart.length" class="btn-primary fixed-order-btn" type="button" @click="sendOrder">{{ submitting ? 'Оформляем...' : 'Оформить заказ • ' + formatPrice(totalPrice) + ' ₽' }}</button>

      <section class="faq">
        <h2 class="section-title">FAQ</h2>
        <div class="faq-list">
          <article v-for="(item, index) in faqItems" :key="item.question" class="surface-card faq-item">
            <button class="faq-toggle" type="button" @click="toggleFaq(index)">{{ item.question }}<span>{{ openFaqIndex === index ? '−' : '+' }}</span></button>
            <p v-if="openFaqIndex === index" class="muted">{{ item.answer }}</p>
          </article>
        </div>
      </section>

      <section class="surface-card contacts">
        <h2 class="section-title">Связаться с нами</h2>
        <div class="contact-grid"><label>Имя<input v-model="contactName" type="text" placeholder="Ваше имя" /></label><label>Телефон<input v-model="contactPhone" type="text" placeholder="+7 900 000-00-00" /></label></div>
        <a class="btn-primary tg-link" :href="telegramContactUrl" target="_blank" rel="noopener noreferrer">Написать в Telegram</a>
      </section>

      <footer class="footer muted">© {{ brandName }} Mini App</footer>
      <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
    </main>

    <div v-if="cartDrawerOpen" class="drawer-overlay" @click="closeDrawers">
      <aside class="drawer" @click.stop>
        <h3>Корзина</h3>
        <p v-if="!cart.length" class="muted">Корзина пока пустая.</p>
        <div v-for="item in cart" :key="item.id" class="drawer-item"><strong>{{ item.title }}</strong><p>{{ item.quantity }} × {{ formatPrice(item.price) }} ₽</p></div>
      </aside>
    </div>

    <div v-if="favoritesDrawerOpen" class="drawer-overlay" @click="closeDrawers">
      <aside class="drawer" @click.stop>
        <h3>Избранное</h3>
        <p v-if="!favorites.length" class="muted">Пока нет избранных наборов.</p>
        <div v-for="product in favorites" :key="product.id" class="drawer-item">
          <strong>{{ product.title }}</strong>
          <p>{{ formatPrice(product.price) }} ₽</p>
          <div class="drawer-actions"><button class="btn-primary" type="button" @click="addToCart(product)">В корзину</button><button class="btn-secondary" type="button" @click="toggleFavorite(product)">Убрать</button></div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import Header from '../components/Header.vue'
import ProductCard from '../components/ProductCard.vue'
import LogoText from '../components/LogoText.vue'
import { apiFetch } from '../api'
import { getToken } from '../authToken'
import { BRAND_NAME, TELEGRAM_CONTACT_URL, UI_EVENTS } from '../constants'
import { getCart, addToCart, removeFromCart, updateCartQuantity, setCart, subscribeCart } from '../store/cart'
import { getFavorites, toggleFavorite, subscribeFavorites } from '../store/favorites'

export default {
  name: 'HomeView',
  components: { Header, ProductCard, LogoText },
  data() {
    return {
      brandName: BRAND_NAME,
      products: [],
      cart: [],
      favorites: [],
      cartDrawerOpen: false,
      favoritesDrawerOpen: false,
      loading: true,
      submitting: false,
      customerName: '', customerPhone: '', customerAddress: '', agreePolicy: false,
      selectedCategory: 'all', minPrice: '', maxPrice: '', sortBy: 'popular',
      openFaqIndex: null, toastMessage: '', toastTimer: null,
      contactName: '', contactPhone: '',
      telegramContactUrl: TELEGRAM_CONTACT_URL,
      unsubscribeCart: null,
      unsubscribeFavorites: null,
      faqItems: [
        { question: 'Это оригинальные LEGO?', answer: 'Да, мы продаём только оригинальные наборы LEGO в заводской упаковке.' },
        { question: 'Какие сроки доставки?', answer: 'По Москве — от 1 дня, по РФ обычно 2–6 дней в зависимости от региона.' },
        { question: 'Можно ли сделать подарочную упаковку?', answer: 'Да, добавим подарочную упаковку и открытку по вашему пожеланию.' },
        { question: 'Как оформить заказ в Telegram?', answer: 'Добавьте товары в корзину, заполните форму и нажмите «Оформить заказ».' },
        { question: 'Можно ли вернуть товар?', answer: 'Да, возврат возможен по правилам дистанционной торговли при сохранении вида товара.' }
      ]
    }
  },
  computed: {
    categories() { return ['Star Wars', 'Technic', 'City', 'Icons'] },
    preparedProducts() { return this.products.map((product) => ({ ...product, image: this.getImageUrl(product.image) })) },
    filteredProducts() {
      let result = this.preparedProducts.slice()
      const min = Number(this.minPrice)
      const max = Number(this.maxPrice)
      if (!isNaN(min) && min > 0) result = result.filter(function (product) { return Number(product.price) >= min })
      if (!isNaN(max) && max > 0) result = result.filter(function (product) { return Number(product.price) <= max })
      if (this.sortBy === 'price-asc') result.sort(function (a, b) { return Number(a.price) - Number(b.price) })
      if (this.sortBy === 'price-desc') result.sort(function (a, b) { return Number(b.price) - Number(a.price) })
      return result
    },
    totalItems() { return this.cart.reduce(function (sum, item) { return sum + item.quantity }, 0) },
    totalPrice() { return this.cart.reduce(function (sum, item) { return sum + item.price * item.quantity }, 0) }
  },
  methods: {
    formatPrice(value) { return new Intl.NumberFormat('ru-RU').format(value) },
    isFavorite(productId) {
      return this.favorites.some(function (item) { return item.id === productId })
    },
    toggleFavorite(product) {
      this.favorites = toggleFavorite(product)
      this.showToast(this.isFavorite(product.id) ? 'Добавлено в избранное' : 'Убрано из избранного')
    },
    showToast(message) {
      this.toastMessage = message
      if (this.toastTimer) clearTimeout(this.toastTimer)
      this.toastTimer = setTimeout(() => { this.toastMessage = '' }, 2000)
    },
    toggleFaq(index) { this.openFaqIndex = this.openFaqIndex === index ? null : index },
    scrollToCatalog() {
      const section = document.getElementById('catalog')
      if (section && section.scrollIntoView) section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    addToCart(product) {
      this.cart = addToCart(product)
      this.showToast('Добавлено в корзину')
    },
    increaseQuantity(product) {
      this.cart = updateCartQuantity(product.id, Number(product.quantity) + 1)
    },
    decreaseQuantity(product) {
      this.cart = updateCartQuantity(product.id, Number(product.quantity) - 1)
    },
    removeFromCart(product) {
      this.cart = removeFromCart(product.id)
    },
    onOpenCart() {
      this.cartDrawerOpen = true
      this.favoritesDrawerOpen = false
      const section = document.getElementById('cart-section')
      if (section && section.scrollIntoView) section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    onOpenFavorites() {
      this.favoritesDrawerOpen = true
      this.cartDrawerOpen = false
    },
    closeDrawers() {
      this.cartDrawerOpen = false
      this.favoritesDrawerOpen = false
    },
    async fetchProducts() {
      try { const res = await apiFetch('/products'); this.products = await res.json() }
      catch (e) { console.error('Ошибка загрузки товаров', e) }
      finally { this.loading = false; this.submitting = false }
    },
    getImageUrl(image) {
      const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
      if (image && (image.startsWith('http://') || image.startsWith('https://'))) return image
      return API_URL + '/images/' + image
    },
    async sendOrder() {
      if (this.submitting) return
      this.submitting = true
      const token = getToken()
      if (!token) { this.submitting = false; this.$router.push('/account'); return }
      if (!this.customerName.trim()) { this.showToast('Введите имя'); this.submitting = false; return }
      if (!this.customerPhone.trim()) { this.showToast('Введите телефон'); this.submitting = false; return }
      if (!this.agreePolicy) { this.showToast('Подтвердите согласие с политикой'); this.submitting = false; return }

      const order = { name: this.customerName, phone: this.customerPhone, address: this.customerAddress, items: this.cart.map(function (item) { return { id: item.id, title: item.title, price: item.price, quantity: item.quantity } }), total: this.totalPrice }
      try {
        const res = await apiFetch('/order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(order) })
        if (!res.ok) { this.showToast('Не удалось оформить заказ. Войдите через Telegram.'); this.submitting = false; return }
        const data = await res.json()
        const id = data.order_id
        this.cart = []
        setCart([])
        this.customerName = ''
        this.customerPhone = ''
        this.customerAddress = ''
        this.agreePolicy = false
        localStorage.setItem('last_order_id', id)
        this.$router.push('/account')
      } catch (e) {
        console.error('Ошибка заказа', e)
        this.showToast('Ошибка соединения')
      } finally { this.submitting = false }
    }
  },
  mounted() {
    this.cart = getCart()
    this.favorites = getFavorites()
    this.unsubscribeCart = subscribeCart((cart) => { this.cart = Array.isArray(cart) ? cart : [] })
    this.unsubscribeFavorites = subscribeFavorites((favorites) => { this.favorites = Array.isArray(favorites) ? favorites : [] })
    window.addEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.addEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    this.fetchProducts()
  },
  beforeUnmount() {
    if (this.unsubscribeCart) this.unsubscribeCart()
    if (this.unsubscribeFavorites) this.unsubscribeFavorites()
    window.removeEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.removeEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    if (this.toastTimer) { clearTimeout(this.toastTimer); this.toastTimer = null }
  }
}
</script>

<style scoped>
.home-page { padding-top: 22px; padding-bottom: 70px; }
.hero { position: relative; overflow: hidden; padding: clamp(22px, 4vw, 42px); background: linear-gradient(145deg, #fffbe7, #ffd8db 60%, #fff3b5); margin-bottom: 26px; border: 2px solid #111; }
.hero-dots { position: absolute; inset: 0; opacity: 0.32; background-image: radial-gradient(circle at 18px 18px, rgba(227,0,11,0.2) 4px, transparent 5px); background-size: 32px 32px; pointer-events: none; }
.hero > * { position: relative; z-index: 1; }
.section-head { display: flex; justify-content: space-between; gap: 10px; align-items: end; margin-bottom: 14px; }
.catalog-layout { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
.filters { padding: 16px; height: fit-content; position: sticky; top: 86px; border: 2px solid #111; }
.filters h3 { margin-bottom: 10px; }
.filters label { display: block; margin-bottom: 10px; font-size: 14px; }
.catalog-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.loading { padding: 18px; }
.cart-panel, .order-panel, .contacts { margin-top: 22px; padding: 18px; border: 2px solid #111; }
.cart-row { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #efefef; padding: 10px 0; }
.cart-actions { display: flex; gap: 6px; }
.cart-total { margin-top: 14px; font-size: 18px; }
.order-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.wide { grid-column: 1 / -1; }
.policy { margin-top: 10px; display: inline-flex; align-items: center; gap: 8px; }
.policy input { width: auto; }
.desktop-order-btn { margin-top: 14px; min-width: 220px; }
.fixed-order-btn { position: fixed; left: 12px; right: 12px; bottom: 10px; z-index: 60; box-shadow: var(--shadow); display: none; }
.faq { margin-top: 28px; }
.faq-list { display: grid; gap: 10px; }
.faq-item { padding: 14px; border: 2px solid #111; }
.faq-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; background: transparent; border: 0; padding: 0; font-weight: 600; text-align: left; box-shadow: none; }
.contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.tg-link { display: inline-flex; }
.footer { padding: 28px 0 12px; text-align: center; }
.toast { position: fixed; right: 14px; bottom: 18px; background: #111; color: #fff; padding: 10px 14px; border-radius: 12px; z-index: 100; box-shadow: var(--shadow); }
.drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 180; display: flex; justify-content: flex-end; }
.drawer { width: min(420px, 100%); height: 100%; background: #fff; border-left: 2px solid #111; padding: 16px; overflow: auto; }
.drawer-item { border: 1px solid #efefef; border-radius: 12px; padding: 10px; margin-top: 10px; }
.drawer-actions { display: flex; gap: 8px; margin-top: 8px; }
@media (max-width: 980px) { .catalog-layout { grid-template-columns: 1fr; } .filters { position: static; } .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 700px) { .section-head { flex-direction: column; align-items: start; } .catalog-grid { grid-template-columns: 1fr; } .contact-grid, .order-grid { grid-template-columns: 1fr; } .cart-row { flex-direction: column; } .desktop-order-btn { display: none; } .fixed-order-btn { display: block; } }
</style>
