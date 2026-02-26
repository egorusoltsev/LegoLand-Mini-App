<template>
  <span class="logo">Lego<span class="logo-land">Land</span></span>
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
  color: var(--primary);
}

.logo-land {
  color: var(--text);
}
</style>
