<template>
  <div>
    <router-view />
    <SiteFooter />
  </div>
</template>

<script>
import SiteFooter from './components/Footer.vue'

export default {
  name: 'App',
  components: { SiteFooter }
}
</script>
