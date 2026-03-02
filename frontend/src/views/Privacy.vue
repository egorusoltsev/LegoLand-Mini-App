<template>
  <div class="container legal-page">
    <article class="card legal-card">
      <button class="btn btnSecondary" type="button" @click="goBack">Назад</button>
      <div class="legal-nav">
        <button class="btn btnSecondary" type="button" disabled>Политика конфиденциальности</button>
        <button class="btn btnSecondary" type="button" @click="goOffer">Публичная оферта</button>
      </div>
      <h1>Политика конфиденциальности</h1>
      <p class="muted">Настоящая политика описывает, какие данные мы обрабатываем в Mini App и для чего.</p>

      <h2>Какие данные мы собираем</h2>
      <ul>
        <li>имя и контактный телефон;</li>
        <li>адрес доставки (если указывается при оформлении);</li>
        <li>Telegram user id и публичные данные профиля (если доступны);</li>
        <li>данные заказа: состав корзины, сумма, комментарии и статус.</li>
      </ul>

      <h2>Цели обработки</h2>
      <ul>
        <li>оформление и обработка заказа;</li>
        <li>связь с пользователем по вопросам заказа;</li>
        <li>организация доставки и возвратов.</li>
      </ul>

      <h2>Правовое основание</h2>
      <p>Обработка данных осуществляется на основании согласия пользователя, которое подтверждается при оформлении заказа.</p>

      <h2>Срок хранения</h2>
      <p>Данные хранятся до достижения целей обработки. После этого данные удаляются по запросу пользователя, если иное не требуется по закону.</p>

      <h2>Передача третьим лицам</h2>
      <p>По необходимости данные могут передаваться сервисам доставки и платёжным сервисам (при подключении онлайн-оплаты в будущем) только в объёме, необходимом для исполнения заказа.</p>

      <h2>Контакты</h2>
      <p>Telegram: <a href="https://t.me/egor2815" target="_blank" rel="noopener noreferrer">@egor2815</a></p>
      <p>Email: <a href="mailto:egorusolcev498@gmail.com">egorusolcev498@gmail.com</a></p>
      <p>ИНН: 253911587570</p>
    </article>
  </div>
</template>

<script>
export default {
  name: 'PrivacyView',
  methods: {
    goBack() {
      this.$router.back()
    },
    goOffer() {
      if (this.$route.path === '/offer') return
      this.$router.replace('/offer')
    }
  }
}
</script>

<style scoped>
.legal-page {
  padding-top: 20px;
  padding-bottom: 20px;
}
.legal-card {
  max-width: 900px;
  margin: 0 auto;
  padding: clamp(16px, 3vw, 28px);
}
.legal-nav {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
h1 {
  margin-top: 14px;
  margin-bottom: 10px;
}
h2 {
  margin-top: 18px;
  margin-bottom: 8px;
}
ul {
  margin: 0;
  padding-left: 20px;
}
a {
  color: var(--primary);
  text-decoration: underline;
}
</style>
