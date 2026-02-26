<template>
  <span class="logo">LEGO<span class="logo-land">land</span></span>
</template>

<script>
export default {
  name: 'LogoText'
}
</script>

<style scoped>
.logo {
  font-weight: 900;
  letter-spacing: -0.03em;
  color: var(--brand-red);
}

.logo-land {
  color: var(--text);
}
</style>
