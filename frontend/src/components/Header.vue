<template>
  <header class="site-header">
    <div class="container header-row">
      <router-link to="/" class="brand" aria-label="LegoLand">
        <LogoText />
      </router-link>

      <nav class="header-actions">
        <button class="icon-btn" type="button" aria-label="Поиск" @click="toggleSearchModal">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" /><line x1="16.65" y1="16.65" x2="21" y2="21" /></svg>
        </button>
        <button class="icon-btn" type="button" aria-label="Аккаунт" @click="goToAccount">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" /><path d="M4 20c1.7-3.3 4.4-5 8-5s6.3 1.7 8 5" /></svg>
        </button>
        <button class="icon-btn" type="button" aria-label="Избранное" @click="openFavorites">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.35-9.33-8.03C.66 9.8 2.06 5.7 5.7 4.62A5.22 5.22 0 0 1 12 7a5.22 5.22 0 0 1 6.3-2.38c3.64 1.08 5.04 5.18 3.03 8.35C19 16.65 12 21 12 21z"/></svg>
          <span v-if="favoritesCount > 0" class="badge action-badge">{{ favoritesCount }}</span>
        </button>
        <button class="icon-btn cart" type="button" aria-label="Корзина" @click="openCart">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="20" r="1.5" /><circle cx="18" cy="20" r="1.5" /><path d="M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h8.9a2 2 0 0 0 2-1.5l1.4-6.3H7.1" /></svg>
          <span v-if="cartCount > 0" class="badge action-badge">{{ cartCount }}</span>
        </button>
      </nav>
    </div>

    <div v-if="searchModalOpen" class="search-modal-overlay" @click="toggleSearchModal">
      <div class="search-modal" @click.stop>
        <h3>Поиск скоро</h3>
        <input ref="searchInput" type="text" placeholder="Скоро добавим умный поиск" />
        <button class="btn-secondary" type="button" @click="toggleSearchModal">Закрыть</button>
      </div>
    </div>
  </header>
</template>

<script>
import LogoText from './LogoText.vue'
import { UI_EVENTS } from '../constants'
import { getCartCount, subscribeCart } from '../store/cart'
import { getFavoritesCount, subscribeFavorites } from '../store/favorites'

export default {
  name: 'Header',
  components: { LogoText },
  data() {
    return {
      cartCount: 0,
      favoritesCount: 0,
      unsubscribeCart: null,
      unsubscribeFavorites: null,
      searchModalOpen: false
    }
  },
  mounted() {
    this.cartCount = getCartCount()
    this.favoritesCount = getFavoritesCount()
    this.unsubscribeCart = subscribeCart(this.onCartUpdate)
    this.unsubscribeFavorites = subscribeFavorites(this.onFavoritesUpdate)
  },
  beforeUnmount() {
    if (this.unsubscribeCart) this.unsubscribeCart()
    if (this.unsubscribeFavorites) this.unsubscribeFavorites()
  },
  methods: {
    onCartUpdate(cart) {
      const list = Array.isArray(cart) ? cart : []
      this.cartCount = list.reduce(function (sum, item) {
        return sum + Number(item && item.quantity ? item.quantity : 0)
      }, 0)
    },
    onFavoritesUpdate(favorites) {
      const list = Array.isArray(favorites) ? favorites : []
      this.favoritesCount = list.length
    },
    goToAccount() {
      this.$router.push('/account')
    },
    openCart() {
      window.dispatchEvent(new CustomEvent(UI_EVENTS.OPEN_CART))
    },
    openFavorites() {
      window.dispatchEvent(new CustomEvent(UI_EVENTS.OPEN_FAVORITES))
    },
    toggleSearchModal() {
      this.searchModalOpen = !this.searchModalOpen
      if (this.searchModalOpen) {
        this.$nextTick(function () {
          if (this.$refs.searchInput && this.$refs.searchInput.focus) {
            this.$refs.searchInput.focus()
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.site-header { position: sticky; top: 0; z-index: 50; background: rgba(250, 250, 250, 0.92); border-bottom: 2px solid #f3d8da; backdrop-filter: blur(6px); }
.header-row { height: 70px; display: flex; align-items: center; justify-content: space-between; }
.brand { font-size: 32px; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.icon-btn { width: 42px; height: 42px; border-radius: 14px; border: 2px solid #111; background: var(--card); display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 4px 0 #111; position: relative; padding: 0; }
.icon-btn svg { width: 20px; height: 20px; stroke: #111; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.icon-btn:active { transform: translateY(2px); box-shadow: 0 2px 0 #111; }
.action-badge { position: absolute; top: -7px; right: -7px; }
.search-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 150; padding: 16px; }
.search-modal { width: min(430px, 100%); background: var(--card); border: 2px solid #111; border-radius: var(--radius); padding: 18px; box-shadow: var(--shadow-hard); }
.search-modal h3 { margin-bottom: 10px; }
.search-modal input { margin-bottom: 12px; }
@media (max-width: 640px) { .header-row { height: 62px; } .brand { font-size: 24px; } .header-actions { gap: 6px; } .icon-btn { width: 36px; height: 36px; border-radius: 12px; } .icon-btn svg { width: 18px; height: 18px; } }
</style>
