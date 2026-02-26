<template>
  <header class="site-header">
    <div class="container header-row">
      <router-link to="/" class="brand">
        LEGO<span>land</span>
      </router-link>

      <nav class="header-actions">
        <button class="icon-btn" type="button" aria-label="Поиск">
          🔎
        </button>
        <router-link class="icon-btn" to="/account" aria-label="Аккаунт">
          👤
        </router-link>
        <button class="icon-btn" type="button" aria-label="Избранное">
          ♡
        </button>
        <button class="icon-btn cart" type="button" aria-label="Корзина">
          🛒
          <span v-if="cartCount > 0" class="badge cart-badge">{{ cartCount }}</span>
        </button>
      </nav>
    </div>
  </header>
</template>

<script>
import { getCartCount, subscribeCart } from '../cartStore'

export default {
  name: 'Header',
  data() {
    return {
      cartCount: 0,
      unsubscribe: null
    }
  },
  mounted() {
    this.cartCount = getCartCount()
    this.unsubscribe = subscribeCart(this.onCartUpdate)
  },
  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe()
      this.unsubscribe = null
    }
  },
  methods: {
    onCartUpdate(cart) {
      const list = Array.isArray(cart) ? cart : []
      this.cartCount = list.reduce(function (sum, item) {
        return sum + Number(item && item.quantity ? item.quantity : 0)
      }, 0)
    }
  }
}
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(245, 245, 245, 0.92);
  border-bottom: 1px solid #ececec;
  backdrop-filter: blur(6px);
}

.header-row {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--primary);
}

.brand span {
  color: var(--text);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #ececec;
  background: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-soft);
  font-size: 18px;
  position: relative;
}

.icon-btn:hover {
  border-color: #d7d7d7;
  transform: translateY(-1px);
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
}

@media (max-width: 640px) {
  .header-row {
    height: 60px;
  }

  .brand {
    font-size: 24px;
  }

  .header-actions {
    gap: 6px;
  }

  .icon-btn {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    font-size: 15px;
  }
}
</style>
