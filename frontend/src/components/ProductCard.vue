<template>
  <div class="card">

    <div class="image-wrapper">
      <img :src="image" alt="LEGO" class="product-image"/>
      <button class="favorite">♡</button>
    </div>

    <div class="card-body">
      <h3>{{ product.title }}</h3>
      <p>{{ formatPrice(product.price) }} ₽</p>

      <div class="buttons">
        <button class="btn secondary">
          Подробнее
        </button>

        <button class="btn primary" @click="buy">
          В корзину
        </button>
      </div>
    </div>

  </div>
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
  methods: {
    buy() {
      this.$emit('buy', this.product)
    },
    formatPrice(value) {
      return new Intl.NumberFormat('ru-RU').format(value)
    }
  }
}
</script>

<style scoped>

.card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}

.image-wrapper {
  position: relative;
  background: #f5f5f5;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.product-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.favorite {
  position: absolute;
  top: 12px;
  right: 12px;
  border: none;
  background: white;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 18px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.card-body {
  padding: 20px;
}

.title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  min-height: 48px;
}

.price {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
}

.buttons {
  display: flex;
  gap: 10px;
}

.btn {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.primary {
  background: #D62828;
  color: white;
  border: none;
}

.primary:hover {
  background: #b71c1c;
}

.secondary {
  background: white;
  border: 1px solid #D62828;
  color: #D62828;
}

.secondary:hover {
  background: #fbe9e7;
}

</style>