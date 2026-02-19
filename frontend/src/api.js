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

  // 👇 важная штука: если токен невалиден / нет токена на защищённом роуте
  if (res.status === 401) {
    clearToken()
    // отправляем в аккаунт (там кнопка входа)
    window.location.href = "/account"
    return res
  }

  return res
}