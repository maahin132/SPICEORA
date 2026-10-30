const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(
  /\/+$/,
  '',
)

let csrfToken = ''

export class AuthApiError extends Error {
  constructor(message, status, errors = {}) {
    super(message)
    this.name = 'AuthApiError'
    this.status = status
    this.errors = errors
  }
}

async function readJson(response) {
  try {
    return await response.json()
  } catch {
    return {}
  }
}

export async function initializeCsrf() {
  const response = await fetch(`${API_BASE_URL}/auth/csrf/`, {
    credentials: 'include',
    headers: { Accept: 'application/json' },
  })
  const payload = await readJson(response)
  if (!response.ok || !payload.csrf_token) {
    throw new AuthApiError('Security initialization failed. Please try again.', response.status)
  }
  csrfToken = payload.csrf_token
  return csrfToken
}

export async function authRequest(path, { method = 'GET', body } = {}) {
  const unsafe = !['GET', 'HEAD', 'OPTIONS'].includes(method.toUpperCase())
  if (unsafe && !csrfToken) await initializeCsrf()
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (unsafe) headers['X-CSRFToken'] = csrfToken

  let response
  try {
    response = await fetch(`${API_BASE_URL}/${path}`, {
      method,
      credentials: 'include',
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new AuthApiError('The service could not be reached. Please try again.', 0)
  }
  const payload = await readJson(response)
  if (payload.csrf_token) csrfToken = payload.csrf_token
  if (!response.ok) {
    const errors =
      payload?.errors && typeof payload.errors === 'object'
        ? payload.errors
        : {}
    const message =
      payload?.message ||
      payload?.detail ||
      (response.status === 403
        ? 'This account does not have permission for that operation.'
        : 'The request could not be completed. Please review the details and try again.')
    throw new AuthApiError(message, response.status, errors)
  }
  return payload
}

export function updateCsrfToken(token) {
  if (token) csrfToken = token
}
