const steps = [
  ['Router', 10],
  ['RAG Research', 25],
  ['Orchestrator', 38],
  ['Specialist Workers', 55],
  ['Reducer / Fix', 72],
  ['Evaluator', 86],
  ['Final Report', 96],
]

export default function ProgressTimeline({ progress, current }: { progress: number, current: string }) {
  return (
    <div className="timeline card">
      <div className="sectionTitle">Live agent execution</div>
      <div className="currentStep">{current}</div>
      <div className="progress"><span style={{ width: `${progress}%` }} /></div>
      <div className="steps">
        {steps.map(([name, at]) => {
          const done = progress >= Number(at)
          const active = !done && progress >= Number(at) - 15
          return <div className={`step ${done ? 'done' : active ? 'active' : ''}`} key={String(name)}>
            <span className="dot">{done ? '✓' : active ? '●' : '○'}</span>
            <span>{name}</span>
          </div>
        })}
      </div>
    </div>
  )
}
