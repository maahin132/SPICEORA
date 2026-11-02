import React from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App.jsx'
import { AuthContext } from '../auth/context.js'

function jsonResponse(payload, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  }))
}

function staffContext(permissions) {
  return {
    user: {
      role: 'staff',
      full_name: 'Phase 11 Tester',
      email: 'phase11@example.com',
      permissions,
    },
    ready: true,
    signOut: vi.fn(),
  }
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    const value = String(url)
    if (value.includes('/auth/session/')) return jsonResponse({ authenticated: true, user: staffContext(['api.view_farm', 'api.add_farm', 'api.change_farm', 'api.view_cropseason', 'api.add_cropseason', 'api.change_cropseason']).user })
    if (value.includes('/auth/csrf/')) return jsonResponse({ csrf_token: 'phase11-csrf' })
    if (value.includes('/operations/farms/?') || value.endsWith('/operations/farms/')) {
      return jsonResponse({ count: 0, next: null, previous: null, results: [] })
    }
    if (value.includes('/operations/crop-seasons/')) {
      return jsonResponse({ count: 0, next: null, previous: null, results: [] })
    }
    return jsonResponse({}, 404)
  }))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Phase 11 Farm and Crop Season pages', () => {
  it('renders the Farm empty state and create action', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/farms']}>
        <AuthContext.Provider value={staffContext(['api.view_farm', 'api.add_farm'])}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Farms' })).toBeInTheDocument()
    expect(await screen.findByText('No farms recorded yet.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Add farm' })).toBeInTheDocument()
  })

  it('renders the Crop Season selector empty state on create', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/crop-seasons/new']}>
        <AuthContext.Provider value={staffContext(['api.view_farm', 'api.view_cropseason', 'api.add_cropseason'])}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Add crop season' })).toBeInTheDocument()
    expect(await screen.findByText('Create an active farm before creating a crop season.')).toBeInTheDocument()
  })

  it('does not expose create UI without add permission', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/farms/new']}>
        <AuthContext.Provider value={staffContext(['api.view_farm'])}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    expect(await screen.findByText('Your account does not have permission to create farms.')).toBeInTheDocument()
  })
})
