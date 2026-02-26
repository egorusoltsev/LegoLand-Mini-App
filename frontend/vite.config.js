import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  plugins: [
    vue(),
    legacy({
      // Telegram WebView часто отстаёт, поэтому делаем совместимость шире
      targets: [
        'defaults',
        'not IE 11',
        'Android >= 7',
        'iOS >= 12'
      ],
      // добавит нужные полифиллы автоматически
      modernPolyfills: true
    })
  ],
})