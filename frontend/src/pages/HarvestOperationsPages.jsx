import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, Edit3, Eye, Plus, RefreshCw } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { authRequest } from '../api/auth.js'
import { useAuth } from '../auth/useAuth.js'

const display = (value) => value === null || value === undefined || value === '' ? '—' : String(value)
const hasPermission = (user, action, model) => Boolean(user?.permissions?.includes(`api.${action}_${model}`))
const CLOSED = new Set(['closed', 'cancelled'])

function Pagination({ payload, page, onPage }) {
  if (!payload) return null
  if (!payload.previous && !payload.next) return null
  return <div className="operations-pagination" aria-label="Pagination"><button className="operations-pagination-button" disabled={!payload.previous} onClick={() => onPage(page - 1)} type="button">Previous</button><span>Page {page}</span><button className="operations-pagination-button" disabled={!payload.next} onClick={() => onPage(page + 1)} type="button">Next</button></div>
}

function ErrorMessage({ error }) { return error ? <p className="auth-notice auth-notice--error" role="alert">{error}</p> : null }

function PageHeader({ title, description, action, actionLabel, refresh }) {
  return <div className="operations-title-row"><div><p className="eyebrow">Operations · Traceability</p><h1>{title}</h1><p>{description}</p></div><div className="operations-header-actions">{refresh && <button aria-label="Refresh list" className="operations-refresh" onClick={refresh} type="button"><RefreshCw aria-hidden="true" size={16} />Refresh</button>}{action && <Link className="operations-primary-action" to={action}><Plus aria-hidden="true" size={16} />{actionLabel}</Link>}</div></div>
}

function useFarmSelector(value, onChange) {
  const [farms, setFarms] = useState([])
  const [page, setPage] = useState(1)
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = useCallback(async (nextPage = 1) => {
    setLoading(true); setError('')
    try { const result = await authRequest(`operations/farms/?page=${nextPage}`); setFarms(result.results || []); setPayload(result); setPage(nextPage) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { Promise.resolve().then(() => load(1)) }, [load])
  return { farms, page, payload, loading, error, load, value, onChange }
}

function FarmSelector({ value, onChange, excludeClosed = false, disabled = false }) {
  const selector = useFarmSelector(value, onChange, { excludeClosed })
  const selectedOnPage = selector.farms.some((farm) => farm.reference === value)
  return <div className="farm-selector"><label className="auth-field"><span>Farm</span><select aria-label="Farm" name="farm_reference" value={value ?? ''} onChange={onChange} required disabled={disabled || selector.loading || selector.farms.length === 0}><option value="">{selector.loading ? 'Loading farms…' : selector.farms.length === 0 ? 'No farms available' : 'Choose a farm'}</option>{!selectedOnPage && value ? <option value={value}>{value}</option> : null}{selector.farms.map((farm) => <option key={farm.reference} value={farm.reference}>{farm.name || farm.reference} — {farm.reference}</option>)}</select></label>{selector.loading && <p className="operations-help" role="status">Loading authorized farms…</p>}<ErrorMessage error={selector.error} /><Pagination payload={selector.payload} page={selector.page} onPage={selector.load} /></div>
}

function SeasonSelector({ farmReference, value, onChange, excludeClosed = true, label = 'Crop season', disabled = false }) {
  const [seasons, setSeasons] = useState([])
  const [page, setPage] = useState(1)
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const load = useCallback(async (nextPage = 1) => {
    if (!farmReference) { setSeasons([]); setPayload(null); setError(''); setLoading(false); return }
    setLoading(true); setError('')
    try { const params = new URLSearchParams({ farm_reference: farmReference, page: String(nextPage), eligible_for_harvest: excludeClosed ? 'true' : 'false' }); const result = await authRequest(`operations/crop-seasons/?${params}`); setSeasons((result.results || []).filter((season) => !excludeClosed || !CLOSED.has(season.status))); setPayload(result); setPage(nextPage) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [farmReference, excludeClosed])
  useEffect(() => { Promise.resolve().then(() => load(1)) }, [load])
  const selectedOnPage = seasons.some((season) => season.reference === value)
  return <div className="farm-selector"><label className="auth-field"><span>{label}</span><select aria-label={label} name="crop_season_reference" value={value ?? ''} onChange={onChange} required disabled={disabled || !farmReference || loading || seasons.length === 0}><option value="">{!farmReference ? 'Choose a farm first' : loading ? 'Loading crop seasons…' : seasons.length === 0 ? 'No eligible crop seasons' : 'Choose a crop season'}</option>{!selectedOnPage && value ? <option value={value}>{value}</option> : null}{seasons.map((season) => <option key={season.reference} value={season.reference}>{season.crop_name || season.reference} — {season.reference}</option>)}</select></label>{loading && <p className="operations-help" role="status">Loading crop seasons…</p>}<ErrorMessage error={error} /><Pagination payload={payload} page={page} onPage={load} /></div>
}

export function HarvestListPage() {
  const { user } = useAuth(); const navigate = useNavigate()
  const [rows, setRows] = useState([]); const [payload, setPayload] = useState(null); const [page, setPage] = useState(1)
  const [farmReference, setFarmReference] = useState(''); const [seasonReference, setSeasonReference] = useState('')
  const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const canView = hasPermission(user, 'view', 'harvest'); const canAdd = hasPermission(user, 'add', 'harvest')
  const load = useCallback(async (nextPage = page) => {
    if (!canView) return
    setLoading(true); setError('')
    const params = new URLSearchParams({ page: String(nextPage) })
    if (farmReference) params.set('farm_reference', farmReference)
    if (seasonReference) params.set('crop_season_reference', seasonReference)
    try { const result = await authRequest(`operations/harvests/?${params}`); setRows(result.results || []); setPayload(result); setPage(nextPage) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [canView, farmReference, seasonReference, page])
  useEffect(() => { Promise.resolve().then(() => load(page)) }, [load, page])
  if (!canView) return <p className="ops-state">Your account does not have permission to view harvests.</p>
  return <div className="operations-list-page"><PageHeader title="Harvests" description="Recorded harvest quantities and crop-season lineage." action={canAdd ? '/operations/harvests/new' : null} actionLabel="Add harvest" refresh={() => load(page)} /><div className="operations-form-grid"><label className="auth-field"><span>Farm reference</span><input aria-label="Farm filter" name="farm_filter" value={farmReference} onChange={(event) => { setFarmReference(event.target.value); setSeasonReference('') }} placeholder="Farm reference" /></label><label className="auth-field"><span>Crop season reference</span><input aria-label="Crop season filter" name="season_filter" value={seasonReference} onChange={(event) => setSeasonReference(event.target.value)} placeholder="Crop season reference" /></label></div><button className="auth-submit operations-submit" type="button" onClick={() => { setPage(1); load(1) }}>Apply filters</button><ErrorMessage error={error} />{loading && <p className="ops-state" role="status">Loading harvests…</p>}{!loading && !error && rows.length === 0 && <p className="ops-state">No harvests recorded yet.</p>}{!loading && rows.length > 0 && <div className="operations-table-wrap"><table className="operations-table"><thead><tr><th>Reference</th><th>Crop season</th><th>Harvest date</th><th>Quantity</th><th>Unit</th><th>Actions</th></tr></thead><tbody>{rows.map((row) => <tr key={row.reference}><td>{row.reference}</td><td>{row.crop_season_reference}</td><td>{display(row.harvest_date)}</td><td>{display(row.quantity)}</td><td>{display(row.quantity_unit)}</td><td><div className="operations-row-actions"><Link aria-label={`View ${row.reference}`} to={`/operations/harvests/${encodeURIComponent(row.reference)}`}><Eye size={15} />View</Link>{hasPermission(user, 'change', 'harvest') && <Link aria-label={`Edit ${row.reference}`} to={`/operations/harvests/${encodeURIComponent(row.reference)}/edit`}><Edit3 size={15} />Edit</Link>}</div></td></tr>)}</tbody></table></div>}<Pagination payload={payload} page={page} onPage={load} /><button className="operations-back-button" onClick={() => navigate('/operations')} type="button"><ArrowLeft size={16} />Back to operations</button></div>
}

function HarvestForm({ mode, record = null }) {
  const navigate = useNavigate(); const { user } = useAuth(); const editing = mode === 'edit'
  const allowed = editing ? hasPermission(user, 'change', 'harvest') : hasPermission(user, 'add', 'harvest')
  const [values, setValues] = useState({ reference: record?.reference || '', crop_season_reference: record?.crop_season_reference || '', harvest_date: record?.harvest_date || '', quantity: record?.quantity ?? '', quantity_unit: record?.quantity_unit || 'kg', notes: record?.notes || '' })
  const [farmReference, setFarmReference] = useState(record?.farm_reference || '')
  const [busy, setBusy] = useState(false); const [error, setError] = useState(''); const [success, setSuccess] = useState('')
  const historicalLocked = Boolean(record?.historical_locked)
  if (!allowed) return <p className="ops-state">Your account does not have permission to {editing ? 'edit' : 'create'} harvests.</p>
  const onChange = (event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setSuccess('')
    const payload = { ...values }
    if (editing && historicalLocked) { delete payload.reference; delete payload.crop_season_reference; delete payload.harvest_date; delete payload.quantity; delete payload.quantity_unit }
    if (!payload.reference) delete payload.reference
    try { if (editing) { await authRequest(`operations/harvests/${encodeURIComponent(record.reference)}/`, { method: 'PATCH', body: payload }); setSuccess('Harvest updated.') } else { await authRequest('operations/harvests/', { method: 'POST', body: payload }); setSuccess('Harvest created.'); navigate('/operations/harvests') } }
    catch (requestError) { setError(Object.values(requestError.errors || {}).flat().join(' ') || requestError.message) }
    finally { setBusy(false) }
  }
  return <div className="operations-list-page"><PageHeader title={editing ? 'Edit harvest' : 'Add harvest'} description="Link each harvest to an authorized farm and crop season." /><form className="operations-form" onSubmit={submit}><div className="operations-form-grid"><label className="auth-field"><span>Harvest reference</span><input name="reference" required={!editing} readOnly={editing || historicalLocked} value={values.reference} onChange={onChange} /></label><div><FarmSelector value={farmReference} disabled={historicalLocked} onChange={(event) => { setFarmReference(event.target.value); setValues((current) => ({ ...current, crop_season_reference: '' })) }} /><SeasonSelector farmReference={farmReference} value={values.crop_season_reference} onChange={onChange} excludeClosed={editing ? (!historicalLocked && !record?.season_closed) : true} disabled={historicalLocked} /></div><label className="auth-field"><span>Harvest date</span><input name="harvest_date" type="date" required readOnly={historicalLocked} value={values.harvest_date} onChange={onChange} /></label><label className="auth-field"><span>Quantity</span><input name="quantity" type="number" min="0.001" step="0.001" required readOnly={historicalLocked} value={values.quantity} onChange={onChange} /></label><label className="auth-field"><span>Unit</span><select name="quantity_unit" required disabled={historicalLocked} value={values.quantity_unit} onChange={onChange}><option value="kg">Kilograms</option><option value="metric_tonne">Metric tonnes</option></select></label><label className="auth-field auth-field--wide"><span>Notes</span><textarea name="notes" value={values.notes} onChange={onChange} /></label></div>{historicalLocked && <p className="operations-help">This historical harvest is linked to a production batch. Origin, date and quantity fields cannot change; notes remain editable.</p>}<ErrorMessage error={error} />{success && <p className="operations-success" role="status">{success}</p>}<button className="auth-submit operations-submit" disabled={busy} type="submit">{busy ? 'Saving…' : editing ? 'Save changes' : 'Create harvest'}</button></form><button className="operations-back-button" onClick={() => navigate('/operations/harvests')} type="button"><ArrowLeft size={16} />Back to harvests</button></div>
}

export function HarvestCreatePage() { return <HarvestForm mode="create" /> }
export function HarvestEditPage() {
  const { reference } = useParams(); const { user } = useAuth(); const [record, setRecord] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  useEffect(() => { if (!hasPermission(user, 'change', 'harvest')) return; authRequest(`operations/harvests/${encodeURIComponent(reference)}/`).then(async (harvest) => { try { const season = await authRequest(`operations/crop-seasons/${encodeURIComponent(harvest.crop_season_reference)}/`); setRecord({ ...harvest, farm_reference: season.farm_reference, season_closed: ['closed', 'cancelled'].includes(season.status) }) } catch (requestError) { setError(requestError.message) } }).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false)) }, [reference, user])
  if (!hasPermission(user, 'change', 'harvest')) return <p className="ops-state">Your account does not have permission to edit harvests.</p>
  if (loading) return <p className="ops-state" role="status">Loading harvest…</p>; if (error) return <ErrorMessage error={error} />; return record ? <HarvestForm mode="edit" record={record} /> : <p className="ops-state">Harvest not found.</p>
}

export function HarvestDetailPage() {
  const { reference } = useParams(); const { user } = useAuth(); const navigate = useNavigate(); const [harvest, setHarvest] = useState(null); const [season, setSeason] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const load = useCallback(async () => { if (!hasPermission(user, 'view', 'harvest')) return; setLoading(true); setError(''); try { const result = await authRequest(`operations/harvests/${encodeURIComponent(reference)}/`); setHarvest(result); const seasonResult = await authRequest(`operations/crop-seasons/${encodeURIComponent(result.crop_season_reference)}/`); setSeason(seasonResult) } catch (requestError) { setError(requestError.message) } finally { setLoading(false) } }, [reference, user])
  useEffect(() => { Promise.resolve().then(load) }, [load])
  if (!hasPermission(user, 'view', 'harvest')) return <p className="ops-state">Your account does not have permission to view harvest details.</p>
  return <div><PageHeader title="Harvest detail" description="Private harvest quantity and lineage information." refresh={load} />{loading && <p className="ops-state" role="status">Loading harvest…</p>}<ErrorMessage error={error} />{!loading && harvest && <section className="operations-detail-card"><dl><div><dt>Reference</dt><dd>{harvest.reference}</dd></div><div><dt>Farm</dt><dd>{season?.farm_reference || '—'}</dd></div><div><dt>Crop season</dt><dd>{harvest.crop_season_reference}</dd></div><div><dt>Harvest date</dt><dd>{display(harvest.harvest_date)}</dd></div><div><dt>Quantity</dt><dd>{display(harvest.quantity)}</dd></div><div><dt>Unit</dt><dd>{display(harvest.quantity_unit)}</dd></div><div className="operations-detail-wide"><dt>Notes</dt><dd>{harvest.notes || '—'}</dd></div><div className="operations-detail-wide"><dt>Historical protection</dt><dd>{harvest.historical_locked ? 'Locked after production batch' : 'Origin and quantity fields editable'}</dd></div></dl>{hasPermission(user, 'change', 'harvest') && <Link className="operations-primary-action" to={`/operations/harvests/${encodeURIComponent(reference)}/edit`}><Edit3 size={16} />Edit harvest</Link>}</section>}<button className="operations-back-button" onClick={() => navigate('/operations/harvests')} type="button"><ArrowLeft size={16} />Back to harvests</button></div>
}
