<template>
  <div>
    <Header />
    <router-view />
    <SiteFooter />
  </div>
</template>

<script>
import SiteFooter from './components/Footer.vue'
import Header from './components/Header.vue'

export default {
  name: 'App',
  components: { SiteFooter, Header }
}
</script>
