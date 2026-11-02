import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, Edit3, Eye, Plus, RefreshCw } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { authRequest } from '../api/auth.js'
import { useAuth } from '../auth/useAuth.js'

const display = (value) => {
  if (value === true) return 'Active'
  if (value === false) return 'Inactive'
  if (value === null || value === undefined || value === '') return '—'
  return String(value)
}

const permission = (user, action, model) => Boolean(user?.permissions?.includes(`api.${action}_${model}`))

function Pagination({ payload, page, onPage }) {
  if (!payload) return null
  const hasPrevious = Boolean(payload.previous)
  const hasNext = Boolean(payload.next)
  if (!hasPrevious && !hasNext) return null
  return (
    <div className="operations-pagination" aria-label="Pagination">
      <button className="operations-pagination-button" disabled={!hasPrevious} onClick={() => onPage(page - 1)} type="button">Previous</button>
      <span>Page {page}</span>
      <button className="operations-pagination-button" disabled={!hasNext} onClick={() => onPage(page + 1)} type="button">Next</button>
    </div>
  )
}

function ErrorMessage({ error }) {
  if (!error) return null
  return <p className="auth-notice auth-notice--error" role="alert">{error}</p>
}

function Field({ label, name, type = 'text', value, onChange, required = false, children, ...props }) {
  return (
    <label className="auth-field">
      <span>{label}</span>
      {type === 'textarea' ? (
        <textarea id={name} name={name} required={required} value={value ?? ''} onChange={onChange} {...props} />
      ) : type === 'select' ? (
        <select id={name} name={name} required={required} value={value ?? ''} onChange={onChange} {...props}>{children}</select>
      ) : (
        <input id={name} name={name} type={type} required={required} value={value ?? ''} onChange={onChange} {...props} />
      )}
    </label>
  )
}

function PageHeader({ eyebrow, title, description, action, actionLabel, refresh, refreshLabel = 'Refresh list' }) {
  return (
    <div className="operations-title-row">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="operations-header-actions">
        {refresh && <button aria-label={refreshLabel} className="operations-refresh" onClick={refresh} type="button"><RefreshCw aria-hidden="true" size={16} />Refresh</button>}
        {action && <Link className="operations-primary-action" to={action}><Plus aria-hidden="true" size={16} />{actionLabel}</Link>}
      </div>
    </div>
  )
}

function FarmSelector(valueProps) {
  const { value, onChange } = valueProps

  const [farms, setFarms] = useState([])
  const [page, setPage] = useState(1)
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async (nextPage = 1) => {
    setLoading(true)
    setError('')
    try {
      const result = await authRequest(`operations/farms/?page=${nextPage}`)
      setFarms(result.results || [])
      setPayload(result)
      setPage(nextPage)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    Promise.resolve().then(() => load(1))
  }, [load])

  const selectedOnPage = farms.some((farm) => farm.reference === value)
  return (
    <div className="farm-selector">
      <label className="auth-field">
        <span>Farm</span>
        <select name="farm_reference" value={value ?? ''} onChange={onChange} required disabled={loading || farms.length === 0}>
          <option value="">{loading ? 'Loading farms…' : farms.length === 0 ? 'No farms available' : 'Choose a farm'}</option>
          {!selectedOnPage && value ? <option value={value}>{value}</option> : null}
          {farms.map((farm) => <option key={farm.reference} value={farm.reference}>{farm.name || farm.reference} — {farm.reference}</option>)}
        </select>
      </label>
      {loading && <p className="operations-help" role="status">Loading authorized farms…</p>}
      {error && <ErrorMessage error={error} />}
      {!loading && !error && farms.length === 0 && <p className="operations-help">Create an active farm before creating a crop season.</p>}
      <Pagination payload={payload} page={page} onPage={(nextPage) => load(nextPage)} />
    </div>
  )
}

export function FarmListPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [payload, setPayload] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canView = permission(user, 'view', 'farm')
  const canAdd = permission(user, 'add', 'farm')

  const load = useCallback(async (nextPage = page) => {
    if (!canView) return
    setLoading(true)
    setError('')
    try {
      const result = await authRequest(`operations/farms/?page=${nextPage}`)
      setRows(result.results || [])
      setPayload(result)
      setPage(nextPage)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [canView, page])

  useEffect(() => { Promise.resolve().then(() => load(page)) }, [load, page])
  if (!canView) return <p className="ops-state">Your account does not have permission to view farms.</p>

  return (
    <div className="operations-list-page">
      <PageHeader eyebrow="Operations · Traceability" title="Farms" description="Private farm records, locations and recorded area." action={canAdd ? '/operations/farms/new' : null} actionLabel="Add farm" refresh={() => load(page)} />
      <ErrorMessage error={error} />
      {loading && <p className="ops-state" role="status">Loading farms…</p>}
      {!loading && !error && rows.length === 0 && <p className="ops-state">No farms recorded yet.</p>}
      {!loading && rows.length > 0 && (
        <div className="operations-table-wrap">
          <table className="operations-table">
            <thead><tr><th>Name</th><th>Reference</th><th>Location</th><th>Area</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>{rows.map((row) => (
              <tr key={row.reference}>
                <td>{row.name}</td><td>{row.reference}</td><td>{row.location || '—'}</td>
                <td>{row.area === null ? '—' : `${row.area} ${row.area_unit || ''}`}</td><td>{row.is_active ? 'Active' : 'Inactive'}</td>
                <td><div className="operations-row-actions"><Link aria-label={`View ${row.name}`} to={`/operations/farms/${encodeURIComponent(row.reference)}`}><Eye size={15} />View</Link>{permission(user, 'change', 'farm') && <Link aria-label={`Edit ${row.name}`} to={`/operations/farms/${encodeURIComponent(row.reference)}/edit`}><Edit3 size={15} />Edit</Link>}</div></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
      <Pagination payload={payload} page={page} onPage={(nextPage) => load(nextPage)} />
      <button className="operations-back-button" onClick={() => navigate('/operations')} type="button"><ArrowLeft size={16} />Back to operations</button>
    </div>
  )
}

function FarmForm({ mode, record = null }) {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [values, setValues] = useState({
    reference: record?.reference || '', name: record?.name || '', location: record?.location || '', area: record?.area ?? '', area_unit: record?.area_unit || '', description: record?.description || '', internal_notes: record?.internal_notes || '', is_active: record?.is_active === false ? 'false' : 'true',
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const editing = mode === 'edit'
  const allowed = editing ? permission(user, 'change', 'farm') : permission(user, 'add', 'farm')
  if (!allowed) return <p className="ops-state">Your account does not have permission to {editing ? 'edit' : 'create'} farms.</p>

  const onChange = (event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
  async function submit(event) {
    event.preventDefault()
    setBusy(true); setError(''); setSuccess('')
    const payload = { ...values, is_active: values.is_active === 'true' }
    if (payload.area === '') { payload.area = null; payload.area_unit = '' }
    if (!editing) payload.area_unit = payload.area_unit || ''
    try {
      if (editing) {
        await authRequest(`operations/farms/${encodeURIComponent(record.reference)}/`, { method: 'PATCH', body: payload })
        setSuccess('Farm updated.')
      } else {
        const created = await authRequest('operations/farms/', { method: 'POST', body: payload })
        navigate(`/operations/farms/${encodeURIComponent(created.reference)}`, { replace: true })
      }
    } catch (requestError) {
      setError(Object.values(requestError.errors || {}).flat().join(' ') || requestError.message)
    } finally { setBusy(false) }
  }

  return (
    <div>
      <PageHeader eyebrow="Operations · Farms" title={editing ? 'Edit farm' : 'Add farm'} description={editing ? 'Update verified farm information.' : 'Create a new private farm record.'} refresh={editing ? () => navigate(0) : null} />
      <form className="operations-form" onSubmit={submit}>
        <div className="operations-form-grid">
          {!editing && <Field label="Farm reference" name="reference" required value={values.reference} onChange={onChange} maxLength={40} />}
          <Field label="Farm name" name="name" required value={values.name} onChange={onChange} maxLength={160} />
          <Field label="Location or address" name="location" type="textarea" required value={values.location} onChange={onChange} />
          <Field label="Area (optional)" name="area" type="number" min="0.001" step="0.001" value={values.area} onChange={onChange} />
          <Field label="Area unit" name="area_unit" type="select" value={values.area_unit} onChange={onChange}><option value="">Choose a unit</option><option value="acre">Acres</option><option value="hectare">Hectares</option></Field>
          <Field label="Description" name="description" type="textarea" value={values.description} onChange={onChange} />
          <Field label="Internal notes" name="internal_notes" type="textarea" value={values.internal_notes} onChange={onChange} />
          <Field label="Status" name="is_active" type="select" value={values.is_active} onChange={onChange}><option value="true">Active</option><option value="false">Inactive</option></Field>
        </div>
        <ErrorMessage error={error} /><p className="operations-success" role="status">{success}</p>
        <button className="auth-submit operations-submit" disabled={busy} type="submit">{busy ? 'Saving…' : editing ? 'Save changes' : 'Create farm'}</button>
      </form>
      <Link className="operations-back" to="/operations/farms"><ArrowLeft size={16} />Back to farms</Link>
    </div>
  )
}

export function FarmCreatePage() { return <FarmForm mode="create" /> }

export function FarmEditPage() {
  const { reference } = useParams()
  const [record, setRecord] = useState(null)
  const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  useEffect(() => {
    if (!permission(user, 'change', 'farm')) return
    authRequest(`operations/farms/${encodeURIComponent(reference)}/`).then(setRecord).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false))
  }, [reference, user])
  if (!permission(user, 'change', 'farm')) return <p className="ops-state">Your account does not have permission to edit farms.</p>
  if (loading) return <p className="ops-state" role="status">Loading farm…</p>
  if (error) return <ErrorMessage error={error} />
  return record ? <FarmForm mode="edit" record={record} /> : <p className="ops-state">Farm not found.</p>
}

export function FarmDetailPage() {
  const { reference } = useParams(); const { user } = useAuth()
  const [farm, setFarm] = useState(null); const [seasons, setSeasons] = useState([])
  const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const canView = permission(user, 'view', 'farm')
  const load = useCallback(async () => {
    if (!canView) return
    setLoading(true); setError('')
    try {
      const [farmData, seasonData] = await Promise.all([
        authRequest(`operations/farms/${encodeURIComponent(reference)}/`),
        permission(user, 'view', 'cropseason') ? authRequest(`operations/crop-seasons/?farm_reference=${encodeURIComponent(reference)}`) : Promise.resolve({ results: [] }),
      ])
      setFarm(farmData); setSeasons(seasonData.results || [])
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }, [canView, reference, user])
  useEffect(() => { Promise.resolve().then(load) }, [load])
  if (!canView) return <p className="ops-state">Your account does not have permission to view farm details.</p>
  return (
    <div>
      <PageHeader eyebrow="Operations · Farms" title="Farm detail" description="Private farm information and linked crop seasons." refresh={load} />
      {loading && <p className="ops-state" role="status">Loading farm…</p>}<ErrorMessage error={error} />
      {!loading && farm && <>
        <section className="operations-detail-card"><dl><div><dt>Name</dt><dd>{farm.name}</dd></div><div><dt>Reference</dt><dd>{farm.reference}</dd></div><div><dt>Location</dt><dd>{farm.location || '—'}</dd></div><div><dt>Area</dt><dd>{farm.area === null ? '—' : `${farm.area} ${farm.area_unit}`}</dd></div><div><dt>Status</dt><dd>{display(farm.is_active)}</dd></div><div className="operations-detail-wide"><dt>Description</dt><dd>{farm.description || '—'}</dd></div><div className="operations-detail-wide"><dt>Internal notes</dt><dd>{farm.internal_notes || '—'}</dd></div></dl>{permission(user, 'change', 'farm') && <Link className="operations-primary-action" to={`/operations/farms/${encodeURIComponent(reference)}/edit`}><Edit3 size={16} />Edit farm</Link>}</section>
        <section className="operations-detail-section"><div className="operations-form-heading"><h2>Linked crop seasons</h2>{permission(user, 'add', 'cropseason') && <Link className="operations-primary-action" to="/operations/crop-seasons/new"><Plus size={16} />Add season</Link>}</div>{seasons.length === 0 ? <p className="ops-state">No crop seasons are linked to this farm.</p> : <div className="operations-table-wrap"><table className="operations-table"><thead><tr><th>Reference</th><th>Crop</th><th>Planting</th><th>Expected harvest</th><th>Status</th><th>Action</th></tr></thead><tbody>{seasons.map((season) => <tr key={season.reference}><td>{season.reference}</td><td>{season.crop_name}</td><td>{display(season.planting_date)}</td><td>{display(season.expected_harvest_date)}</td><td>{display(season.status)}</td><td><Link className="operations-row-link" to={`/operations/crop-seasons/${encodeURIComponent(season.reference)}`}>View</Link></td></tr>)}</tbody></table></div>}</section>
      </>}
      <Link className="operations-back" to="/operations/farms"><ArrowLeft size={16} />Back to farms</Link>
    </div>
  )
}

export function CropSeasonListPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [payload, setPayload] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canView = permission(user, 'view', 'cropseason')
  const canAdd = permission(user, 'add', 'cropseason')
  const load = useCallback(async (nextPage = page) => {
    if (!canView) return
    setLoading(true); setError('')
    try {
      const result = await authRequest(`operations/crop-seasons/?page=${nextPage}`)
      setRows(result.results || []); setPayload(result); setPage(nextPage)
    } catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [canView, page])
  useEffect(() => { Promise.resolve().then(() => load(page)) }, [load, page])
  if (!canView) return <p className="ops-state">Your account does not have permission to view crop seasons.</p>
  return <div className="operations-list-page">
    <PageHeader eyebrow="Operations · Traceability" title="Crop seasons" description="Season records connected to verified farms." action={canAdd ? '/operations/crop-seasons/new' : null} actionLabel="Add season" refresh={() => load(page)} />
    <ErrorMessage error={error} />
    {loading && <p className="ops-state" role="status">Loading crop seasons…</p>}
    {!loading && !error && rows.length === 0 && <p className="ops-state">No crop seasons recorded yet.</p>}
    {!loading && rows.length > 0 && <div className="operations-table-wrap"><table className="operations-table"><thead><tr><th>Reference</th><th>Farm</th><th>Crop</th><th>Planting</th><th>Expected harvest</th><th>Status</th><th>Actions</th></tr></thead><tbody>{rows.map((row) => <tr key={row.reference}><td>{row.reference}</td><td><Link to={`/operations/farms/${encodeURIComponent(row.farm_reference)}`}>{row.farm_reference}</Link></td><td>{row.crop_name}</td><td>{display(row.planting_date)}</td><td>{display(row.expected_harvest_date)}</td><td>{display(row.status)}</td><td><div className="operations-row-actions"><Link aria-label={`View ${row.reference}`} to={`/operations/crop-seasons/${encodeURIComponent(row.reference)}`}><Eye size={15} />View</Link>{permission(user, 'change', 'cropseason') && <Link aria-label={`Edit ${row.reference}`} to={`/operations/crop-seasons/${encodeURIComponent(row.reference)}/edit`}><Edit3 size={15} />Edit</Link>}</div></td></tr>)}</tbody></table></div>}
    <Pagination payload={payload} page={page} onPage={(nextPage) => load(nextPage)} />
    <button className="operations-back-button" onClick={() => navigate('/operations')} type="button"><ArrowLeft size={16} />Back to operations</button>
  </div>
}

function CropSeasonForm({ mode, record = null }) {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [values, setValues] = useState({ reference: record?.reference || '', farm_reference: record?.farm_reference || '', crop_name: record?.crop_name || '', planting_date: record?.planting_date || '', expected_harvest_date: record?.expected_harvest_date || '', status: record?.status || 'planned', internal_notes: record?.internal_notes || '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const editing = mode === 'edit'
  const allowed = editing ? permission(user, 'change', 'cropseason') : permission(user, 'add', 'cropseason')
  if (!allowed) return <p className="ops-state">Your account does not have permission to {editing ? 'edit' : 'create'} crop seasons.</p>
  const onChange = (event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
  async function submit(event) {
    event.preventDefault()
    if (!values.farm_reference) { setError('Choose a valid farm.'); return }
    setBusy(true); setError(''); setSuccess('')
    const payload = { ...values }
    for (const key of ['planting_date', 'expected_harvest_date', 'internal_notes']) if (payload[key] === '') delete payload[key]
    try {
      if (editing) { await authRequest(`operations/crop-seasons/${encodeURIComponent(record.reference)}/`, { method: 'PATCH', body: payload }); setSuccess('Crop season updated.') }
      else { const created = await authRequest('operations/crop-seasons/', { method: 'POST', body: payload }); navigate(`/operations/crop-seasons/${encodeURIComponent(created.reference)}`, { replace: true }) }
    } catch (requestError) { setError(Object.values(requestError.errors || {}).flat().join(' ') || requestError.message) }
    finally { setBusy(false) }
  }
  return <div><PageHeader eyebrow="Operations · Crop seasons" title={editing ? 'Edit crop season' : 'Add crop season'} description={editing ? 'Update season information while preserving historical relationships.' : 'Create a private season linked to an existing farm.'} />
    <form className="operations-form" onSubmit={submit}><div className="operations-form-grid">
      {!editing && <Field label="Season reference" name="reference" required value={values.reference} onChange={onChange} maxLength={40} />}
      <FarmSelector value={values.farm_reference} onChange={onChange} />
      <Field label="Crop name" name="crop_name" required value={values.crop_name} onChange={onChange} maxLength={120} />
      <Field label="Planting date" name="planting_date" type="date" value={values.planting_date} onChange={onChange} />
      <Field label="Expected harvest date" name="expected_harvest_date" type="date" value={values.expected_harvest_date} onChange={onChange} />
      <Field label="Status" name="status" type="select" value={values.status} onChange={onChange}><option value="planned">Planned</option><option value="growing">Growing</option><option value="harvested">Harvested</option><option value="closed">Closed</option><option value="cancelled">Cancelled</option></Field>
      <Field label="Internal notes" name="internal_notes" type="textarea" value={values.internal_notes} onChange={onChange} />
    </div><ErrorMessage error={error} /><p className="operations-success" role="status">{success}</p><button className="auth-submit operations-submit" disabled={busy} type="submit">{busy ? 'Saving…' : editing ? 'Save changes' : 'Create season'}</button></form>
    <Link className="operations-back" to="/operations/crop-seasons"><ArrowLeft size={16} />Back to crop seasons</Link>
  </div>
}

export function CropSeasonCreatePage() { return <CropSeasonForm mode="create" /> }

export function CropSeasonEditPage() {
  const { reference } = useParams()
  const { user } = useAuth()
  const [record, setRecord] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    if (!permission(user, 'change', 'cropseason')) return
    authRequest(`operations/crop-seasons/${encodeURIComponent(reference)}/`).then(setRecord).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false))
  }, [reference, user])
  if (!permission(user, 'change', 'cropseason')) return <p className="ops-state">Your account does not have permission to edit crop seasons.</p>
  if (loading) return <p className="ops-state" role="status">Loading crop season…</p>
  if (error) return <ErrorMessage error={error} />
  return record ? <CropSeasonForm mode="edit" record={record} /> : <p className="ops-state">Crop season not found.</p>
}

export function CropSeasonDetailPage() {
  const { reference } = useParams()
  const { user } = useAuth()
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canView = permission(user, 'view', 'cropseason')
  const load = useCallback(async () => {
    if (!canView) return
    setLoading(true); setError('')
    try { setRecord(await authRequest(`operations/crop-seasons/${encodeURIComponent(reference)}/`)) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [canView, reference])
  useEffect(() => { Promise.resolve().then(load) }, [load])
  if (!canView) return <p className="ops-state">Your account does not have permission to view crop season details.</p>
  return <div><PageHeader eyebrow="Operations · Crop seasons" title="Crop season detail" description="Private season information and linked Farm record." refresh={load} />{loading && <p className="ops-state" role="status">Loading crop season…</p>}<ErrorMessage error={error} />{!loading && record && <section className="operations-detail-card"><dl><div><dt>Reference</dt><dd>{record.reference}</dd></div><div><dt>Farm</dt><dd><Link to={`/operations/farms/${encodeURIComponent(record.farm_reference)}`}>{record.farm_reference}</Link></dd></div><div><dt>Crop</dt><dd>{record.crop_name}</dd></div><div><dt>Planting date</dt><dd>{display(record.planting_date)}</dd></div><div><dt>Expected harvest</dt><dd>{display(record.expected_harvest_date)}</dd></div><div><dt>Status</dt><dd>{display(record.status)}</dd></div><div className="operations-detail-wide"><dt>Internal notes</dt><dd>{record.internal_notes || '—'}</dd></div></dl>{permission(user, 'change', 'cropseason') && <Link className="operations-primary-action" to={`/operations/crop-seasons/${encodeURIComponent(reference)}/edit`}><Edit3 size={16} />Edit season</Link>}</section>}<Link className="operations-back" to="/operations/crop-seasons"><ArrowLeft size={16} />Back to crop seasons</Link></div>
}
