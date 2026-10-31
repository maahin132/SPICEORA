import React from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import App from '../App.jsx'
import { AuthContext } from '../auth/context.js'

function jsonResponse(payload, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  }))
}

function staffContext(overrides = {}) {
  return {
    user: {
      role: 'staff',
      full_name: 'Staff Tester',
      email: 'staff@example.com',
      permissions: ['api.view_exportenquiry', 'api.change_exportenquiry'],
    },
    ready: true,
    signOut: vi.fn(),
    ...overrides,
  }
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (url, options = {}) => {
    if (String(url).includes('/auth/csrf/')) {
      return jsonResponse({ csrf_token: 'test-csrf-token' })
    }
    if (String(url).includes('/operations/enquiries/ENQ-TEST')) {
      if (options.method === 'PATCH') {
        return jsonResponse({
          public_reference: 'ENQ-TEST',
          full_name: 'Buyer One',
          email: 'buyer@example.com',
          phone: '',
          country: 'Test Country',
          category: { slug: 'cumin', name: 'Cumin' },
          product: null,
          quantity: '25.000',
          quantity_unit: 'kg',
          message: 'Test message',
          status: 'responded',
          internal_notes: 'Updated staff note',
        })
      }
      return jsonResponse({
        public_reference: 'ENQ-TEST',
        full_name: 'Buyer One',
        email: 'buyer@example.com',
        phone: '',
        country: 'Test Country',
        category: { slug: 'cumin', name: 'Cumin' },
        product: null,
        quantity: '25.000',
        quantity_unit: 'kg',
        message: 'Test message',
        status: 'new',
        internal_notes: '',
      })
    }
    if (String(url).includes('/operations/enquiries/')) {
      return jsonResponse({
        count: 1,
        next: null,
        previous: null,
        results: [{
          public_reference: 'ENQ-TEST',
          category: { slug: 'cumin', name: 'Cumin' },
          product: null,
          product_name_snapshot: '',
          quantity: '25.000',
          quantity_unit: 'kg',
          status: 'new',
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        }],
        summary: { total: 1, new: 1, in_progress: 0, responded: 0, closed: 0 },
      })
    }
    return jsonResponse({}, 404)
  }))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Phase 10 staff enquiry dashboard', () => {
  it('shows the inbox and does not expose private list fields', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/enquiries']}>
        <AuthContext.Provider value={staffContext()}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Enquiry inbox.' })).toBeInTheDocument()
    expect(await screen.findByText('ENQ-TEST')).toBeInTheDocument()
    expect(screen.queryByText('buyer@example.com')).not.toBeInTheDocument()
    expect(screen.queryByText('Private Buyer')).not.toBeInTheDocument()
  })

  it('loads private detail only after navigation and PATCHes status and notes with CSRF', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/operations/enquiries/ENQ-TEST']}>
        <AuthContext.Provider value={staffContext()}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    await screen.findByText('buyer@example.com')
    await user.selectOptions(screen.getByLabelText('Status'), 'responded')
    await user.type(screen.getByLabelText('Internal notes'), 'Updated staff note')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    await waitFor(() => {
      expect(screen.getByText('Enquiry updated.')).toBeInTheDocument()
    })

    const patchCall = vi.mocked(fetch).mock.calls.find(([, options]) => options?.method === 'PATCH')
    expect(patchCall).toBeTruthy()
    expect(patchCall[1].headers['X-CSRFToken']).toBe('test-csrf-token')
    expect(JSON.parse(patchCall[1].body)).toEqual({ status: 'responded', internal_notes: 'Updated staff note' })
  })

  it('redirects staff without view permission and never fetches enquiry data', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/enquiries']}>
        <AuthContext.Provider value={staffContext({
          user: { role: 'staff', full_name: 'No Permission', permissions: [] },
        })}><App /></AuthContext.Provider>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: 'Enquiry inbox.' })).not.toBeInTheDocument()
    })
    const enquiryCalls = vi.mocked(fetch).mock.calls.filter(([url]) => String(url).includes('/operations/enquiries/'))
    expect(enquiryCalls).toHaveLength(0)
  })
})
