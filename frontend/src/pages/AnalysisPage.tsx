import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Nav from '../components/Nav'
import ProgressTimeline from '../components/ProgressTimeline'
import { api, WS_URL } from '../lib/api'
import type { Analysis } from '../lib/types'

function Evidence({ items }: { items: any[] }) {
  return <div className="evidenceList">{items?.map((e, i) => <details className="evidence" key={`${e.path}-${i}`}>
    <summary><b>{e.path}</b><span>lines {e.start_line}-{e.end_line} · score {e.score}</span></summary>
    <pre>{e.snippet}</pre>
  </details>)}</div>
}

export default function AnalysisPage() {
  const { analysisId } = useParams()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [live, setLive] = useState<{progress:number, step:string} | null>(null)

  async function load() { const { data } = await api.get(`/analyses/${analysisId}`); setAnalysis(data) }
  useEffect(() => { load() }, [analysisId])
  useEffect(() => {
    const token = localStorage.getItem('repopilot_token') || ''
    const ws = new WebSocket(`${WS_URL}/analyses/${analysisId}?token=${encodeURIComponent(token)}`)
    ws.onmessage = (e) => { const d = JSON.parse(e.data); setLive(d); if (d.progress === 100 || d.status === 'failed') load() }
    const id = setInterval(load, 5000)
    return () => { ws.close(); clearInterval(id) }
  }, [analysisId])

  const progress = live?.progress ?? analysis?.progress ?? 0
  const current = live?.step ?? analysis?.current_step ?? 'Loading'
  const r: any = analysis?.result_json

  return <>
    <Nav />
    <main className="container">
      {analysis && <Link className="back" to={`/repositories/${analysis.repo_id}`}>← Repository workspace</Link>}
      <section className="analysisTitle">
        <div><div className="eyebrow">{analysis?.kind?.replace('_',' ').toUpperCase()}</div><h1>Engineering analysis <span>#{analysisId}</span></h1><p>{analysis?.question}</p></div>
        <span className={`status bigStatus ${analysis?.status}`}>{analysis?.status}</span>
      </section>

      <ProgressTimeline progress={progress} current={current} />
      {analysis?.error && <div className="error card">{analysis.error}</div>}

      {r && <section className="report">
        <div className="grid2">
          <div className="card"><div className="sectionTitle">Summary</div><p className="reportText">{r.summary}</p></div>
          <div className="card scoreCard"><div className="sectionTitle">Evaluator</div><div className="confidence">{Math.round((r.evaluation?.confidence || 0) * 100)}<small>%</small></div><p>{r.evaluation?.passed ? 'Grounding check passed' : 'Returned with caveats'}</p><span className="muted">{r.evaluation?.reason}</span></div>
        </div>
        <div className="card"><div className="sectionTitle">Root cause / conclusion</div><p className="reportText emphasis">{r.root_cause}</p></div>
        <div className="card"><div className="sectionTitle">Suggested fix</div><p className="reportText">{r.suggested_fix}</p>{r.optional_patch && <pre className="patch">{r.optional_patch}</pre>}</div>
        <div className="card"><div className="sectionTitle">Specialist findings</div><div className="findingGrid">{r.findings?.map((f:any,i:number) => <div className="finding" key={i}><div className="findingTop"><b>{f.task || `Finding ${i+1}`}</b><span className={`severity ${f.severity}`}>{f.severity || 'info'}</span></div><p>{f.summary}</p><small>confidence {Math.round((f.confidence || 0)*100)}%</small></div>)}</div></div>
        <div className="card"><div className="sectionTitle">Repository evidence</div><Evidence items={r.evidence || []} /></div>
      </section>}
    </main>
  </>
}
