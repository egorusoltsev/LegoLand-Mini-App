<template>
  <div>
    <Header />
    <main class="container home-page">
      <section class="hero card section">
        <p class="chip">Оригинальные LEGO наборы</p>
        <h1><LogoText /> — оригинальные наборы LEGO по ценам ниже рынка</h1>
        <p class="muted">Подборка редких и популярных наборов с быстрой доставкой по РФ.</p>
        <button class="btn btnPrimary" type="button" @click="scrollToCatalog">Перейти в каталог</button>
        <div class="hero-shape" aria-hidden="true"></div>
      </section>

      <section id="catalog" class="section">
        <div class="section-head">
          <h2 class="sectionTitle">Каталог</h2>
          <p class="muted">Найдено: {{ filteredProducts.length }} товаров</p>
        </div>

        <div class="catalog-layout">
          <aside class="filters card">
            <h3>Фильтры</h3>
            <label>Категория<select v-model="selectedCategory" class="input"><option value="all">Все</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option></select></label>
            <label>Цена от<input v-model="minPrice" class="input" type="number" min="0" placeholder="0" /></label>
            <label>Цена до<input v-model="maxPrice" class="input" type="number" min="0" placeholder="150000" /></label>
            <label>Сортировка<select v-model="sortBy" class="input"><option value="popular">По популярности</option><option value="price-asc">Сначала дешевле</option><option value="price-desc">Сначала дороже</option></select></label>
          </aside>

          <div>
            <div v-if="loading" class="card loading">Загрузка товаров...</div>
            <div v-else class="catalog-grid">
              <ProductCard v-for="product in filteredProducts" :key="product.id" :product="product" :favorite="isFavorite(product.id)" @buy="addToCart" @toggle-favorite="toggleFavorite" />
            </div>
          </div>
        </div>
      </section>

      <section class="card cart-panel section" v-if="cart.length" id="cart-section">
        <h2 class="sectionTitle">Корзина</h2>
        <div class="cart-row" v-for="item in cart" :key="item.id">
          <div><strong>{{ item.title }}</strong><p class="muted">{{ formatPrice(item.price) }} ₽ × {{ item.quantity }}</p></div>
          <div class="cart-actions">
            <button type="button" class="btn btnSecondary" @click="decreaseQuantity(item)">−</button>
            <button type="button" class="btn btnSecondary" @click="increaseQuantity(item)">+</button>
            <button type="button" class="btn btnSecondary" @click="removeFromCart(item)">Удалить</button>
          </div>
        </div>
        <p class="cart-total">Итого: <strong>{{ cartItemsTotal }}</strong> шт. на <strong>{{ formatPrice(cartPriceTotal) }} ₽</strong></p>
      </section>

      <section class="card order-panel section" v-if="cart.length" id="checkout-section">
        <h2 class="sectionTitle">Данные для заказа</h2>
        <div class="order-grid">
          <label>Имя<input v-model="customerName" class="input" type="text" placeholder="Иван" /></label>
          <label>Телефон<input v-model="customerPhone" class="input" type="text" placeholder="+7 999 123-45-67" /></label>
          <label class="wide">Адрес (необязательно)<input v-model="customerAddress" class="input" type="text" placeholder="Москва, улица..., дом..." /></label>
        </div>
        <label class="policy"><input v-model="agreePolicy" type="checkbox" /><span>Согласен с <a href="#" @click.prevent>политикой обработки данных</a></span></label>
        <button class="btn btnPrimary desktop-order-btn" type="button" @click="sendOrder">{{ submitting ? 'Оформляем...' : 'Оформить заказ' }}</button>
      </section>

      <section class="faq section">
        <h2 class="sectionTitle">FAQ</h2>
        <div class="faq-list">
          <article v-for="(item, index) in faqItems" :key="item.question" class="card faq-item">
            <button class="faq-toggle" type="button" @click="toggleFaq(index)">{{ item.question }}<span>{{ openFaqIndex === index ? '−' : '+' }}</span></button>
            <p v-if="openFaqIndex === index" class="muted">{{ item.answer }}</p>
          </article>
        </div>
      </section>

      <section class="card contacts section">
        <h2 class="sectionTitle">Связаться с нами</h2>
        <div class="contact-grid"><label>Имя<input v-model="contactName" class="input" type="text" placeholder="Ваше имя" /></label><label>Телефон<input v-model="contactPhone" class="input" type="text" placeholder="+7 900 000-00-00" /></label></div>
        <a class="btn btnPrimary tg-link" :href="telegramContactUrl" target="_blank" rel="noopener noreferrer">Написать в Telegram</a>
      </section>

      <footer class="footer muted">© {{ brandName }} Mini App</footer>
      <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
    </main>

    <div v-if="cartDrawerOpen" class="drawer-overlay" @click="closeDrawers">
      <aside class="drawer" @click.stop>
        <h3>Корзина</h3>
        <p v-if="!cart.length" class="muted">Корзина пока пустая.</p>
        <div v-for="item in cart" :key="item.id" class="drawer-item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.quantity }} × {{ formatPrice(item.price) }} ₽</p>
          <div class="drawer-actions">
            <button class="btn btnSecondary" type="button" @click="decreaseQuantity(item)">−</button>
            <button class="btn btnSecondary" type="button" @click="increaseQuantity(item)">+</button>
            <button class="btn btnSecondary" type="button" @click="removeFromCart(item)">Удалить</button>
          </div>
        </div>
        <p class="drawer-total">Итого: {{ formatPrice(cartPriceTotal) }} ₽</p>
        <button class="btn btnPrimary" type="button" @click="goToCheckout">Перейти к оформлению</button>
      </aside>
    </div>

    <div v-if="favoritesDrawerOpen" class="drawer-overlay" @click="closeDrawers">
      <aside class="drawer" @click.stop>
        <h3>Избранное</h3>
        <p v-if="!favorites.length" class="muted">Пока нет избранных наборов.</p>
        <div v-for="product in favorites" :key="product.id" class="drawer-item">
          <strong>{{ product.title }}</strong>
          <p>{{ formatPrice(product.price) }} ₽</p>
          <div class="drawer-actions"><button class="btn btnPrimary" type="button" @click="addToCart(product)">В корзину</button><button class="btn btnSecondary" type="button" @click="toggleFavorite(product)">Убрать</button></div>
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
import { add, clear, dec, inc, loadCart, remove, subscribe as subscribeCart, totalItems, totalPrice } from '../store/cartStore'
import { loadFavorites, subscribe as subscribeFavorites, toggle } from '../store/favoritesStore'

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
      searchQuery: '',
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
      if (this.selectedCategory !== 'all') result = result.filter((product) => String(product.category || product.series || '').toLowerCase().includes(this.selectedCategory.toLowerCase()))
      if (!isNaN(min) && min > 0) result = result.filter(function (product) { return Number(product.price) >= min })
      if (!isNaN(max) && max > 0) result = result.filter(function (product) { return Number(product.price) <= max })
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.trim().toLowerCase()
        result = result.filter(function (product) { return String(product.title || '').toLowerCase().includes(query) })
      }
      if (this.sortBy === 'price-asc') result.sort(function (a, b) { return Number(a.price) - Number(b.price) })
      if (this.sortBy === 'price-desc') result.sort(function (a, b) { return Number(b.price) - Number(a.price) })
      return result
    },
    cartItemsTotal() { return totalItems(this.cart) },
    cartPriceTotal() { return totalPrice(this.cart) }
  },
  methods: {
    formatPrice(value) { return new Intl.NumberFormat('ru-RU').format(value) },
    isFavorite(productId) {
      return this.favorites.some(function (item) { return item.id === productId })
    },
    toggleFavorite(product) {
      this.favorites = toggle(product)
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
    goToCheckout() {
      this.closeDrawers()
      const section = document.getElementById('checkout-section')
      if (section && section.scrollIntoView) section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    addToCart(product) {
      this.cart = add(product)
      this.showToast('Добавлено в корзину')
    },
    increaseQuantity(product) { this.cart = inc(product.id) },
    decreaseQuantity(product) { this.cart = dec(product.id) },
    removeFromCart(product) { this.cart = remove(product.id) },
    onOpenCart() { this.cartDrawerOpen = true; this.favoritesDrawerOpen = false },
    onOpenFavorites() { this.favoritesDrawerOpen = true; this.cartDrawerOpen = false },
    onSearch(event) { this.searchQuery = event && event.detail ? String(event.detail) : '' },
    closeDrawers() { this.cartDrawerOpen = false; this.favoritesDrawerOpen = false },
    async fetchProducts() {
      try {
        const res = await apiFetch('/products')
        const data = await res.json()
        this.products = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('Ошибка загрузки товаров', error)
      } finally {
        this.loading = false
        this.submitting = false
      }
    },
    getImageUrl(image) {
      const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
      if (typeof image === 'string' && image && (image.startsWith('http://') || image.startsWith('https://'))) return image
      if (typeof image === 'string' && image) return API_URL + '/images/' + image
      return ''
    },
    async sendOrder() {
      if (this.submitting) return
      this.submitting = true
      const token = getToken()
      if (!token) { this.submitting = false; this.$router.push('/account'); return }
      if (!this.customerName.trim()) { this.showToast('Введите имя'); this.submitting = false; return }
      if (!this.customerPhone.trim()) { this.showToast('Введите телефон'); this.submitting = false; return }
      if (!this.agreePolicy) { this.showToast('Подтвердите согласие с политикой'); this.submitting = false; return }

      const order = { name: this.customerName, phone: this.customerPhone, address: this.customerAddress, items: this.cart.map(function (item) { return { id: item.id, title: item.title, price: item.price, quantity: item.quantity } }), total: this.cartPriceTotal }
      try {
        const res = await apiFetch('/order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(order) })
        if (!res.ok) { this.showToast('Не удалось оформить заказ. Войдите через Telegram.'); this.submitting = false; return }
        const data = await res.json()
        localStorage.setItem('last_order_id', data.order_id)
        this.cart = clear()
        this.customerName = ''
        this.customerPhone = ''
        this.customerAddress = ''
        this.agreePolicy = false
        this.$router.push('/account')
      } catch (error) {
        console.error('Ошибка заказа', error)
        this.showToast('Ошибка соединения')
      } finally { this.submitting = false }
    }
  },
  mounted() {
    this.cart = loadCart()
    this.favorites = loadFavorites()
    this.unsubscribeCart = subscribeCart((cart) => { this.cart = Array.isArray(cart) ? cart : [] })
    this.unsubscribeFavorites = subscribeFavorites((favorites) => { this.favorites = Array.isArray(favorites) ? favorites : [] })
    window.addEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.addEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    window.addEventListener(UI_EVENTS.SET_SEARCH, this.onSearch)
    this.fetchProducts()
  },
  beforeUnmount() {
    if (this.unsubscribeCart) this.unsubscribeCart()
    if (this.unsubscribeFavorites) this.unsubscribeFavorites()
    window.removeEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.removeEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    window.removeEventListener(UI_EVENTS.SET_SEARCH, this.onSearch)
    if (this.toastTimer) { clearTimeout(this.toastTimer); this.toastTimer = null }
  }
}
</script>

<style scoped>
.home-page { padding-top: 22px; padding-bottom: 40px; }
.hero { padding: clamp(24px, 4vw, 44px); position: relative; overflow: hidden; }
.hero-shape { position: absolute; right: -80px; top: -40px; width: 260px; height: 180px; background: #fee2e2; border-radius: 24px; transform: rotate(-12deg); }
.hero > * { position: relative; z-index: 1; }
.section-head { display: flex; justify-content: space-between; gap: 12px; align-items: end; margin-bottom: 14px; }
.catalog-layout { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
.filters { padding: 16px; height: fit-content; position: sticky; top: 88px; }
.filters label { display: block; margin-top: 10px; font-size: 14px; }
.catalog-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.loading { padding: 18px; }
.cart-panel, .order-panel, .contacts { padding: 18px; }
.cart-row { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--border); padding: 10px 0; }
.cart-actions, .drawer-actions { display: flex; gap: 6px; }
.cart-total { margin-top: 12px; font-size: 18px; }
.order-grid, .contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.wide { grid-column: 1 / -1; }
.policy { margin-top: 10px; display: inline-flex; align-items: center; gap: 8px; }
.policy input { width: auto; }
.desktop-order-btn { margin-top: 14px; min-width: 220px; }
.faq-list { display: grid; gap: 10px; }
.faq-item { padding: 14px; }
.faq-toggle { width: 100%; border: 0; background: transparent; padding: 0; display: flex; justify-content: space-between; align-items: center; font-weight: 600; text-align: left; }
.tg-link { display: inline-flex; }
.footer { padding: 28px 0 12px; text-align: center; }
.toast { position: fixed; right: 14px; bottom: 18px; background: var(--text); color: #fff; padding: 10px 14px; border-radius: 12px; z-index: 100; box-shadow: var(--shadow); }
.drawer-overlay { position: fixed; inset: 0; background: rgba(17, 24, 39, 0.4); z-index: 180; display: flex; justify-content: flex-end; }
.drawer { width: min(420px, 100%); height: 100%; background: #fff; border-left: 1px solid var(--border); padding: 16px; overflow: auto; }
.drawer-item { border: 1px solid var(--border); border-radius: 12px; padding: 10px; margin-top: 10px; }
.drawer-total { margin-top: 12px; font-weight: 700; }
@media (max-width: 980px) { .catalog-layout { grid-template-columns: 1fr; } .filters { position: static; } .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 700px) { .section-head { flex-direction: column; align-items: start; } .catalog-grid { grid-template-columns: 1fr; } .contact-grid, .order-grid { grid-template-columns: 1fr; } .cart-row { flex-direction: column; } }
</style>
