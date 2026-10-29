const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(
  /\/+$/,
  '',
)

export class CatalogApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'CatalogApiError'
    this.status = status
  }
}

async function getJson(path) {
  const response = await fetch(`${API_BASE_URL}/${path}`, {
    headers: { Accept: 'application/json' },
  })

  let payload
  try {
    payload = await response.json()
  } catch {
    throw new CatalogApiError('The catalogue response could not be read.', response.status)
  }

  if (!response.ok) {
    throw new CatalogApiError(
      'The catalogue could not be loaded.',
      response.status,
    )
  }

  return payload
}

export function getCategories() {
  return getJson('categories/')
}

export function getProducts({ category = '', page = '1' } = {}) {
  const query = new URLSearchParams()
  if (category) query.set('category', category)
  if (page) query.set('page', page)
  return getJson(`products/?${query.toString()}`)
}

export function getProduct(slug) {
  return getJson(`products/${encodeURIComponent(slug)}/`)
}
