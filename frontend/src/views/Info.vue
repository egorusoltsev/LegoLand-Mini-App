<template>
  <div class="container info-page">
    <h2 class="section-title">Информация</h2>
    <div class="card info-card">
      <p><strong>LegoLand</strong> — магазин оригинальных LEGO наборов для коллекции, подарков и личной сборки.</p>
      <p>В каталоге представлены популярные и редкие наборы разных серий, включая Star Wars, Technic, City и Icons.</p>
      <p>Заказ оформляется через корзину: добавьте товары, подтвердите согласие с документами и отправьте заявку.</p>
      <p>После оформления менеджер связывается с вами в Telegram для подтверждения деталей доставки и оплаты.</p>
      <p>Связь: <a href="https://t.me/egor2815" target="_blank" rel="noopener noreferrer">@egor2815</a>.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InfoPage'
}
</script>

<style scoped>
.info-page { padding-top: 22px; padding-bottom: 30px; }
.info-card { padding: 16px; display: grid; gap: 10px; }
.info-card a { color: var(--primary); }
</style>
