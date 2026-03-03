export const BRAND_NAME = 'LegoLand'

function resolveTelegramUrl() {
  const configured = import.meta.env.VITE_TELEGRAM_CONTACT_URL
  if (typeof configured === 'string' && configured.trim()) {
    return configured.trim()
  }
  return 'https://t.me/your_support'
}

export const TELEGRAM_CONTACT_URL = resolveTelegramUrl()

export const UI_EVENTS = {
  OPEN_CART: 'legoland:open-cart',
  OPEN_FAVORITES: 'legoland:open-favorites',
  OPEN_SEARCH: 'legoland:open-search',
  CLOSE_SEARCH: 'legoland:close-search',
  OPEN_AUTH_CHOOSER: 'legoland:open-auth-chooser',
  SET_SEARCH: 'legoland:set-search'
}
