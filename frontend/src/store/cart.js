const CART_KEY = 'legoland_cart'
const CART_EVENT = 'legoland-cart-updated'

function normalizeCart(rawCart) {
  if (!Array.isArray(rawCart)) return []
  return rawCart.filter(function (item) {
    return item && item.id
  }).map(function (item) {
    return {
      ...item,
      quantity: Number(item.quantity) > 0 ? Number(item.quantity) : 1
    }
  })
}

export function getCart() {
  try {
    const raw = localStorage.getItem(CART_KEY)
    if (!raw) return []
    return normalizeCart(JSON.parse(raw))
  } catch (e) {
    console.error('Ошибка чтения корзины', e)
    return []
  }
}

function emit(cart) {
  window.dispatchEvent(new CustomEvent(CART_EVENT, { detail: cart }))
}

export function setCart(cart) {
  const safeCart = normalizeCart(cart)
  localStorage.setItem(CART_KEY, JSON.stringify(safeCart))
  emit(safeCart)
  return safeCart
}

export function addToCart(product) {
  const cart = getCart()
  const item = cart.find(function (entry) {
    return entry.id === product.id
  })

  if (item) item.quantity += 1
  else cart.push({ ...product, quantity: 1 })

  return setCart(cart)
}

export function removeFromCart(productId) {
  const cart = getCart().filter(function (entry) {
    return entry.id !== productId
  })
  return setCart(cart)
}

export function updateCartQuantity(productId, quantity) {
  const targetQty = Number(quantity)
  if (targetQty <= 0) {
    return removeFromCart(productId)
  }

  const cart = getCart().map(function (entry) {
    if (entry.id === productId) {
      return { ...entry, quantity: targetQty }
    }
    return entry
  })

  return setCart(cart)
}

export function getCartCount() {
  return getCart().reduce(function (sum, item) {
    return sum + Number(item.quantity)
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
