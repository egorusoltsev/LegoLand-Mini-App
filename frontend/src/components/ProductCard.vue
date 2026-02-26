<template>
  <article class="product-card">
    <div class="image-wrapper">
      <img :src="product.image" :alt="product.title" class="product-image" />
      <button class="favorite" type="button" aria-label="Избранное">♡</button>
    </div>

    <div class="card-body">
      <h3 class="title">{{ product.title }}</h3>
      <p class="muted specs">{{ productSpecs }}</p>
      <p class="price">{{ formatPrice(product.price) }} ₽</p>

      <div class="buttons">
        <button class="btn-secondary" type="button" @click="openDetails">Подробнее</button>
        <button class="btn-primary" type="button" @click="buy">В корзину</button>
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
        <button class="btn-primary" type="button" @click="buyFromModal">В корзину</button>
      </div>
    </div>
  </article>
</template>

<script>
export default {
  name: 'ProductCard',
  props: {
    product: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showModal: false
    }
  },
  computed: {
    productSpecs() {
      const pieces = this.product && this.product.pieces ? 'Деталей: ' + this.product.pieces : ''
      const series = this.product && this.product.series ? 'Серия: ' + this.product.series : ''
      const sku = this.product && this.product.sku ? 'Артикул: ' + this.product.sku : ''
      const merged = [pieces, series, sku].filter(function (item) {
        return Boolean(item)
      }).join(' • ')
      return merged || 'Оригинальный LEGO набор'
    },
    descriptionText() {
      if (this.product && this.product.description) {
        return this.product.description
      }
      return 'Набор в заводской упаковке LEGO. Отличный вариант для коллекции, подарка или личной сборки.'
    }
  },
  methods: {
    openDetails() {
      this.showModal = true
    },
    closeDetails() {
      this.showModal = false
    },
    buy() {
      this.$emit('buy', this.product)
    },
    buyFromModal() {
      this.buy()
      this.closeDetails()
    },
    formatPrice(value) {
      return new Intl.NumberFormat('ru-RU').format(value)
    }
  }
}
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  transition: 0.25s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.image-wrapper {
  position: relative;
  background: linear-gradient(145deg, #fff8dc, #f6f6f6);
  padding: 16px;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  max-height: 190px;
  object-fit: contain;
}

.favorite {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid #ececec;
  background: #fff;
}

.card-body {
  padding: 16px;
}

.title {
  font-size: 18px;
  margin-bottom: 8px;
  min-height: 50px;
}

.specs {
  min-height: 40px;
  margin: 0 0 12px;
  font-size: 14px;
}

.price {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 12px;
}

.buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 200;
}

.modal-card {
  position: relative;
  width: min(520px, 100%);
  max-height: 90vh;
  overflow: auto;
  background: #fff;
  border-radius: 18px;
  padding: 20px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #ddd;
}

.modal-image {
  width: 100%;
  max-height: 260px;
  object-fit: contain;
  margin-bottom: 12px;
}

.description {
  margin: 10px 0 16px;
}
</style>
