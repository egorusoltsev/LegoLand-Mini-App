const FAVORITES_KEY = 'legoland_favorites'
const FAVORITES_EVENT = 'legoland-favorites-updated'

function normalize(items) {
  if (!Array.isArray(items)) return []
  return items.filter(function (item) {
    return item && item.id
  })
}

function notify(items) {
  window.dispatchEvent(new CustomEvent(FAVORITES_EVENT, { detail: items }))
}

export function loadFavorites() {
  try {
    const raw = localStorage.getItem(FAVORITES_KEY)
    if (!raw) return []
    return normalize(JSON.parse(raw))
  } catch (error) {
    console.error('Ошибка чтения избранного', error)
    return []
  }
}

export function saveFavorites(items) {
  const safe = normalize(items)
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(safe))
  notify(safe)
  return safe
}

export function toggle(product) {
  const favorites = loadFavorites()
  const exists = favorites.some(function (item) {
    return item.id === product.id
  })

  if (exists) {
    return saveFavorites(favorites.filter(function (item) {
      return item.id !== product.id
    }))
  }

  return saveFavorites(favorites.concat(product))
}

export function count(items) {
  return normalize(items).length
}

export function subscribe(listener) {
  function onUpdate(event) {
    const detail = event && event.detail ? event.detail : loadFavorites()
    listener(detail)
  }

  function onStorage(event) {
    if (!event || event.key !== FAVORITES_KEY) return
    listener(loadFavorites())
  }

  window.addEventListener(FAVORITES_EVENT, onUpdate)
  window.addEventListener('storage', onStorage)

  return function unsubscribe() {
    window.removeEventListener(FAVORITES_EVENT, onUpdate)
    window.removeEventListener('storage', onStorage)
  }
}
