import React from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App.jsx'
import { AuthContext } from '../auth/context.js'

function jsonResponse(payload, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } }))
}

function staffContext(permissions) {
  return { user: { role: 'staff', full_name: 'Phase 12 Tester', email: 'phase12@example.com', permissions }, ready: true, signOut: vi.fn() }
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    const value = String(url)
    if (value.includes('/auth/session/')) return jsonResponse({ authenticated: true, user: { role: 'staff', permissions: ['api.view_harvest', 'api.add_harvest', 'api.change_harvest', 'api.view_farm', 'api.view_cropseason'] } })
    if (value.includes('/auth/csrf/')) return jsonResponse({ csrf_token: 'phase12-csrf' })
    if (value.includes('/operations/harvests/')) {
      if (value.includes('HARVEST-01')) return jsonResponse({ reference: 'HARVEST-01', crop_season_reference: 'SEASON-01', harvest_date: '2026-10-01', quantity: '100.000', quantity_unit: 'kg', notes: 'Test note', historical_locked: false })
      return jsonResponse({ count: 0, next: null, previous: null, results: [] })
    }
    if (value.includes('/operations/farms/')) return jsonResponse({ count: 0, next: null, previous: null, results: [] })
    if (value.includes('/operations/crop-seasons/')) return jsonResponse({ count: 0, next: null, previous: null, results: [] })
    return jsonResponse({}, 404)
  }))
})

afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('Phase 12 Harvest pages', () => {
  it('renders the Harvest empty state and create action', async () => {
    render(<MemoryRouter initialEntries={["/operations/harvests"]}><AuthContext.Provider value={staffContext(['api.view_harvest', 'api.add_harvest'])}><App /></AuthContext.Provider></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: 'Harvests' })).toBeInTheDocument()
    expect(await screen.findByText('No harvests recorded yet.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Add harvest' })).toBeInTheDocument()
  })

  it('renders the create page and selector empty state', async () => {
    render(<MemoryRouter initialEntries={["/operations/harvests/new"]}><AuthContext.Provider value={staffContext(['api.view_harvest', 'api.add_harvest', 'api.view_farm', 'api.view_cropseason'])}><App /></AuthContext.Provider></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: 'Add harvest' })).toBeInTheDocument()
    expect(await screen.findByText('Choose a farm first')).toBeInTheDocument()
    expect(screen.queryByRole('textbox', { name: 'Crop season reference' })).not.toBeInTheDocument()
  })

  it('renders Harvest detail data', async () => {
    render(<MemoryRouter initialEntries={["/operations/harvests/HARVEST-01"]}><AuthContext.Provider value={staffContext(['api.view_harvest', 'api.change_harvest'])}><App /></AuthContext.Provider></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: 'Harvest detail' })).toBeInTheDocument()
    expect(await screen.findByText('HARVEST-01')).toBeInTheDocument()
  })

  it('does not expose create UI without add permission', async () => {
    render(<MemoryRouter initialEntries={["/operations/harvests/new"]}><AuthContext.Provider value={staffContext(['api.view_harvest'])}><App /></AuthContext.Provider></MemoryRouter>)
    expect(await screen.findByText('Your account does not have permission to create harvests.')).toBeInTheDocument()
  })
})
