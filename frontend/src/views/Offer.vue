<template>
  <div class="container legal-page">
    <article class="card legal-card">
      <button class="btn btnSecondary" type="button" @click="goBack">Назад</button>
      <div class="legal-nav">
        <button class="btn btnSecondary" type="button" @click="goPrivacy">Политика конфиденциальности</button>
        <button class="btn btnSecondary" type="button" disabled>Публичная оферта</button>
      </div>
      <h1>Публичная оферта</h1>
      <p class="muted">Данный документ определяет порядок оформления и исполнения заказов через Mini App.</p>

      <h2>1. Предмет договора</h2>
      <p>Продавец обязуется передать товар, выбранный покупателем в каталоге, а покупатель обязуется принять и оплатить заказ на согласованных условиях.</p>

      <h2>2. Оформление заказа</h2>
      <p>Заказ оформляется через интерфейс Mini App. После отправки заказа менеджер связывается с покупателем для подтверждения деталей.</p>

      <h2>3. Оплата</h2>
      <p>Оплата может производиться по согласованным реквизитам. Онлайн-оплата может быть добавлена позднее как отдельный способ оплаты.</p>

      <h2>4. Доставка</h2>
      <p>Способы и сроки доставки уточняются при оформлении заказа и подтверждаются отдельно по каждому заказу.</p>

      <h2>Доставка и получение</h2>
      <ul>
        <li>Доставка осуществляется по всей территории РФ.</li>
        <li>Способ доставки согласовывается с покупателем после оформления заказа.</li>
        <li>После оформления заказа менеджер связывается с покупателем в Telegram (@egor2815) в течение 1–2 часов.</li>
        <li>Детали доставки, сроки и способ получения согласовываются индивидуально.</li>
      </ul>

      <h2>5. Возврат</h2>
      <p>Возвраты и обращения по качеству рассматриваются индивидуально в рамках действующего законодательства и согласованных условий заказа.</p>

      <h2>6. Ответственность</h2>
      <p>Стороны несут ответственность за неисполнение или ненадлежащее исполнение обязательств согласно законодательству РФ.</p>

      <h2>7. Контакты</h2>
      <p>Telegram: <a href="https://t.me/egor2815" target="_blank" rel="noopener noreferrer">@egor2815</a></p>
      <p>Email: <a href="mailto:egorusolcev498@gmail.com">egorusolcev498@gmail.com</a></p>
      <p>ИНН: 253911587570</p>
    </article>
  </div>
</template>

<script>
export default {
  name: 'OfferView',
  methods: {
    goBack() {
      this.$router.back()
    },
    goPrivacy() {
      if (this.$route.path === '/privacy') return
      this.$router.replace('/privacy')
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
