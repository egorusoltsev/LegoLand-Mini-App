<template>
  <div class="card">
    <img :src="image" alt="LEGO" class="product-image"/>

    <h3 class="title">{{ title }}</h3>
    <p class="price">{{ price }} ₽</p>

    <button class="btn" @click="buy">
      Купить
    </button>
  </div>
</template>

<script>
export default {
  name: 'ProductCard',
  props: {
    title: {
      type: String,
      required: true
    },
    price: {
      type: Number,
      required: true
    },
    image: {
      type: String,
      required: true
    }
  },
  methods: {
    buy() {
        this.$emit('buy')
    }
  }
}
</script>

<style scoped>
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  width: 200px;
}

.image {
  width: 100%;
  height: 140px;
  object-fit: contain;
  margin-bottom: 8px;
}

.title {
  font-size: 16px;
  margin-bottom: 6px;
}

.price {
  font-weight: bold;
  margin-bottom: 10px;
}

.btn {
  width: 100%;
  padding: 8px;
  border: none;
  background: black;
  color: white;
  cursor: pointer;
}

.product-image {
  width: 200px;
  height: 200px;
  object-fit: contain;
}

</style>