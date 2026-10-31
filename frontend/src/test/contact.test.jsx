import React from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, useLocation } from 'react-router-dom'
import App from '../App.jsx'

function LocationDisplay() {
  const location = useLocation()
  return <output data-testid="location-display">
    {location.pathname}{location.search}{location.hash}
  </output>
}

function jsonResponse(payload, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  }))
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (url, options = {}) => {
    if (options.method === 'POST') {
      return jsonResponse({ reference: 'test-reference', message: 'Your enquiry has been received.' }, 201)
    }
    if (String(url).includes('/categories/')) {
      return jsonResponse([
        { slug: 'cumin', name: 'Cumin' },
        { slug: 'turmeric', name: 'Turmeric' },
      ])
    }
    if (String(url).includes('/products/cumin/')) {
      return jsonResponse({
        slug: 'cumin',
        name: 'Approved Cumin Product',
        category: { slug: 'cumin', name: 'Cumin' },
        summary: 'Approved test summary',
        description: 'Approved test description',
        image: null,
        image_alt: '',
      })
    }
    return jsonResponse({}, 404)
  }))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Phase 9 public contact route', () => {
  it('renders /contact/ using the existing enquiry form and product preselection', async () => {
    render(
      <MemoryRouter initialEntries={['/contact/?product=cumin&category=cumin']}>
        <LocationDisplay />
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByTestId('location-display')).toHaveTextContent('/contact/?product=cumin&category=cumin')
    expect(await screen.findByRole('heading', { name: 'Start a business conversation.' })).toBeInTheDocument()
    expect(await screen.findByText('Approved Cumin Product')).toBeInTheDocument()
  })

  it('preserves /enquiry/ category and legacy query parameters through the redirect', async () => {
    render(
      <MemoryRouter initialEntries={['/enquiry/?category=cumin&source=legacy#request']}>
        <LocationDisplay />
        <App />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByTestId('location-display')).toHaveTextContent('/contact/?category=cumin&source=legacy#request')
    })
    expect(await screen.findByRole('heading', { name: 'Start a business conversation.' })).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText(/Product or category of interest/i)).toHaveValue('cumin')
    })
  })

  it('preserves product preselection through the existing API submission payload contract', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/contact/?product=cumin&category=cumin']}>
        <App />
      </MemoryRouter>,
    )

    await screen.findByText('Approved Cumin Product')
    await user.type(screen.getByLabelText(/Full name/i), 'Buyer One')
    await user.type(screen.getByLabelText(/Business email/i), 'buyer@example.com')
    await user.type(screen.getByLabelText(/Country/i), 'Buyer Country')
    await user.type(screen.getByLabelText(/Estimated required quantity/i), '500')
    await user.selectOptions(screen.getByLabelText(/Quantity unit/i), 'kg')
    await user.click(screen.getByRole('button', { name: /Send export enquiry/i }))

    await screen.findByText('test-reference')

    const postCall = vi.mocked(fetch).mock.calls.find(([, options]) => options?.method === 'POST')
    expect(postCall).toBeTruthy()
    const payload = JSON.parse(postCall[1].body)
    expect(payload).not.toHaveProperty('consent')
    expect(payload).not.toHaveProperty('privacy_notice_version')
    expect(payload.product_slug).toBe('cumin')
    expect(payload).not.toHaveProperty('category_slug')
  })
})
