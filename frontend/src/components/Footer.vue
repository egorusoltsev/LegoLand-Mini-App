<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p class="muted">© {{ brandName }} Mini App</p>
      <nav class="footer-links" aria-label="Юридическая информация">
        <a href="#" @click.prevent="openLegal('/privacy')">Политика конфиденциальности</a>
        <a href="#" @click.prevent="openLegal('/offer')">Публичная оферта</a>
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
  },
  methods: {
    openLegal(path) {
      if (this.$route.path === path) return
      this.$router.push(path)
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
