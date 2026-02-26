<template>
  <article class="product-card">
    <div class="image-wrapper">
      <img :src="product.image" :alt="product.title" class="product-image" />
      <button class="favorite" :class="{ active: favorite }" type="button" aria-label="Избранное" @click="toggleFavoriteState">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.35-9.33-8.03C.66 9.8 2.06 5.7 5.7 4.62A5.22 5.22 0 0 1 12 7a5.22 5.22 0 0 1 6.3-2.38c3.64 1.08 5.04 5.18 3.03 8.35C19 16.65 12 21 12 21z"/></svg>
      </button>
    </div>

    <div class="card-body">
      <h3 class="title">{{ product.title }}</h3>
      <p class="muted specs">{{ productSpecs }}</p>
      <p class="price">{{ formatPrice(product.price) }} ₽</p>

      <div class="buttons">
        <button class="btn btnSecondary" type="button" @click="openDetails">Подробнее</button>
        <button class="btn btnPrimary" type="button" @click="buy">В корзину</button>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click="closeDetails">
      <div class="modal-card" @click.stop>
        <button class="close-btn" type="button" @click="closeDetails">✕</button>
        <img :src="product.image" :alt="product.title" class="modal-image" />
        <h3>{{ product.title }}</h3>
        <p class="muted">{{ productSpecs }}</p>
        <p class="price">{{ formatPrice(product.price) }} ₽</p>
        <p class="description">{{ descriptionText }}</p>
        <button class="btn btnPrimary" type="button" @click="buyFromModal">В корзину</button>
      </div>
    </div>
  </article>
</template>

<script>
export default {
  name: 'ProductCard',
  props: {
    product: { type: Object, required: true },
    favorite: { type: Boolean, default: false }
  },
  emits: ['buy', 'toggle-favorite'],
  data() {
    return { showModal: false }
  },
  computed: {
    productSpecs() {
      const pieces = this.product && this.product.pieces ? 'Деталей: ' + this.product.pieces : ''
      const series = this.product && this.product.series ? 'Серия: ' + this.product.series : ''
      const sku = this.product && this.product.sku ? 'Артикул: ' + this.product.sku : ''
      const merged = [pieces, series, sku].filter(function (item) { return Boolean(item) }).join(' • ')
      return merged || 'Оригинальный LEGO набор'
    },
    descriptionText() {
      if (this.product && this.product.description) return this.product.description
      return 'Набор в заводской упаковке LEGO. Отличный вариант для коллекции, подарка или личной сборки.'
    }
  },
  methods: {
    openDetails() { this.showModal = true },
    closeDetails() { this.showModal = false },
    buy() { this.$emit('buy', this.product) },
    buyFromModal() { this.buy(); this.closeDetails() },
    toggleFavoriteState() { this.$emit('toggle-favorite', this.product) },
    formatPrice(value) { return new Intl.NumberFormat('ru-RU').format(value) }
  }
}
</script>

<style scoped>
.product-card { background: var(--surface); border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); box-shadow: var(--shadow); transition: transform 0.18s ease, box-shadow 0.18s ease; }
.product-card:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(17, 24, 39, 0.12); }
.image-wrapper { position: relative; background: #f9fafb; padding: 16px; min-height: 220px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid var(--border); }
.product-image { width: 100%; max-height: 190px; object-fit: contain; }
.favorite { position: absolute; top: 10px; right: 10px; width: 36px; height: 36px; border-radius: 50%; border: 1px solid var(--border); background: #fff; display: inline-flex; align-items: center; justify-content: center; }
.favorite svg { width: 18px; height: 18px; stroke: #6b7280; fill: none; stroke-width: 1.8; }
.favorite.active svg { fill: var(--primary); stroke: var(--primary); }
.card-body { padding: 16px; }
.title { font-size: 18px; margin-bottom: 8px; min-height: 50px; }
.specs { min-height: 40px; margin: 0 0 12px; font-size: 14px; }
.price { font-size: 22px; font-weight: 800; margin: 0 0 12px; }
.buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(17, 24, 39, 0.45); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 200; }
.modal-card { position: relative; width: min(520px, 100%); max-height: 90vh; overflow: auto; background: #fff; border-radius: var(--radius); padding: 20px; border: 1px solid var(--border); }
.close-btn { position: absolute; top: 10px; right: 10px; width: 32px; height: 32px; padding: 0; border-radius: 50%; background: #fff; border: 1px solid var(--border); }
.modal-image { width: 100%; max-height: 260px; object-fit: contain; margin-bottom: 12px; }
.description { margin: 10px 0 16px; }
</style>
