const KEY = "token"

export function getToken() {
  try {
    return localStorage.getItem(KEY) || ""
  } catch (e) {
    // Telegram WebView иногда кидает SecurityError
    return ""
  }
}

export function setToken(token) {
  try {
    localStorage.setItem(KEY, token)
  } catch (e) {}
}

export function clearToken() {
  try {
    localStorage.removeItem(KEY)
  } catch (e) {}
}