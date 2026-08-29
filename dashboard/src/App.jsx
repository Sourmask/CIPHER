import { useCallback, useEffect, useState } from 'react'
import './App.css'

const score = (value) => Number(value || 0).toFixed(1)

function NetworkView({ selected, people, edges, onSelect }) {
  const links = edges.filter((e) => e.source === selected.person_id || e.target === selected.person_id).sort((a, b) => b.count - a.count).slice(0, 12)
  const ids = [selected.person_id, ...links.map((e) => e.source === selected.person_id ? e.target : e.source)]
  const nodes = ids.map((id) => people.find((p) => p.person_id === id)).filter(Boolean)
  const center = { x: 290, y: 190 }
  const positions = Object.fromEntries(nodes.map((node, index) => {
    if (!index) return [node.person_id, center]
    const angle = (Math.PI * 2 * (index - 1)) / Math.max(nodes.length - 1, 1) - Math.PI / 2
    return [node.person_id, { x: center.x + Math.cos(angle) * 135, y: center.y + Math.sin(angle) * 130 }]
  }))
  return <div className="network-wrap"><svg className="network" viewBox="0 0 580 380" role="img" aria-label={`Relationship network centered on ${selected.name}`}>
    {links.map((e) => <line key={`${e.source}-${e.target}`} x1={positions[e.source].x} y1={positions[e.source].y} x2={positions[e.target].x} y2={positions[e.target].y} />)}
    {nodes.map((node, index) => <g key={node.person_id} className={`network-node ${index === 0 ? 'focus' : ''}`} onClick={() => onSelect(node.person_id)}><circle cx={positions[node.person_id].x} cy={positions[node.person_id].y} r={index === 0 ? 32 : 22} /><text x={positions[node.person_id].x} y={positions[node.person_id].y + 4}>{node.person_id}</text></g>)}
  </svg><p className="muted">Person-to-person relationships are aggregated. Select a connected entity to inspect its evidence.</p></div>
}

function Timeline({ events }) {
  const visible = (events || []).slice(0, 12)
  return <div className="timeline">{visible.length ? visible.map((event, index) => <article key={`${event.timestamp}-${index}`}><i className={event.relationship.toLowerCase()} /><div><b>{event.relationship.replace('_', ' ')}</b><p>{event.counterparty ? `Connected with ${event.counterparty}` : `Evidence source ${event.report_id || 'record'}`}{event.amount ? ` · ₹${Number(event.amount).toLocaleString()}` : ''}</p><small>{event.timestamp.replace('T', ' ')}</small></div></article>) : <p className="muted">No dated source events available.</p>}</div>
}

function TransactionFlow({ patterns }) {
  const flow = patterns.layering_chains[0] || patterns.transaction_cycles[0]
  const path = flow ? (flow.chain || flow.cycle).split(' -> ') : []
  return <div className="flow"><div className="flow-row">{path.map((person, index) => <div className="flow-step" key={`${person}-${index}`}><b>{person}</b>{index < path.length - 1 && <span>→</span>}</div>)}</div><p className="muted">{flow?.chain ? 'Rapid, declining high-value transfer chain.' : 'Rapid comparable-value circular transfer flow.'}</p></div>
}

function CommunityView({ people, selected, onSelect }) {
  const communities = [...new Set(people.map((person) => person.community))].sort()
  return <div className="community-grid">{communities.map((community) => <div className={`community ${selected.community === community ? 'selected-community' : ''}`} key={community}><b>Community {community}</b><div>{people.filter((person) => person.community === community).sort((a, b) => b.investigation_priority_score - a.investigation_priority_score).slice(0, 6).map((person) => <button key={person.person_id} className={person.person_id === selected.person_id ? 'community-person selected-person' : 'community-person'} onClick={() => onSelect(person.person_id)}>{person.person_id}</button>)}</div></div>)}</div>
}

function App() {
  const [data, setData] = useState(null); const [selectedId, setSelectedId] = useState('P044'); const [query, setQuery] = useState(''); const [error, setError] = useState(''); const [refreshing, setRefreshing] = useState(false)
  const apiBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
  const loadData = useCallback(() => fetch(`${apiBase}/dashboard`, { signal: AbortSignal.timeout(3000) }).then((r) => r.ok ? r.json() : Promise.reject(new Error('Live API unavailable'))).catch(() => fetch('/data/analysis.json').then((r) => r.ok ? r.json() : Promise.reject(new Error('Analysis data not found. Start the API or run python3 src/main.py first.')))).then(setData).catch((e) => setError(e.message)), [apiBase])
  useEffect(() => { loadData() }, [loadData])
  const refreshAnalysis = async () => { setRefreshing(true); setError(''); try { const response = await fetch(`${apiBase}/reanalyse`, { method: 'POST' }); if (!response.ok) throw new Error('Refresh failed'); await loadData() } catch { setError('Live refresh needs the FastAPI server. The existing export is still available.') } finally { setRefreshing(false) } }
  const people = data?.people || []; const selected = people.find((p) => p.person_id === selectedId) || people[0]
  const ranked = people.filter((p) => `${p.person_id} ${p.name}`.toLowerCase().includes(query.toLowerCase())).slice(0, 10)
  const reports = (data?.reports || []).filter((r) => r.evidence.some((e) => e.entity_id === selected?.person_id))
  if (error) return <main className="status"><h1>Dataset unavailable</h1><p>{error}</p></main>
  if (!selected) return <main className="status"><h1>Loading analytical workspace…</h1></main>
  const signals = [['Network influence', selected.network_influence], ['Communication anomaly', selected.communication_anomaly], ['Financial anomaly', selected.financial_anomaly], ['Bridge importance', selected.bridge_score], ['Cycle evidence', selected.cycle_score], ['Layering evidence', selected.layering_score]]
  return <main><header><div><p className="eyebrow">SIH 26189 · Investigation Decision Support</p><h1>Criminal Network Analysis</h1></div><div className="header-actions"><button className="refresh" onClick={refreshAnalysis} disabled={refreshing}>{refreshing ? 'Refreshing…' : '↻ Refresh analysis'}</button><div className="human-review">Human review required<br /><span>Analytical leads, not accusations</span></div></div></header>
    <section className="metrics"><article><span>Knowledge graph</span><strong>{data.summary.nodes}</strong><small>nodes · {data.summary.edges} relationships</small></article><article><span>Intelligence evidence</span><strong>{data.summary.reports}</strong><small>source reports integrated</small></article><article><span>Transaction patterns</span><strong>{data.summary.cycles_detected + data.summary.layering_chains_detected}</strong><small>{data.summary.cycles_detected} cycles · {data.summary.layering_chains_detected} chains</small></article><article><span>Entities analysed</span><strong>{data.summary.people}</strong><small>people with explainable scores</small></article></section>
    <section className="workspace"><aside className="sidebar"><label htmlFor="person-search">Search entity</label><input id="person-search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ID or name" /><p className="eyebrow">Priority ranking</p><div className="entity-list">{ranked.map((p) => <button key={p.person_id} className={p.person_id === selected.person_id ? 'entity active' : 'entity'} onClick={() => setSelectedId(p.person_id)}><span><b>{p.person_id}</b>{p.name}</span><strong>{score(p.investigation_priority_score)}</strong></button>)}</div></aside>
      <div className="content"><section className="profile"><div><p className="eyebrow">Selected entity</p><h2>{selected.name} <span>{selected.person_id}</span></h2><p className="muted">Community {selected.community} · {selected.cross_community_edges} cross-community connections</p></div><div className="priority"><span>Investigation Priority Score</span><strong>{score(selected.investigation_priority_score)}</strong><small>/ 100</small></div></section>
        <section className="panel"><div className="panel-title"><div><p className="eyebrow">Evidence network</p><h3>Connected relationships</h3></div><span className="tag">Click a node to inspect</span></div><NetworkView selected={selected} people={people} edges={data.graph_edges} onSelect={setSelectedId} /></section>
        <section className="two-col"><div className="panel"><p className="eyebrow">Activity over time</p><h3>Entity timeline</h3><Timeline events={data.timelines[selected.person_id]} /></div><div className="panel"><p className="eyebrow">Network structure</p><h3>Community constellation</h3><CommunityView people={people} selected={selected} onSelect={setSelectedId} /></div></section>
        <section className="two-col"><div className="panel"><p className="eyebrow">Financial movement</p><h3>Transaction flow</h3><TransactionFlow patterns={data.patterns} /></div><div className="panel"><p className="eyebrow">Location footprint</p><h3>Intelligence report locations</h3><div className="locations">{data.location_footprint.slice(0, 8).map((location) => <article key={location.location_id}><b>{location.name}</b><span>{location.city}</span><strong>{location.report_count}</strong><small>reports</small></article>)}</div><p className="muted">Location coordinates are not available in the supplied synthetic dataset; this view preserves the source-record geography without inventing map positions.</p></div></section>
        <section className="two-col"><div className="panel"><p className="eyebrow">Why this requires review</p><h3>Analytical signals</h3><div className="signals">{signals.map(([label, value]) => <div key={label}><div><span>{label}</span><b>{score(value)}</b></div><i><em style={{ width: `${Math.min(value || 0, 100)}%` }} /></i></div>)}</div></div><div className="panel"><p className="eyebrow">Source provenance</p><h3>Intelligence report evidence</h3>{reports.length ? reports.map((r) => <article className="report" key={r.report_id}><b>{r.report_id}</b><p>{r.text}</p><small>{r.evidence.filter((e) => e.entity_id === selected.person_id).map((e) => `${e.relationship} · ${e.match_type} · ${Math.round(e.confidence * 100)}% confidence`).join(' · ')}</small></article>) : <p className="muted">No intelligence-report mention for this entity.</p>}</div></section>
        <section className="panel patterns"><p className="eyebrow">Detected financial patterns</p><h3>Evidence requiring investigator review</h3><div>{data.patterns.transaction_cycles.map((i) => <article key={i.cycle}><b>Circular flow</b><p>{i.cycle}</p><small>{i.timestamp} · average transfer ₹{Number(i.amount).toLocaleString()}</small></article>)}{data.patterns.layering_chains.map((i) => <article key={i.chain}><b>Layering chain</b><p>{i.chain}</p><small>{i.timestamp} · initial transfer ₹{Number(i.initial_amount).toLocaleString()}</small></article>)}</div></section>
      </div></section></main>
}
export default App
