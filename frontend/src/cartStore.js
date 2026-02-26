const CART_KEY = 'legoland_cart'
const CART_EVENT = 'legoland-cart-updated'

export function getCart() {
  try {
    const raw = localStorage.getItem(CART_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
  } catch (e) {
    console.error('Ошибка чтения корзины', e)
    return []
  }
}

export function saveCart(cart) {
  const safeCart = Array.isArray(cart) ? cart : []
  localStorage.setItem(CART_KEY, JSON.stringify(safeCart))
  window.dispatchEvent(new CustomEvent(CART_EVENT, { detail: safeCart }))
}

export function getCartCount() {
  const cart = getCart()
  return cart.reduce(function (sum, item) {
    const quantity = Number(item && item.quantity ? item.quantity : 0)
    return sum + quantity
  }, 0)
}

export function subscribeCart(listener) {
  function handler(event) {
    const detail = event && event.detail ? event.detail : getCart()
    listener(detail)
  }

  function onStorage(event) {
    if (!event || event.key !== CART_KEY) return
    listener(getCart())
  }

  window.addEventListener(CART_EVENT, handler)
  window.addEventListener('storage', onStorage)

  return function unsubscribe() {
    window.removeEventListener(CART_EVENT, handler)
    window.removeEventListener('storage', onStorage)
  }
}
