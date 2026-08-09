import { FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Nav from '../components/Nav'
import { api } from '../lib/api'
import type { Analysis, Repository } from '../lib/types'

const prompts = {
  ask: 'Explain how authentication works and trace the files involved.',
  bug: 'Describe the bug, observed behavior, expected behavior, and any error message.',
  code_review: 'Review this repository for the highest-impact correctness, maintainability, security and performance issues.',
  architecture: 'Explain the application architecture, major modules, data flow, integrations and scaling risks.',
  tests: 'Generate a focused test plan and implementation-ready tests for the highest-risk code paths in this repository.',
  performance: 'Find the most important performance bottlenecks, repeated work, database/API inefficiencies and caching opportunities.',
}

export default function RepositoryPage() {
  const { repoId } = useParams(); const navigate = useNavigate()
  const [repo, setRepo] = useState<Repository | null>(null)
  const [history, setHistory] = useState<Analysis[]>([])
  const [kind, setKind] = useState<keyof typeof prompts>('bug')
  const [question, setQuestion] = useState(prompts.bug)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function load() {
    const [r, h] = await Promise.all([api.get(`/repositories/${repoId}`), api.get('/analyses', { params: { repo_id: repoId } })])
    setRepo(r.data); setHistory(h.data)
  }
  useEffect(() => { load(); const id = setInterval(load, 4000); return () => clearInterval(id) }, [repoId])

  async function start(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      const { data } = await api.post('/analyses', { repo_id: Number(repoId), kind, question })
      navigate(`/analyses/${data.id}`)
    } catch (err: any) { setError(err?.response?.data?.detail || 'Could not start analysis') }
    finally { setBusy(false) }
  }

  return <>
    <Nav />
    <main className="container">
      <Link className="back" to="/">← All repositories</Link>
      <section className="repoHeader card">
        <div><div className="eyebrow">REPOSITORY</div><h1>{repo?.owner} / <span>{repo?.name}</span></h1><p>{repo?.url}</p></div>
        <div className={`status bigStatus ${repo?.status}`}>{repo?.status || 'loading'}</div>
      </section>

      <section className="grid2 workspaceGrid">
        <form className="card" onSubmit={start}>
          <div className="sectionTitle">Start engineering analysis</div>
          <div className="tabs">
            {(Object.keys(prompts) as Array<keyof typeof prompts>).map(k => <button type="button" className={kind === k ? 'tab active' : 'tab'} onClick={() => { setKind(k); setQuestion(prompts[k]) }} key={k}>{k.replace('_',' ')}</button>)}
          </div>
          <label>Task / question<textarea rows={9} value={question} onChange={e => setQuestion(e.target.value)} /></label>
          {repo?.status !== 'ready' && <div className="notice">Repository must finish indexing before analysis.</div>}
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={busy || repo?.status !== 'ready'}>{busy ? 'Starting…' : 'Run multi-agent analysis'}</button>
        </form>

        <div className="card">
          <div className="sectionTitle">Repository index</div>
          <div className="metricList"><div><span>Status</span><b>{repo?.status}</b></div><div><span>Branch</span><b>{repo?.branch}</b></div><div><span>Indexed files</span><b>{repo?.file_count}</b></div></div>
          <button className="ghost full" onClick={async () => { await api.post(`/repositories/${repoId}/reindex`); load() }}>Re-index repository</button>
          {repo?.last_error && <div className="error">{repo.last_error}</div>}
        </div>
      </section>

      <section>
        <div className="sectionHeader"><div><div className="eyebrow">HISTORY</div><h2>Previous analyses</h2></div></div>
        <div className="historyList">
          {history.map(a => <Link to={`/analyses/${a.id}`} className="historyItem" key={a.id}>
            <span className="kindBadge">{a.kind.replace('_',' ')}</span><div className="historyBody"><b>{a.question}</b><small>{new Date(a.created_at).toLocaleString()}</small></div><span className={`status ${a.status}`}>{a.status}</span>
          </Link>)}
          {!history.length && <div className="empty card">No analyses yet.</div>}
        </div>
      </section>
    </main>
  </>
}
