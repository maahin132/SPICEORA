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

export class EnquiryApiError extends Error {
  constructor(message, status, errors = {}) {
    super(message)
    this.name = 'EnquiryApiError'
    this.status = status
    this.errors = errors
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

export async function submitEnquiry(enquiry) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}/enquiries/`, {
      method: 'POST',
      credentials: 'omit',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(enquiry),
    })
  } catch {
    throw new EnquiryApiError(
      'We could not send your enquiry. Check your connection and try again.',
      0,
    )
  }

  let payload = {}
  try {
    payload = await response.json()
  } catch {
    if (response.ok) {
      throw new EnquiryApiError('The server response could not be read.', response.status)
    }
  }

  if (!response.ok) {
    const errors =
      payload?.errors &&
      typeof payload.errors === 'object' &&
      !Array.isArray(payload.errors)
        ? payload.errors
        : {}
    const message =
      response.status === 429
        ? 'Too many submissions were received from this connection. Please try again later.'
        : Object.keys(errors).length
          ? 'Review the highlighted fields and try again.'
          : 'We could not submit your enquiry. Please try again.'
    throw new EnquiryApiError(message, response.status, errors)
  }

  return payload
}
