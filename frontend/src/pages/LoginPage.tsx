import { FormEvent, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import { api } from '../lib/api'
import { setToken, type RootState } from '../store'

export default function LoginPage() {
  const token = useSelector((s: RootState) => s.auth.token)
  const dispatch = useDispatch()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('demo@repopilot.dev')
  const [password, setPassword] = useState('password123')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  if (token) return <Navigate to="/" replace />

  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      const { data } = await api.post(`/auth/${mode}`, { email, password })
      dispatch(setToken(data.access_token))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Request failed')
    } finally { setBusy(false) }
  }

  return (
    <main className="authShell">
      <section className="authHero">
        <div className="eyebrow">AI-NATIVE SOFTWARE ENGINEERING</div>
        <h1>Understand a codebase.<br/><span>Investigate it like an engineer.</span></h1>
        <p>RepoPilot routes software questions through repository research, specialist agents, synthesis and an evaluator loop.</p>
        <div className="miniFlow"><b>Router</b><i>→</i><b>RAG</b><i>→</i><b>Workers</b><i>→</i><b>Evaluator</b></div>
      </section>
      <form className="authCard" onSubmit={submit}>
        <div className="brand big"><span className="brandMark">RP</span> RepoPilot AI</div>
        <h2>{mode === 'login' ? 'Welcome back' : 'Create account'}</h2>
        <label>Email<input value={email} onChange={e => setEmail(e.target.value)} type="email" required /></label>
        <label>
  Password
  <div className="passwordField">
    <input
      value={password}
      onChange={e => setPassword(e.target.value)}
      type={showPassword ? 'text' : 'password'}
      minLength={6}
      required
    />

    <button
      type="button"
      className="passwordToggle"
      onClick={() => setShowPassword(prev => !prev)}
      aria-label={showPassword ? 'Hide password' : 'Show password'}
      title={showPassword ? 'Hide password' : 'Show password'}
    >
      {showPassword ? (
        // Eye off
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M3 3l18 18" />
          <path d="M10.6 10.6a3 3 0 0 0 4.2 4.2" />
          <path d="M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.7 4 10 8-0.4 1.2-1.2 2.7-2.4 4" />
          <path d="M6.6 6.6C4.7 7.8 3.3 9.7 2 12c1.3 3.2 5 7 10 7a10 10 0 0 0 3.2-.5" />
        </svg>
      ) : (
        // Eye
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      )}
    </button>
  </div>
</label>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? 'Working…' : mode === 'login' ? 'Sign in' : 'Register'}</button>
        <button className="linkButton" type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Need an account? Register' : 'Already registered? Sign in'}
        </button>
      </form>
    </main>
  )
}
