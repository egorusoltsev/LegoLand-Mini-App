import { getToken, clearToken } from './authToken'

const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')

export async function apiFetch(path, options = {}) {
  const token = getToken()

  const headers = {
    ...(options.headers || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  })

  // Если токен невалиден, просто очищаем его.
  // Навигацию не делаем здесь, чтобы избежать циклов/белого экрана в webview.
  if (res.status === 401) {
    clearToken()
  }

  return res
}