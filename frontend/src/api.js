import { getToken, clearToken } from './authToken'

function resolveApiUrl() {
  const rawUrl = import.meta.env.VITE_API_URL
  if (typeof rawUrl === 'string' && rawUrl.trim()) {
    return rawUrl.replace(/\/$/, '')
  }

  if (typeof window !== 'undefined' && window.location && window.location.origin) {
    return window.location.origin
  }

  return ''
}

export const API_URL = resolveApiUrl()

export async function apiFetch(path, options = {}) {
  const token = getToken()
  const endpoint = path.charAt(0) === '/' ? path : '/' + path
  const url = API_URL + endpoint

  const headers = {
    ...(options.headers || {})
  }

  if (token) {
    headers.Authorization = 'Bearer ' + token
  }

  let res
  try {
    res = await fetch(url, {
      ...options,
      headers,
      redirect: 'follow'
    })
  } catch (error) {
    console.error('API network error', {
      apiUrl: API_URL,
      endpoint,
      error
    })
    throw error
  }

  if (res.status === 401) {
    clearToken()
    if (typeof window !== 'undefined') {
      window.location.href = '/#/account'
    }
    return res
  }

  return res
}
