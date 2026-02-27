<template>
  <div>
    <Header />
    <main class="container home-page">
      <section class="hero card section">
        <p class="chip">Оригинальные LEGO наборы</p>
        <h1><LogoText /> — оригинальные наборы LEGO по ценам ниже рынка</h1>
        <p class="muted">Подборка редких и популярных наборов с быстрой доставкой по РФ.</p>
        <button class="btn btnPrimary hero-cta" type="button" @click="scrollToCatalog">Перейти в каталог</button>
        <div class="hero-shape" aria-hidden="true"></div>
      </section>

      <section class="strip section card" aria-label="Популярные товары" v-if="preparedProducts.length">
        <div class="strip-track">
          <article class="strip-item" v-for="(product, index) in stripProducts" :key="product.id + '-' + index">
            <img v-if="product.image" :src="product.image" :alt="product.title" loading="lazy" />
            <span>{{ product.title }}</span>
          </article>
        </div>
      </section>

      <section id="catalog" class="section">
        <div class="section-head">
          <h2 class="sectionTitle">Каталог</h2>
          <p class="muted">Найдено: {{ filteredProducts.length }} товаров</p>
        </div>

        <div v-if="loadError" class="card error-card">
          <strong>Не удалось загрузить каталог</strong>
          <p class="muted">{{ loadError }}</p>
        </div>

        <div v-if="!loading && !filteredProducts.length" class="card loading">По вашему запросу ничего не найдено.</div>

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

      <footer class="footer muted">© {{ brandName }} Mini App</footer>
      <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
    </main>

    <div v-if="cartDrawerOpen" class="drawer-overlay" @click="closeOverlay('cart')">
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
      </aside>
    </div>

    <div v-if="favoritesDrawerOpen" class="drawer-overlay" @click="closeOverlay('fav')">
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
import { API_URL, apiFetch } from '../api'
import { BRAND_NAME, UI_EVENTS } from '../constants'
import { add, dec, inc, loadCart, remove, subscribe as subscribeCart, totalPrice } from '../store/cartStore'
import { loadFavorites, subscribe as subscribeFavorites, toggle } from '../store/favoritesStore'

function normalizeText(input) {
  return String(input || '')
    .toLowerCase()
    .replace(/ё/g, 'е')
    .replace(/[^a-zа-я0-9\s-]/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

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
      selectedCategory: 'all',
      minPrice: '',
      maxPrice: '',
      sortBy: 'popular',
      searchQuery: '',
      loadError: '',
      toastMessage: '',
      toastTimer: null,
      unsubscribeCart: null,
      unsubscribeFavorites: null
    }
  },
  computed: {
    categories() { return ['Star Wars', 'Technic', 'City', 'Icons'] },
    preparedProducts() { return this.products.map((product) => ({ ...product, image: this.getImageUrl(product.image) })) },
    stripProducts() { return this.preparedProducts.concat(this.preparedProducts) },
    filteredProducts() {
      let result = this.preparedProducts.slice()
      const min = Number(this.minPrice)
      const max = Number(this.maxPrice)
      if (this.selectedCategory !== 'all') result = result.filter((product) => String(product.category || product.series || '').toLowerCase().includes(this.selectedCategory.toLowerCase()))
      if (!isNaN(min) && min > 0) result = result.filter(function (product) { return Number(product.price) >= min })
      if (!isNaN(max) && max > 0) result = result.filter(function (product) { return Number(product.price) <= max })

      const query = normalizeText(this.searchQuery)
      if (query) {
        const parts = query.split(' ').filter(function (item) { return item.length > 0 })
        result = result.filter(function (product) {
          const haystack = normalizeText([product.title, product.category, product.set_number, product.id].join(' '))
          if (!parts.length) return true
          if (query.length <= 2) return haystack.indexOf(query) !== -1
          return parts.every(function (part) { return haystack.indexOf(part) !== -1 })
        })
      }

      if (this.sortBy === 'price-asc') result.sort(function (a, b) { return Number(a.price) - Number(b.price) })
      if (this.sortBy === 'price-desc') result.sort(function (a, b) { return Number(b.price) - Number(a.price) })
      return result
    },
    cartPriceTotal() { return totalPrice(this.cart) }
  },
  watch: {
    '$route.query': {
      deep: true,
      handler() {
        this.syncDrawersWithRoute()
      }
    }
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
      this.toastTimer = setTimeout(() => { this.toastMessage = '' }, 1800)
    },
    scrollToCatalog() {
      const section = document.getElementById('catalog')
      if (section && section.scrollIntoView) section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    addToCart(product) {
      this.cart = add(product)
      this.showToast('Добавлено в корзину')
    },
    increaseQuantity(product) { this.cart = inc(product.id) },
    decreaseQuantity(product) { this.cart = dec(product.id) },
    removeFromCart(product) { this.cart = remove(product.id) },
    onOpenCart() {
      this.updateOverlayQuery('cart', true)
    },
    onOpenFavorites() {
      this.updateOverlayQuery('fav', true)
    },
    onOpenSearch() {
      this.updateOverlayQuery('search', true)
    },
    onCloseSearch() {
      this.updateOverlayQuery('search', false, true)
    },
    onSearch(event) { this.searchQuery = event && event.detail ? String(event.detail) : '' },
    closeOverlay(type) {
      this.updateOverlayQuery(type, false, true)
    },
    syncDrawersWithRoute() {
      const query = this.$route.query || {}
      this.cartDrawerOpen = query.cart === '1'
      this.favoritesDrawerOpen = query.fav === '1'
    },
    updateOverlayQuery(type, open, replace) {
      const nextQuery = { ...this.$route.query }
      const key = type
      if (open) {
        if (key === 'cart') delete nextQuery.fav
        if (key === 'fav') delete nextQuery.cart
        nextQuery[key] = '1'
      } else {
        delete nextQuery[key]
      }
      const hasDiff = JSON.stringify(nextQuery) !== JSON.stringify(this.$route.query || {})
      if (!hasDiff) return
      if (replace) {
        this.$router.replace({ query: nextQuery })
      } else {
        this.$router.push({ query: nextQuery })
      }
    },
    async fetchProducts() {
      this.loadError = ''
      try {
        const endpoint = '/products'
        const res = await apiFetch(endpoint)
        if (!res.ok) {
          const responseText = await res.text()
          console.error('Ошибка загрузки товаров', {
            apiUrl: API_URL,
            endpoint,
            status: res.status,
            responseText
          })
          this.loadError = 'Код: ' + res.status
          this.products = []
          return
        }
        const data = await res.json()
        this.products = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('Ошибка загрузки товаров', {
          apiUrl: API_URL,
          endpoint: '/products',
          status: 'network_error',
          responseText: error && error.message ? error.message : 'unknown'
        })
        this.products = []
        this.loadError = 'Сетевая ошибка при загрузке каталога.'
      } finally {
        this.loading = false
      }
    },
    getImageUrl(image) {
      if (typeof image === 'string' && image && (image.startsWith('http://') || image.startsWith('https://'))) return image
      if (typeof image === 'string' && image) return API_URL + '/images/' + image
      return ''
    }
  },
  mounted() {
    this.cart = loadCart()
    this.favorites = loadFavorites()
    this.unsubscribeCart = subscribeCart((cart) => { this.cart = Array.isArray(cart) ? cart : [] })
    this.unsubscribeFavorites = subscribeFavorites((favorites) => { this.favorites = Array.isArray(favorites) ? favorites : [] })
    window.addEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.addEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    window.addEventListener(UI_EVENTS.OPEN_SEARCH, this.onOpenSearch)
    window.addEventListener(UI_EVENTS.CLOSE_SEARCH, this.onCloseSearch)
    window.addEventListener(UI_EVENTS.SET_SEARCH, this.onSearch)
    this.syncDrawersWithRoute()
    this.fetchProducts()
  },
  beforeUnmount() {
    if (this.unsubscribeCart) this.unsubscribeCart()
    if (this.unsubscribeFavorites) this.unsubscribeFavorites()
    window.removeEventListener(UI_EVENTS.OPEN_CART, this.onOpenCart)
    window.removeEventListener(UI_EVENTS.OPEN_FAVORITES, this.onOpenFavorites)
    window.removeEventListener(UI_EVENTS.OPEN_SEARCH, this.onOpenSearch)
    window.removeEventListener(UI_EVENTS.CLOSE_SEARCH, this.onCloseSearch)
    window.removeEventListener(UI_EVENTS.SET_SEARCH, this.onSearch)
    if (this.toastTimer) { clearTimeout(this.toastTimer); this.toastTimer = null }
  }
}
</script>

<style scoped>
.home-page { padding-top: 22px; padding-bottom: 40px; }
.hero { padding: clamp(24px, 4vw, 44px); position: relative; overflow: hidden; }
.hero-shape { pointer-events: none; position: absolute; right: -40px; top: -24px; width: 180px; height: 120px; background: #fee2e2; border-radius: 24px; transform: rotate(-12deg); z-index: 0; }
.hero > * { position: relative; z-index: 1; }
.hero-cta { z-index: 2; position: relative; }
.strip { overflow: hidden; padding: 10px 0; }
.strip-track { display: flex; gap: 12px; width: max-content; padding: 0 12px; animation: run-strip 40s linear infinite; }
.strip-item { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--border); border-radius: 12px; background: #fff; padding: 6px 10px; min-width: 190px; }
.strip-item img { width: 36px; height: 36px; border-radius: 8px; object-fit: cover; }
.strip:hover .strip-track { animation-play-state: paused; }
.section-head { display: flex; justify-content: space-between; gap: 12px; align-items: end; margin-bottom: 14px; }
.catalog-layout { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
.filters { padding: 16px; height: fit-content; position: sticky; top: 88px; }
.filters label { display: block; margin-top: 10px; font-size: 14px; }
.catalog-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.loading { padding: 18px; }
.error-card { padding: 14px; margin-bottom: 12px; border-color: #fecaca; }
.footer { padding: 28px 0 12px; text-align: center; }
.toast { position: fixed; right: 14px; bottom: 18px; background: var(--text); color: #fff; padding: 10px 14px; border-radius: 12px; z-index: 100; box-shadow: var(--shadow); }
.drawer-overlay { position: fixed; inset: 0; background: rgba(17, 24, 39, 0.4); z-index: 180; display: flex; justify-content: flex-end; }
.drawer { width: min(420px, 100%); height: 100%; background: #fff; border-left: 1px solid var(--border); padding: 16px; overflow: auto; }
.drawer-item { border: 1px solid var(--border); border-radius: 12px; padding: 10px; margin-top: 10px; }
.drawer-actions { display: flex; gap: 6px; }
.drawer-total { margin-top: 12px; font-weight: 700; }
@keyframes run-strip {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
@media (prefers-reduced-motion: reduce) {
  .strip-track { animation: none; }
}
@media (max-width: 980px) {
  .catalog-layout { grid-template-columns: 1fr; }
  .filters { position: static; }
  .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 700px) {
  .hero-shape { width: 110px; height: 72px; right: -34px; top: -16px; }
  .section-head { flex-direction: column; align-items: start; }
  .catalog-grid { grid-template-columns: 1fr; }
}
</style>
