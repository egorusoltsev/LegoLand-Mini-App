<template>
  <header class="site-header">
    <div class="container header-row">
      <router-link to="/" class="brand" aria-label="LegoLand">
        <LogoText />
      </router-link>

      <nav class="header-actions">
        <button class="iconBtn" type="button" aria-label="Поиск" @click="toggleSearchModal">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" /><line x1="16.65" y1="16.65" x2="21" y2="21" /></svg>
        </button>
        <button class="iconBtn" type="button" aria-label="Аккаунт" @click="goToAccount">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" /><path d="M4 20c1.7-3.3 4.4-5 8-5s6.3 1.7 8 5" /></svg>
        </button>
        <button class="iconBtn" type="button" aria-label="Избранное" @click="openFavorites">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.35-9.33-8.03C.66 9.8 2.06 5.7 5.7 4.62A5.22 5.22 0 0 1 12 7a5.22 5.22 0 0 1 6.3-2.38c3.64 1.08 5.04 5.18 3.03 8.35C19 16.65 12 21 12 21z"/></svg>
          <span v-if="favoritesCount > 0" class="badge actionBadge">{{ favoritesCount }}</span>
        </button>
        <button class="iconBtn" type="button" aria-label="Корзина" @click="openCart">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="20" r="1.5" /><circle cx="18" cy="20" r="1.5" /><path d="M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h8.9a2 2 0 0 0 2-1.5l1.4-6.3H7.1" /></svg>
          <span v-if="cartCount > 0" class="badge actionBadge">{{ cartCount }}</span>
        </button>
      </nav>
    </div>

    <div v-if="searchModalOpen" class="search-modal-overlay" @click="toggleSearchModal">
      <div class="search-modal card" @click.stop>
        <h3>Поиск по каталогу</h3>
        <input ref="searchInput" v-model="searchQuery" class="input" type="text" placeholder="Например: Star Wars" @input="emitSearch" />
        <div class="search-actions">
          <button class="btn btnSecondary" type="button" @click="clearSearch">Очистить</button>
          <button class="btn btnPrimary" type="button" @click="toggleSearchModal">Готово</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import LogoText from './LogoText.vue'
import { UI_EVENTS } from '../constants'
import { loadCart, subscribe as subscribeCart, totalItems } from '../store/cartStore'
import { count, loadFavorites, subscribe as subscribeFavorites } from '../store/favoritesStore'

export default {
  name: 'Header',
  components: { LogoText },
  data() {
    return {
      cartCount: 0,
      favoritesCount: 0,
      unsubscribeCart: null,
      unsubscribeFavorites: null,
      searchModalOpen: false,
      searchQuery: ''
    }
  },
  mounted() {
    this.cartCount = totalItems(loadCart())
    this.favoritesCount = count(loadFavorites())
    this.unsubscribeCart = subscribeCart(this.onCartUpdate)
    this.unsubscribeFavorites = subscribeFavorites(this.onFavoritesUpdate)
  },
  beforeUnmount() {
    if (this.unsubscribeCart) this.unsubscribeCart()
    if (this.unsubscribeFavorites) this.unsubscribeFavorites()
  },
  methods: {
    onCartUpdate(cart) {
      this.cartCount = totalItems(cart)
    },
    onFavoritesUpdate(favorites) {
      this.favoritesCount = count(favorites)
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
    emitSearch() {
      window.dispatchEvent(new CustomEvent(UI_EVENTS.SET_SEARCH, { detail: this.searchQuery }))
    },
    clearSearch() {
      this.searchQuery = ''
      this.emitSearch()
    },
    toggleSearchModal() {
      this.searchModalOpen = !this.searchModalOpen
      if (this.searchModalOpen) {
        this.$nextTick(function () {
          if (this.$refs.searchInput && this.$refs.searchInput.focus) this.$refs.searchInput.focus()
        })
      }
    }
  }
}
</script>

<style scoped>
.site-header { position: sticky; top: 0; z-index: 80; background: #ffffff; border-bottom: 1px solid var(--border); }
.header-row { height: 72px; display: flex; align-items: center; justify-content: space-between; }
.brand { font-size: 32px; }
.header-actions { display: flex; gap: 8px; }
.actionBadge { position: absolute; margin-top: -26px; margin-left: 24px; }
.search-modal-overlay { position: fixed; inset: 0; background: rgba(17, 24, 39, 0.35); display: flex; justify-content: center; align-items: flex-start; padding: 88px 16px 16px; z-index: 120; }
.search-modal { width: min(520px, 100%); padding: 18px; }
.search-modal h3 { margin-bottom: 10px; }
.search-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
@media (max-width: 700px) {
  .header-row { height: 64px; }
  .brand { font-size: 24px; }
  .header-actions { gap: 6px; }
}
</style>
