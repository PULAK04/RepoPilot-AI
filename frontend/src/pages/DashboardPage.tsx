import { FormEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Nav from '../components/Nav'
import { api } from '../lib/api'
import type { Repository } from '../lib/types'

export default function DashboardPage() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [url, setUrl] = useState('https://github.com/')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function load() {
    const { data } = await api.get('/repositories')
    setRepos(data)
  }

  useEffect(() => { load(); const id = setInterval(load, 4000); return () => clearInterval(id) }, [])

  async function addRepo(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      await api.post('/repositories', { url })
      setUrl('https://github.com/')
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Could not add repository')
    } finally { setBusy(false) }
  }

  return <>
    <Nav />
    <main className="container">
      <section className="heroCard">
        <div>
          <div className="eyebrow">REPOSITORY INTELLIGENCE</div>
          <h1>Engineering answers grounded in <span>your code.</span></h1>
          <p>Import a GitHub repository, index it, then run RAG + multi-agent investigations.</p>
        </div>
        <div className="stats">
          <div><b>{repos.length}</b><span>Repositories</span></div>
          <div><b>{repos.filter(r => r.status === 'ready').length}</b><span>Indexed</span></div>
        </div>
      </section>

      <section className="grid2">
        <form className="card" onSubmit={addRepo}>
          <div className="sectionTitle">Connect repository</div>
          <p className="muted">Public GitHub repositories work without a token. Set <code>GITHUB_TOKEN</code> for private repositories or higher limits.</p>
          <label>GitHub URL<input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://github.com/owner/repo" /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={busy}>{busy ? 'Connecting…' : 'Import & index'}</button>
        </form>
        <div className="card architectureMini">
          <div className="sectionTitle">Agent architecture</div>
          <div className="flowRows"><span>Router</span><i>→</i><span>RAG research</span><i>→</i><span>Orchestrator</span></div>
          <div className="workers"><span>Code</span><span>API</span><span>DB</span><span>Tests</span></div>
          <div className="flowRows"><span>Reducer</span><i>→</i><span>Evaluator</span><i>→</i><span>Report</span></div>
        </div>
      </section>

      <section>
        <div className="sectionHeader"><div><div className="eyebrow">WORKSPACE</div><h2>Your repositories</h2></div></div>
        <div className="repoGrid">
          {repos.map(repo => <Link className="repoCard" to={`/repositories/${repo.id}`} key={repo.id}>
            <div className="repoTop"><div className="repoIcon">{'</>'}</div><span className={`status ${repo.status}`}>{repo.status}</span></div>
            <h3>{repo.owner} / {repo.name}</h3>
            <p>Branch <b>{repo.branch}</b> · {repo.file_count} indexed files</p>
            {repo.last_error && <div className="tinyError">{repo.last_error}</div>}
            <div className="open">Open workspace →</div>
          </Link>)}
          {!repos.length && <div className="empty card">No repositories yet. Import one above.</div>}
        </div>
      </section>
    </main>
  </>
}
