const FAVORITES_KEY = 'legoland_favorites'
const FAVORITES_EVENT = 'legoland-favorites-updated'

function normalizeFavorites(rawFavorites) {
  if (!Array.isArray(rawFavorites)) return []
  return rawFavorites.filter(function (item) {
    return item && item.id
  })
}

export function getFavorites() {
  try {
    const raw = localStorage.getItem(FAVORITES_KEY)
    if (!raw) return []
    return normalizeFavorites(JSON.parse(raw))
  } catch (e) {
    console.error('Ошибка чтения избранного', e)
    return []
  }
}

function emit(favorites) {
  window.dispatchEvent(new CustomEvent(FAVORITES_EVENT, { detail: favorites }))
}

export function setFavorites(favorites) {
  const safeFavorites = normalizeFavorites(favorites)
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(safeFavorites))
  emit(safeFavorites)
  return safeFavorites
}

export function isFavorite(productId) {
  return getFavorites().some(function (item) {
    return item.id === productId
  })
}

export function toggleFavorite(product) {
  const favorites = getFavorites()
  const exists = favorites.some(function (item) {
    return item.id === product.id
  })

  if (exists) {
    return setFavorites(favorites.filter(function (item) {
      return item.id !== product.id
    }))
  }

  return setFavorites(favorites.concat(product))
}

export function getFavoritesCount() {
  return getFavorites().length
}

export function subscribeFavorites(listener) {
  function handler(event) {
    const detail = event && event.detail ? event.detail : getFavorites()
    listener(detail)
  }

  function onStorage(event) {
    if (!event || event.key !== FAVORITES_KEY) return
    listener(getFavorites())
  }

  window.addEventListener(FAVORITES_EVENT, handler)
  window.addEventListener('storage', onStorage)

  return function unsubscribe() {
    window.removeEventListener(FAVORITES_EVENT, handler)
    window.removeEventListener('storage', onStorage)
  }
}
