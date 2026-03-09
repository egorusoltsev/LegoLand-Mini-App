import { getToken, clearToken } from './authToken'

function resolveApiUrl() {
  const rawUrl = import.meta.env.VITE_API_URL
  if (typeof rawUrl === 'string' && rawUrl.trim()) {
    return rawUrl.trim().replace(/\/+$/, '')
  }

  if (typeof window !== 'undefined' && window.location && window.location.origin) {
    return window.location.origin
  }

  return ''
}

export const API_URL = resolveApiUrl()

export function buildApiUrl(path) {
  const endpoint = path.charAt(0) === '/' ? path : '/' + path
  return API_URL + endpoint
}

if (import.meta.env.DEV) {
  console.info('[api] resolved API_URL:', API_URL || '(empty, fallback to current origin)')
}

if (!API_URL) {
  console.error('[api] VITE_API_URL is empty. Frontend requests will use relative URLs and may fail in production.')
}

export async function apiFetch(path, options = {}) {
  const token = getToken()
  const endpoint = path.charAt(0) === '/' ? path : '/' + path
  const url = buildApiUrl(path)

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
