import { Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { authRequest } from '../api/auth.js'
import { useAuth } from '../auth/useAuth.js'

function errorText(error) {
  const fieldErrors = Object.values(error?.errors || {}).flat()
  return fieldErrors.length ? fieldErrors.join(' ') : error?.message || 'Please try again.'
}

function AuthFrame({ eyebrow, title, intro, children }) {
  return (
    <main className="auth-page" id="main-content">
      <section aria-labelledby="auth-title" className="auth-card">
        <p className="eyebrow">{eyebrow}</p>
        <h1 id="auth-title">{title}</h1>
        <p className="auth-intro">{intro}</p>
        {children}
      </section>
    </main>
  )
}

function PasswordField({ label, name, value, onChange, autoComplete }) {
  const [visible, setVisible] = useState(false)
  return (
    <label className="auth-field">
      <span>{label}</span>
      <span className="password-input-wrap">
        <input
          autoComplete={autoComplete}
          name={name}
          onChange={onChange}
          required
          type={visible ? 'text' : 'password'}
          value={value}
        />
        <button
          aria-label={visible ? 'Hide password' : 'Show password'}
          className="password-visibility"
          onClick={() => setVisible((shown) => !shown)}
          type="button"
        >
          {visible ? <EyeOff aria-hidden="true" size={18} /> : <Eye aria-hidden="true" size={18} />}
        </button>
      </span>
    </label>
  )
}

function Notice({ children, error = false }) {
  if (!children) return null
  return (
    <p aria-live="polite" className={`auth-notice${error ? ' auth-notice--error' : ''}`} role={error ? 'alert' : 'status'}>
      {children}
    </p>
  )
}

export function RegistrationPage() {
  const navigate = useNavigate()
  const [values, setValues] = useState({
    full_name: '',
    email: '',
    mobile_number: '',
    password: '',
    confirm_password: '',
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  function update(event) {
    setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = await authRequest('auth/register/', {
        method: 'POST',
        body: values,
      })
      const query = new URLSearchParams({
        challenge: result.challenge_id,
      })
      navigate(`/verify/email?${query}`)
    } catch (requestError) {
      setError(errorText(requestError))
      setBusy(false)
    }
  }

  return (
    <AuthFrame
      eyebrow="SPICEORA · Customer account"
      title="Create your account."
      intro="If your details are eligible, email verification instructions will be sent. Your mobile number remains unverified."
    >
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field">
          <span>Full name</span>
          <input autoComplete="name" maxLength="160" name="full_name" onChange={update} required value={values.full_name} />
        </label>
        <label className="auth-field">
          <span>Email address</span>
          <input autoComplete="email" maxLength="254" name="email" onChange={update} required type="email" value={values.email} />
        </label>
        <label className="auth-field">
          <span>Mobile number with country code (unverified)</span>
          <input autoComplete="tel" inputMode="tel" name="mobile_number" onChange={update} placeholder="+14155552671" required value={values.mobile_number} />
        </label>
        <p className="auth-help">Your mobile number will be stored as unverified. SPICEORA does not send SMS verification codes.</p>
        <PasswordField autoComplete="new-password" label="Password" name="password" onChange={update} value={values.password} />
        <PasswordField autoComplete="new-password" label="Confirm password" name="confirm_password" onChange={update} value={values.confirm_password} />
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy} type="submit">
          Create account
        </button>
      </form>
      <p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p>
    </AuthFrame>
  )
}

export function VerificationPage({ channel }) {
  const [query] = useSearchParams()
  const navigate = useNavigate()
  const challengeId = query.get('challenge') || ''
  const [code, setCode] = useState('')
  const [seconds, setSeconds] = useState(60)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!seconds) return undefined
    const timer = window.setTimeout(() => {
      setSeconds((value) => Math.max(0, value - 1))
    }, 1000)
    return () => window.clearTimeout(timer)
  }, [seconds])

  if (channel === 'mobile') {
    return (
      <AuthFrame
        eyebrow="SPICEORA · Mobile verification"
        title="Mobile verification is pending."
        intro="SMS verification is not available in the current zero-budget configuration. Your mobile number remains unverified."
      >
        <Link className="auth-submit auth-submit--link" to="/login">Continue to sign in</Link>
      </AuthFrame>
    )
  }

  if (!challengeId) {
    return (
      <AuthFrame eyebrow="SPICEORA · Verification" title="Verification link unavailable." intro="Return to registration to create a new verification request.">
        <Link className="auth-submit auth-submit--link" to="/register">Return to registration</Link>
      </AuthFrame>
    )
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const route = channel === 'email' ? 'auth/verify/email/' : 'auth/verify/mobile/'
      const result = await authRequest(route, {
        method: 'POST',
        body: { challenge_id: challengeId, code },
      })
      navigate(`/login?verified=${result.account_active ? '1' : '0'}`)
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  async function resend() {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const result = await authRequest('auth/verify/resend/', {
        method: 'POST',
        body: { challenge_id: challengeId },
      })
      setSeconds(60)
      setMessage(result.message)
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthFrame
      eyebrow={`SPICEORA · ${channel} verification`}
      title={`Verify your ${channel}.`}
      intro="Enter a six-digit code if you received one. Successful email verification activates an eligible account; your mobile number remains unverified."
    >
      <div className="verification-status">
        <span className="verification-step verification-step--done"><ShieldCheck aria-hidden="true" size={18} /> Account details submitted</span>
        <span className={`verification-step${channel === 'email' ? ' verification-step--current' : ' verification-step--done'}`}>Email verification</span>
        <span>Mobile number · unverified</span>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field">
          <span>Six-digit code</span>
          <input autoComplete="one-time-code" inputMode="numeric" maxLength="6" name="code" onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} pattern="[0-9]{6}" required value={code} />
        </label>
        <Notice>{message}</Notice>
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy || code.length !== 6} type="submit">
          {busy ? 'Verifying…' : `Verify ${channel}`}
        </button>
        <button className="auth-secondary" disabled={busy || seconds > 0} onClick={resend} type="button">
          {seconds > 0 ? `Resend code in ${seconds}s` : 'Resend code'}
        </button>
      </form>
    </AuthFrame>
  )
}

export function LoginPage({ audience = 'customer' }) {
  const { user, ready, signIn } = useAuth()
  const navigate = useNavigate()
  const [values, setValues] = useState({ identity: '', password: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [query] = useSearchParams()

  if (!ready) return <AuthFrame eyebrow="SPICEORA" title="Checking your session." intro="One moment." />
  if (user) {
    return <Navigate replace to={user.role === 'staff' ? '/operations' : '/'} />
  }

  function update(event) {
    setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await signIn(values.identity, values.password, audience)
      navigate(audience === 'staff' ? '/operations' : '/', { replace: true })
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthFrame
      eyebrow={audience === 'staff' ? 'SPICEORA · Staff access' : 'SPICEORA · Customer account'}
      title={audience === 'staff' ? 'Operations sign in.' : 'Welcome back.'}
      intro={audience === 'staff' ? 'Use an administrator-authorized staff account. Customer registration cannot grant staff access.' : 'Sign in with your verified email address.'}
    >
      {query.get('verified') === '1' && <Notice>Your email is verified and your account is active. Your mobile number remains unverified because SMS verification is currently unavailable.</Notice>}
      {query.get('verified') === '0' && <Notice error>Email verification is not complete. Verify your email before signing in.</Notice>}
      {query.get('reset') === '1' && <Notice>Your password was reset. Sign in with your new password.</Notice>}
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field">
          <span>Email address</span>
          <input autoComplete="username" name="identity" onChange={update} required value={values.identity} />
        </label>
        <PasswordField autoComplete="current-password" label="Password" name="password" onChange={update} value={values.password} />
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy} type="submit">{busy ? 'Signing in…' : 'Sign in'}</button>
      </form>
      {audience === 'customer' ? (
        <p className="auth-switch"><Link to="/forgot-password">Forgot your password?</Link><br />New to SPICEORA? <Link to="/register">Create a customer account</Link></p>
      ) : (
        <p className="auth-switch"><Link to="/login">Customer sign in</Link></p>
      )}
    </AuthFrame>
  )
}

export function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [identity, setIdentity] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = await authRequest('auth/recovery/start/', {
        method: 'POST',
        body: { identity },
      })
      navigate(`/forgot-password/verify?${new URLSearchParams({
        flow: result.flow_id,
      })}`)
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthFrame eyebrow="SPICEORA · Account recovery" title="Reset your password." intro="Recovery codes are sent to the registered email address. For privacy, the same confirmation is shown whether or not an account matches.">
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field">
          <span>Email address</span>
          <input autoComplete="email" onChange={(event) => setIdentity(event.target.value)} required type="email" value={identity} />
        </label>
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy} type="submit">{busy ? 'Requesting…' : 'Send recovery code'}</button>
      </form>
      <p className="auth-switch"><Link to="/login">Return to sign in</Link></p>
    </AuthFrame>
  )
}

export function RecoveryVerificationPage() {
  const [query] = useSearchParams()
  const navigate = useNavigate()
  const flow = query.get('flow') || ''
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = await authRequest('auth/recovery/verify/', {
        method: 'POST',
        body: { challenge_id: flow, code },
      })
      navigate(`/new-password?${new URLSearchParams({ flow: result.flow_id })}`)
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthFrame eyebrow="SPICEORA · Account recovery" title="Enter your recovery code." intro="If the details match an active account, a code was sent to its registered email address.">
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field">
          <span>Six-digit code</span>
          <input autoComplete="one-time-code" inputMode="numeric" maxLength="6" onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} pattern="[0-9]{6}" required value={code} />
        </label>
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy || code.length !== 6} type="submit">{busy ? 'Verifying…' : 'Verify code'}</button>
      </form>
      <p className="auth-switch"><Link to="/forgot-password">Request another code</Link></p>
    </AuthFrame>
  )
}

export function NewPasswordPage() {
  const [query] = useSearchParams()
  const navigate = useNavigate()
  const [values, setValues] = useState({ password: '', confirm_password: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await authRequest('auth/recovery/reset/', {
        method: 'POST',
        body: { flow_id: query.get('flow'), ...values },
      })
      navigate('/login?reset=1', { replace: true })
    } catch (requestError) {
      setError(errorText(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthFrame eyebrow="SPICEORA · Account recovery" title="Choose a new password." intro="Your verified recovery code is single-use and expires after five minutes.">
      <form className="auth-form" onSubmit={submit}>
        <PasswordField autoComplete="new-password" label="New password" name="password" onChange={(event) => setValues((current) => ({ ...current, password: event.target.value }))} value={values.password} />
        <PasswordField autoComplete="new-password" label="Confirm new password" name="confirm_password" onChange={(event) => setValues((current) => ({ ...current, confirm_password: event.target.value }))} value={values.confirm_password} />
        <Notice error>{error}</Notice>
        <button className="auth-submit" disabled={busy} type="submit">{busy ? 'Updating…' : 'Set new password'}</button>
      </form>
    </AuthFrame>
  )
}
