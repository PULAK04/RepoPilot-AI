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
        <label>Password<input value={password} onChange={e => setPassword(e.target.value)} type="password" minLength={6} required /></label>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? 'Working…' : mode === 'login' ? 'Sign in' : 'Register'}</button>
        <button className="linkButton" type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Need an account? Register' : 'Already registered? Sign in'}
        </button>
      </form>
    </main>
  )
}
