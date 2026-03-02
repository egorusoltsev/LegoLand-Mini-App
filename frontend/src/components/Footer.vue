<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p class="muted">© {{ brandName }} Mini App</p>
      <nav class="footer-links" aria-label="Юридическая информация">
        <router-link to="/privacy">Политика конфиденциальности</router-link>
        <router-link to="/offer">Публичная оферта</router-link>
      </nav>
    </div>
  </footer>
</template>

<script>
import { BRAND_NAME } from '../constants'

export default {
  name: 'SiteFooter',
  data() {
    return {
      brandName: BRAND_NAME
    }
  }
}
</script>

<style scoped>
.site-footer {
  border-top: 1px solid var(--border);
  margin-top: 28px;
  background: var(--surface);
}
.footer-inner {
  padding-top: 16px;
  padding-bottom: 20px;
}
.footer-links {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}
.footer-links a {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>
