const CART_KEY = 'legoland_cart'
const CART_EVENT = 'legoland-cart-updated'

function normalize(items) {
  if (!Array.isArray(items)) return []
  return items.filter(function (item) {
    return item && item.id
  }).map(function (item) {
    const quantity = Number(item.quantity)
    return {
      ...item,
      quantity: quantity > 0 ? quantity : 1
    }
  })
}

function notify(items) {
  window.dispatchEvent(new CustomEvent(CART_EVENT, { detail: items }))
}

export function loadCart() {
  try {
    const raw = localStorage.getItem(CART_KEY)
    if (!raw) return []
    return normalize(JSON.parse(raw))
  } catch (error) {
    console.error('Ошибка чтения корзины', error)
    return []
  }
}

export function saveCart(items) {
  const safe = normalize(items)
  localStorage.setItem(CART_KEY, JSON.stringify(safe))
  notify(safe)
  return safe
}

export function add(product) {
  const cart = loadCart()
  const existing = cart.find(function (item) {
    return item.id === product.id
  })

  if (existing) {
    existing.quantity = Number(existing.quantity) + 1
  } else {
    cart.push({ ...product, quantity: 1 })
  }

  return saveCart(cart)
}

export function remove(productId) {
  return saveCart(loadCart().filter(function (item) {
    return item.id !== productId
  }))
}

export function inc(productId) {
  const cart = loadCart().map(function (item) {
    if (item.id !== productId) return item
    return { ...item, quantity: Number(item.quantity) + 1 }
  })
  return saveCart(cart)
}

export function dec(productId) {
  const cart = loadCart()
  const item = cart.find(function (entry) {
    return entry.id === productId
  })

  if (!item) return cart

  if (Number(item.quantity) <= 1) {
    return remove(productId)
  }

  item.quantity = Number(item.quantity) - 1
  return saveCart(cart)
}

export function clear() {
  return saveCart([])
}

export function totalItems(items) {
  return normalize(items).reduce(function (sum, item) {
    return sum + Number(item.quantity)
  }, 0)
}

export function totalPrice(items) {
  return normalize(items).reduce(function (sum, item) {
    return sum + Number(item.price) * Number(item.quantity)
  }, 0)
}

export function subscribe(listener) {
  function onUpdate(event) {
    const detail = event && event.detail ? event.detail : loadCart()
    listener(detail)
  }

  function onStorage(event) {
    if (!event || event.key !== CART_KEY) return
    listener(loadCart())
  }

  window.addEventListener(CART_EVENT, onUpdate)
  window.addEventListener('storage', onStorage)

  return function unsubscribe() {
    window.removeEventListener(CART_EVENT, onUpdate)
    window.removeEventListener('storage', onStorage)
  }
}
