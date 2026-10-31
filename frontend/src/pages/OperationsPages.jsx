import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, ArrowUpRight, Boxes, CircleUserRound, Leaf, LogOut, Mail, RefreshCw, ShieldCheck } from 'lucide-react'
import { Link, Navigate, Outlet, useLocation, useNavigate, useParams } from 'react-router-dom'
import { authRequest } from '../api/auth.js'
import { useAuth } from '../auth/useAuth.js'

const operationPages = [
  { path: 'enquiries', label: 'Enquiries', endpoint: 'operations/enquiries/', permission: 'exportenquiry', icon: Mail },
  { path: 'farms', label: 'Farms', endpoint: 'operations/farms/', permission: 'farm', icon: Leaf },
  { path: 'crop-seasons', label: 'Crop seasons', endpoint: 'operations/crop-seasons/', permission: 'cropseason', icon: Leaf },
  { path: 'harvests', label: 'Harvests', endpoint: 'operations/harvests/', permission: 'harvest', icon: Leaf },
  { path: 'batches', label: 'Production batches', endpoint: 'operations/batches/', permission: 'productionbatch', icon: Boxes },
  { path: 'processing-records', label: 'Processing records', endpoint: 'operations/processing-records/', permission: 'processingrecord', icon: Boxes },
  { path: 'inventory', label: 'Inventory movements', endpoint: 'operations/inventory-movements/', permission: 'inventorymovement', icon: Boxes },
]

const field = (name, label, type = 'text', options = {}) => ({ name, label, type, ...options })

const definitions = {
  farms: {
    title: 'Farms',
    description: 'Private farm records and their recorded location and area.',
    list: ['reference', 'name', 'location', 'area', 'area_unit', 'is_active'],
    create: [
      field('reference', 'Farm reference', 'text', { required: true }),
      field('name', 'Farm name', 'text', { required: true }),
      field('location', 'Location or address', 'textarea', { required: true }),
      field('area', 'Area (optional)', 'number'),
      field('area_unit', 'Area unit', 'select', { options: [['', 'Choose a unit'], ['acre', 'Acres'], ['hectare', 'Hectares']] }),
      field('description', 'Description', 'textarea'),
      field('internal_notes', 'Internal notes', 'textarea'),
      field('is_active', 'Status', 'select', { options: [['true', 'Active'], ['false', 'Inactive']] }),
    ],
    edit: [
      field('name', 'Farm name', 'text', { required: true }),
      field('location', 'Location or address', 'textarea', { required: true }),
      field('area', 'Area (optional)', 'number'),
      field('area_unit', 'Area unit', 'select', { options: [['', 'Choose a unit'], ['acre', 'Acres'], ['hectare', 'Hectares']] }),
      field('description', 'Description', 'textarea'),
      field('internal_notes', 'Internal notes', 'textarea'),
      field('is_active', 'Status', 'select', { options: [['true', 'Active'], ['false', 'Inactive']] }),
    ],
  },
  'crop-seasons': {
    title: 'Crop seasons',
    description: 'Season records connected to a farm. Dates are optional when not known.',
    list: ['reference', 'farm_reference', 'crop_name', 'planting_date', 'expected_harvest_date', 'status'],
    create: [
      field('reference', 'Season reference', 'text', { required: true }),
      field('farm_reference', 'Farm reference', 'text', { required: true }),
      field('crop_name', 'Crop name', 'text', { required: true }),
      field('planting_date', 'Planting date', 'date'),
      field('expected_harvest_date', 'Expected harvest date', 'date'),
      field('status', 'Status', 'select', { options: [['planned', 'Planned'], ['growing', 'Growing'], ['harvested', 'Harvested'], ['closed', 'Closed'], ['cancelled', 'Cancelled']] }),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
    edit: [
      field('farm_reference', 'Farm reference', 'text', { required: true }),
      field('crop_name', 'Crop name', 'text', { required: true }),
      field('planting_date', 'Planting date', 'date'),
      field('expected_harvest_date', 'Expected harvest date', 'date'),
      field('status', 'Status', 'select', { options: [['planned', 'Planned'], ['growing', 'Growing'], ['harvested', 'Harvested'], ['closed', 'Closed'], ['cancelled', 'Cancelled']] }),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
  },
  harvests: {
    title: 'Harvests',
    description: 'Recorded harvest quantities, dates, and crop-season lineage.',
    list: ['reference', 'crop_season_reference', 'harvest_date', 'quantity', 'quantity_unit'],
    create: [
      field('reference', 'Harvest reference', 'text', { required: true }),
      field('crop_season_reference', 'Crop season reference', 'text', { required: true }),
      field('harvest_date', 'Harvest date', 'date', { required: true }),
      field('quantity', 'Quantity', 'number', { required: true, min: '0.001', step: '0.001' }),
      field('quantity_unit', 'Unit', 'select', { required: true, options: [['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('notes', 'Notes', 'textarea'),
    ],
    edit: [
      field('crop_season_reference', 'Crop season reference', 'text', { required: true }),
      field('harvest_date', 'Harvest date', 'date', { required: true }),
      field('quantity', 'Quantity', 'number', { required: true, min: '0.001', step: '0.001' }),
      field('quantity_unit', 'Unit', 'select', { required: true, options: [['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('notes', 'Notes', 'textarea'),
    ],
  },
  batches: {
    title: 'Production batches',
    description: 'Each batch links to a harvest and starts with an automatic production receipt.',
    list: ['reference', 'harvest_reference', 'crop_season_reference', 'farm_reference', 'product_name', 'batch_date', 'status', 'available_quantity_kg'],
    create: [
      field('reference', 'Batch reference', 'text', { required: true }),
      field('harvest_reference', 'Harvest reference', 'text', { required: true }),
      field('product_name', 'Spice or product identification', 'text', { required: true }),
      field('batch_date', 'Batch date', 'date', { required: true }),
      field('initial_quantity', 'Initial quantity', 'number', { required: true, min: '0.001', step: '0.001' }),
      field('quantity_unit', 'Unit', 'select', { required: true, options: [['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('status', 'Status', 'select', { options: [['recorded', 'Recorded'], ['processing', 'Processing'], ['stored', 'Stored'], ['on_hold', 'On hold'], ['closed', 'Closed']] }),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
    edit: [
      field('status', 'Status', 'select', { options: [['recorded', 'Recorded'], ['processing', 'Processing'], ['stored', 'Stored'], ['on_hold', 'On hold'], ['closed', 'Closed']] }),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
  },
  'processing-records': {
    title: 'Processing records',
    description: 'Record actual activities only. These notes do not change inventory automatically.',
    list: ['id', 'batch_reference', 'activity', 'activity_date', 'input_quantity', 'output_quantity'],
    create: [
      field('batch_reference', 'Batch reference', 'text', { required: true }),
      field('activity', 'Activity', 'text', { required: true }),
      field('activity_date', 'Activity date', 'date', { required: true }),
      field('input_quantity', 'Input quantity', 'number', { min: '0.001', step: '0.001' }),
      field('input_unit', 'Input unit', 'select', { options: [['', 'Not recorded'], ['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('output_quantity', 'Output quantity', 'number', { min: '0.001', step: '0.001' }),
      field('output_unit', 'Output unit', 'select', { options: [['', 'Not recorded'], ['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('description', 'Description', 'textarea'),
      field('supporting_document_references', 'Document references', 'textarea'),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
    immutable: true,
  },
  inventory: {
    title: 'Inventory movements',
    description: 'Append-only ledger events. Available batch quantities are calculated by the backend.',
    list: ['reference', 'batch_reference', 'movement_type', 'quantity', 'quantity_unit', 'movement_date', 'reason'],
    create: (permissions) => [
      field('batch_reference', 'Batch reference', 'text', { required: true }),
      field('movement_type', 'Movement type', 'select', {
        required: true,
        options: [
          ['processing_increase', 'Processing adjustment (increase)'],
          ['processing_decrease', 'Processing adjustment (decrease)'],
          ['reservation', 'Reservation'],
          ['reservation_release', 'Reservation release'],
          ['dispatch', 'Dispatch'],
          ...(permissions.includes('api.approve_inventory_correction')
            ? [['correction_in', 'Approved correction (increase)'], ['correction_out', 'Approved correction (decrease)']]
            : []),
        ],
      }),
      field('quantity', 'Quantity', 'number', { required: true, min: '0.001', step: '0.001' }),
      field('quantity_unit', 'Unit', 'select', { required: true, options: [['kg', 'Kilograms'], ['metric_tonne', 'Metric tonnes']] }),
      field('movement_date', 'Movement date', 'date', { required: true }),
      field('reason', 'Reason or reference', 'text', { required: true, maxLength: 250 }),
      field('internal_notes', 'Internal notes', 'textarea'),
    ],
    immutable: true,
  },
}

function routeFor(page) {
  return page.path === 'inventory'
    ? 'operations/inventory-movements/'
    : page.endpoint
}

function hasPermission(user, permission) {
  return Boolean(user?.permissions?.includes(`api.${permission}`))
}

export function ProtectedOperationsRoute() {
  const { user, ready } = useAuth()
  const location = useLocation()
  if (!ready) return <p className="ops-state" role="status">Checking staff session…</p>
  if (!user || user.role !== 'staff') {
    return <Navigate replace state={{ from: location.pathname }} to="/operations/login" />
  }
  return <OperationsLayout />
}

export function OperationsLayout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  async function logout() {
    setError('')
    try {
      await signOut()
      navigate('/operations/login', { replace: true })
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  return (
    <main className="operations-shell" id="main-content">
      <header className="operations-header">
        <Link aria-label="SPICEORA home" className="wordmark operations-wordmark" to="/">SPICEORA<span>.</span></Link>
        <div className="operations-user">
          <span><CircleUserRound aria-hidden="true" size={17} />{user.full_name || user.email}</span>
          <button className="operations-logout" onClick={logout} type="button"><LogOut aria-hidden="true" size={16} />Sign out</button>
        </div>
      </header>
      <div className="operations-frame">
        <nav aria-label="Operations navigation" className="operations-nav">
          <Link className="operations-home-link" to="/operations"><ShieldCheck aria-hidden="true" size={18} />Operations</Link>
          {operationPages.map((page) => {
            const Icon = page.icon
            return hasPermission(user, `view_${page.permission}`) ? (
              <Link key={page.path} to={`/operations/${page.path}`}>
                <Icon aria-hidden="true" size={16} />{page.label}
              </Link>
            ) : null
          })}
        </nav>
        <section className="operations-content">
          {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
          <Outlet />
        </section>
      </div>
    </main>
  )
}

export function OperationsDashboard() {
  const { user } = useAuth()
  const [counts, setCounts] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    const available = operationPages.filter((page) =>
      hasPermission(user, `view_${page.permission}`),
    )
    const results = await Promise.all(
      available.map(async (page) => {
        try {
          const payload = await authRequest(routeFor(page))
          return [page.path, payload.count ?? payload.results?.length ?? 0]
        } catch (requestError) {
          return [page.path, requestError]
        }
      }),
    )
    const nextCounts = Object.fromEntries(results)
    setCounts(nextCounts)
    if (Object.values(nextCounts).some((value) => value instanceof Error)) {
      setError('Some records could not be loaded. Confirm your access and try again.')
    }
    setLoading(false)
  }, [user])

  useEffect(() => {
    Promise.resolve().then(load)
  }, [load])

  return (
    <>
      <div className="operations-title-row">
        <div>
          <p className="eyebrow">SPICEORA · Internal operations</p>
          <h1>Farm to inventory.</h1>
          <p>Private records for farms, crop seasons, harvests, batches and stock movements.</p>
        </div>
        <button aria-label="Refresh records" className="operations-refresh" onClick={load} type="button"><RefreshCw aria-hidden="true" size={16} />Refresh</button>
      </div>
      {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
      {loading ? <p className="ops-state" role="status">Loading authorized records…</p> : null}
      {!loading && !operationPages.some((page) => hasPermission(user, `view_${page.permission}`)) ? (
        <p className="ops-state">Your staff account has no operations viewing permissions. Contact an administrator.</p>
      ) : null}
      <div className="operations-cards">
        {operationPages.filter((page) => hasPermission(user, `view_${page.permission}`)).map((page) => {
          const Icon = page.icon
          const count = counts[page.path]
          return (
            <Link className="operations-card" key={page.path} to={`/operations/${page.path}`}>
              <span className="operations-card-icon"><Icon aria-hidden="true" size={20} /></span>
              <span className="operations-card-count">{loading ? '—' : count instanceof Error ? '—' : count ?? 0}</span>
              <span>{page.label}</span>
              <ArrowUpRight aria-hidden="true" className="operations-card-arrow" size={17} />
            </Link>
          )
        })}
      </div>
      <p className="operations-disclaimer">No farm or production data is preloaded. Add only records verified by your team.</p>
    </>
  )
}

function getDisplayValue(value) {
  if (value === true) return 'Active'
  if (value === false) return 'Inactive'
  if (value === null || value === undefined || value === '') return '—'
  return String(value)
}

function formValues(fields, row) {
  return Object.fromEntries(
    fields.map(({ name }) => {
      let value = row?.[name]
      if (typeof value === 'boolean') value = String(value)
      return [name, value ?? '']
    }),
  )
}

export function OperationsCollectionPage() {
  const { section } = useParams()
  const { user } = useAuth()
  const definition = definitions[section]
  const route = operationPages.find((page) => page.path === section)
  const endpoint = route && routeFor(route)
  const canView = route && hasPermission(user, `view_${route.permission}`)
  const canAdd = route && hasPermission(user, `add_${route.permission}`)
  const canChange = route && hasPermission(user, `change_${route.permission}`)
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [editing, setEditing] = useState(null)
  const createFields = typeof definition?.create === 'function' ? definition.create(user.permissions) : definition?.create || []
  const fields = editing ? (definition?.edit || createFields) : createFields
  const [values, setValues] = useState({})
  const columns = definition?.list || []

  const load = useCallback(async () => {
    if (!endpoint || !canView) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError('')
    try {
      const payload = await authRequest(endpoint)
      setRows(payload.results || [])
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [endpoint, canView])

  useEffect(() => {
    Promise.resolve().then(load)
  }, [load])

  if (!definition || !route) return <Navigate replace to="/operations" />
  if (!canView) return <p className="ops-state">Your account does not have permission to view {definition.title.toLowerCase()}.</p>

  function startEdit(row) {
    setEditing(row)
    setValues(formValues(definition.edit || createFields, row))
    setError('')
    setNotice('')
  }

  function resetForm() {
    setEditing(null)
    setValues({})
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    const payload = { ...values }
    for (const [key, value] of Object.entries(payload)) {
      if (value === '') delete payload[key]
    }
    if (values.area === '') {
      payload.area = null
      payload.area_unit = ''
    }
    for (const key of ['is_active']) {
      if (key in payload) payload[key] = payload[key] === 'true'
    }
    try {
      if (editing) {
        const reference = encodeURIComponent(editing.reference)
        await authRequest(`${endpoint}${reference}/`, {
          method: 'PATCH',
          body: payload,
        })
        setNotice('Record updated.')
      } else {
        await authRequest(endpoint, { method: 'POST', body: payload })
        setNotice('Record created.')
      }
      resetForm()
      await load()
    } catch (requestError) {
      setError(
        Object.values(requestError.errors || {}).flat().join(' ') ||
          requestError.message,
      )
    } finally {
      setBusy(false)
    }
  }

  function editAvailable(row) {
    return canChange && !definition.immutable && row.reference
  }

  return (
    <div className="operations-list-page">
      <div className="operations-title-row">
        <div>
          <p className="eyebrow">Operations · Traceability</p>
          <h1>{definition.title}</h1>
          <p>{definition.description}</p>
        </div>
        <button aria-label="Refresh list" className="operations-refresh" onClick={load} type="button"><RefreshCw aria-hidden="true" size={16} />Refresh</button>
      </div>

      {canAdd && (
        <form className="operations-form" onSubmit={submit}>
          <div className="operations-form-heading">
            <h2>{editing ? `Update ${definition.title.toLowerCase().replace(/s$/, '')}` : `Add ${definition.title.toLowerCase().replace(/s$/, '')}`}</h2>
            {editing && <button className="operations-cancel" onClick={resetForm} type="button">Cancel edit</button>}
          </div>
          <div className="operations-form-grid">
            {fields.map((item) => (
              <label className={`auth-field${item.type === 'textarea' ? ' auth-field--wide' : ''}`} key={item.name}>
                <span>{item.label}</span>
                {item.type === 'textarea' ? (
                  <textarea maxLength={item.maxLength} onChange={(event) => setValues((current) => ({ ...current, [item.name]: event.target.value }))} required={item.required} value={values[item.name] ?? ''} />
                ) : item.type === 'select' ? (
                  <select onChange={(event) => setValues((current) => ({ ...current, [item.name]: event.target.value }))} required={item.required} value={values[item.name] ?? ''}>
                    {(item.options || []).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                ) : (
                  <input max={item.max} maxLength={item.maxLength} min={item.min} onChange={(event) => setValues((current) => ({ ...current, [item.name]: event.target.value }))} required={item.required} step={item.step} type={item.type} value={values[item.name] ?? ''} />
                )}
              </label>
            ))}
          </div>
          {section === 'batches' && !editing && <p className="operations-help">Saving a batch also creates its initial receipt. The harvest allocation is validated by the server.</p>}
          {section === 'inventory' && <p className="operations-help">Inventory events are immutable. Current availability is shown on the batches page and calculated by the backend.</p>}
          <p aria-live="polite" className="operations-success" role="status">{notice}</p>
          {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
          <button className="auth-submit operations-submit" disabled={busy} type="submit">{busy ? 'Saving…' : editing ? 'Save changes' : 'Create record'}</button>
        </form>
      )}

      {!canAdd && <p className="operations-disclaimer">Your account can view these records but cannot create new ones.</p>}
      {loading && <p className="ops-state" role="status">Loading {definition.title.toLowerCase()}…</p>}
      {error && !canAdd && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
      {!loading && rows.length === 0 && !error && <p className="ops-state">No {definition.title.toLowerCase()} recorded yet.</p>}
      {!loading && rows.length > 0 && (
        <div className="operations-table-wrap">
          <table className="operations-table">
            <thead><tr>{columns.map((column) => <th key={column} scope="col">{column.replaceAll('_', ' ')}</th>)}{canChange && !definition.immutable && <th scope="col">Action</th>}</tr></thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={row.reference || row.id || index}>
                  {columns.map((column) => <td key={column}>{getDisplayValue(row[column])}</td>)}
                  {canChange && !definition.immutable && (
                    <td>{editAvailable(row) && <button className="operations-edit" onClick={() => startEdit(row)} type="button">Edit</button>}</td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Link className="operations-back" to="/operations"><ArrowLeft aria-hidden="true" size={16} />Back to operations</Link>
    </div>
  )
}
