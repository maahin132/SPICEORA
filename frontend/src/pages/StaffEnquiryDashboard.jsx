import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, RefreshCw, Search } from 'lucide-react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { authRequest } from '../api/auth.js'
import { useAuth } from '../auth/useAuth.js'

const statusLabels = {
  new: 'New',
  in_progress: 'In progress',
  responded: 'Responded',
  closed: 'Closed',
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

export function StaffEnquiryInboxPage() {
  const { user, ready } = useAuth()
  const [rows, setRows] = useState([])
  const [summary, setSummary] = useState({ total: 0, new: 0, in_progress: 0, responded: 0, closed: 0 })
  const [filters, setFilters] = useState({ q: '', status: '', category: '', product: '', date_from: '', date_to: '' })
  const [page, setPage] = useState(1)
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canView = Boolean(user?.permissions?.includes('api.view_exportenquiry'))

  const load = useCallback(async () => {
    if (!canView) return
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({ page: String(page) })
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.set(key, value)
      })
      const payload = await authRequest(`operations/enquiries/?${params.toString()}`)
      setRows(payload.results || [])
      setCount(payload.count || 0)
      if (payload.summary) setSummary(payload.summary)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [filters, page, canView])

  useEffect(() => {
    if (ready && canView) Promise.resolve().then(load)
  }, [load, ready, canView])

  if (ready && !canView) return <Navigate replace to="/operations" />

  const maxPage = Math.max(1, Math.ceil(count / 25))
  return (
    <>
      <div className="operations-title-row">
        <div><p className="eyebrow">SPICEORA · Staff enquiries</p><h1>Enquiry inbox.</h1></div>
        <button className="operations-refresh" onClick={load} type="button"><RefreshCw aria-hidden="true" size={16} />Refresh</button>
      </div>
      <div className="enquiry-stat-grid">
        {[['total', 'Total enquiries'], ['new', 'New'], ['in_progress', 'In progress'], ['responded', 'Responded'], ['closed', 'Closed']].map(([key, label]) => (
          <article className="enquiry-stat" key={key}><span>{label}</span><strong>{summary[key] ?? 0}</strong></article>
        ))}
      </div>
      <form className="enquiry-filter-grid" onSubmit={(event) => { event.preventDefault(); setPage(1); load() }}>
        <label><span>Search</span><span className="enquiry-search"><Search aria-hidden="true" size={16} /><input value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} placeholder="Reference, name, company or country" /></span></label>
        <label><span>Status</span><select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}><option value="">All statuses</option>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label><span>Category</span><input value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value })} placeholder="Category slug" /></label>
        <label><span>Product</span><input value={filters.product} onChange={(event) => setFilters({ ...filters, product: event.target.value })} placeholder="Product slug" /></label>
        <label><span>From</span><input type="date" value={filters.date_from} onChange={(event) => setFilters({ ...filters, date_from: event.target.value })} /></label>
        <label><span>To</span><input type="date" value={filters.date_to} onChange={(event) => setFilters({ ...filters, date_to: event.target.value })} /></label>
        <button className="operations-primary" type="submit">Apply filters</button>
      </form>
      {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
      {loading ? <p className="ops-state">Loading enquiries…</p> : (
        <div className="enquiry-table-wrap">
          <table className="enquiry-table"><thead><tr><th>Reference</th><th>Interest</th><th>Status</th><th>Received</th></tr></thead><tbody>
                      {rows.map((row) => <tr key={row.public_reference}><td><Link to={`/operations/enquiries/${row.public_reference}`}>{row.public_reference}</Link></td><td>{row.product?.name || row.product_name_snapshot || row.category?.name || 'Not specified'}<small>{row.quantity ? `${row.quantity} ${row.quantity_unit}` : 'Quantity not specified'}</small></td><td><span className={`enquiry-status enquiry-status--${row.status}`}>{statusLabels[row.status]}</span></td><td>{formatDate(row.created_at)}</td></tr>)}
                      {!rows.length && <tr><td colSpan="4">No enquiries match these filters.</td></tr>}
          </tbody></table>
        </div>
      )}
      <div className="enquiry-pagination"><button type="button" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Previous</button><span>Page {page} of {maxPage}</span><button type="button" disabled={page >= maxPage} onClick={() => setPage((current) => current + 1)}>Next</button></div>
    </>
  )
}

export function StaffEnquiryDetailPage() {
  const { user, ready } = useAuth()
  const { publicReference } = useParams()
  const navigate = useNavigate()
  const [enquiry, setEnquiry] = useState(null)
  const [status, setStatus] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const canView = Boolean(user?.permissions?.includes('api.view_exportenquiry'))
  const canChange = Boolean(user?.permissions?.includes('api.change_exportenquiry'))

  const load = useCallback(async () => {
    if (!canView) return
    setLoading(true)
    setError('')
    try {
      const payload = await authRequest(`operations/enquiries/${encodeURIComponent(publicReference)}/`)
      setEnquiry(payload)
      setStatus(payload.status)
      setNotes(payload.internal_notes || '')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [publicReference, canView])

  useEffect(() => { if (ready && canView) Promise.resolve().then(load) }, [load, ready, canView])

  async function save(event) {
    event.preventDefault()
    if (!canChange) return
    setSaving(true); setError(''); setNotice('')
    try {
      const payload = await authRequest(`operations/enquiries/${encodeURIComponent(publicReference)}/`, { method: 'PATCH', body: { status, internal_notes: notes } })
      setEnquiry(payload); setStatus(payload.status); setNotes(payload.internal_notes || '')
      setNotice('Enquiry updated.')
    } catch (requestError) { setError(requestError.message) } finally { setSaving(false) }
  }

  if (ready && !canView) return <Navigate replace to="/operations" />
  if (loading) return <p className="ops-state">Loading enquiry…</p>
  if (!enquiry) return <><p className="auth-notice auth-notice--error" role="alert">{error || 'Enquiry not found.'}</p><button className="operations-back" type="button" onClick={() => navigate('/operations/enquiries')}><ArrowLeft aria-hidden="true" size={16} />Back to inbox</button></>
  return (
    <>
      <Link className="operations-back" to="/operations/enquiries"><ArrowLeft aria-hidden="true" size={16} />Back to inbox</Link>
      <div className="operations-title-row"><div><p className="eyebrow">Enquiry {enquiry.public_reference}</p><h1>{enquiry.full_name}</h1></div><span className={`enquiry-status enquiry-status--${enquiry.status}`}>{statusLabels[enquiry.status]}</span></div>
      {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}{notice && <p className="auth-notice" role="status">{notice}</p>}
      <div className="enquiry-detail-grid">
        <article className="enquiry-detail-card"><h2>Buyer</h2><dl><dt>Name</dt><dd>{enquiry.full_name}</dd><dt>Company</dt><dd>{enquiry.company_name || '—'}</dd><dt>Email</dt><dd>{enquiry.email}</dd><dt>Phone</dt><dd>{enquiry.phone || '—'}</dd><dt>Country</dt><dd>{enquiry.country}</dd></dl></article>
        <article className="enquiry-detail-card"><h2>Request</h2><dl><dt>Category</dt><dd>{enquiry.category?.name || '—'}</dd><dt>Product</dt><dd>{enquiry.product?.name || enquiry.product_name_snapshot || '—'}</dd><dt>Quantity</dt><dd>{enquiry.quantity ? `${enquiry.quantity} ${enquiry.quantity_unit}` : 'Not specified'}</dd><dt>Message</dt><dd className="enquiry-message">{enquiry.message || '—'}</dd></dl></article>
      </div>
      <form className="enquiry-edit-card" onSubmit={save}><h2>Staff handling</h2><label><span>Status</span><select value={status} disabled={!canChange} onChange={(event) => setStatus(event.target.value)}>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label><span>Internal notes</span><textarea maxLength={5000} disabled={!canChange} value={notes} onChange={(event) => setNotes(event.target.value)} /></label>      <button className="operations-primary" disabled={!canChange || saving} type="submit">{saving ? 'Saving…' : 'Save changes'}</button></form>    </>
  )
}
