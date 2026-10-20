function SimpleBar({ label, value, max, color = '#3b82f6' }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', marginBottom: 4 }}>
        <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontWeight: 600 }}>{value}</span>
      </div>
      <div style={{ height: 6, background: 'rgba(255,255,255,0.07)', borderRadius: 3 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.4s' }} />
      </div>
    </div>
  );
}

function StatBox({ label, value, icon, color = '#3b82f6' }) {
  return (
    <div className="card" style={{ textAlign: 'center', borderTop: `2px solid ${color}` }}>
      <div style={{ fontSize: '1.6rem', marginBottom: 4 }}>{icon}</div>
      <div style={{ fontSize: '1.5rem', fontWeight: 800, color }}>{value ?? '—'}</div>
      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
    </div>
  );
}

export default function Analytics({ simState }) {
  const analytics = simState?.analytics || {};
  const hospitals = simState?.hospitals || [];
  const ambulances = simState?.ambulances || [];
  const emergencies = simState?.emergencies || [];
  const messages = simState?.analytics?.total_messages || 0;
  const searchRuns = analytics.search_runs || [];

  const active = emergencies.filter(e => e.status === 'ACTIVE').length;
  const completed = emergencies.filter(e => e.status === 'COMPLETED').length;
  const failed = emergencies.filter(e => e.status === 'FAILED').length;
  const totalReplans = simState?.coordinator_stats?.total_replans || analytics.total_replans || 0;
  const completionRate = emergencies.length > 0 ? Math.round((completed / emergencies.length) * 100) : 0;

  const searchByAlgo = searchRuns.reduce((acc, r) => {
    const a = r.algorithm;
    if (!acc[a]) acc[a] = { runs: 0, totalNodes: 0, totalTime: 0, totalCost: 0 };
    acc[a].runs++;
    acc[a].totalNodes += r.nodes_expanded || 0;
    acc[a].totalTime += r.execution_time_ms || 0;
    acc[a].totalCost += r.cost || 0;
    return acc;
  }, {});

  const busyAmbulances = ambulances.filter(a => a.status !== 'IDLE').length;

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">📈 Analytics</div>
          <div className="page-subtitle">Performance metrics for the multi-agent system</div>
        </div>
        <span className="badge badge-blue">Tick #{simState?.tick || 0}</span>
      </div>

      <div className="page-body fade-in">
        {/* Top-level KPIs */}
        <div className="grid-4" style={{ marginBottom: 20 }}>
          <StatBox icon="🚨" label="Total Emergencies" value={emergencies.length} color="#ef4444" />
          <StatBox icon="✅" label="Completion Rate" value={`${completionRate}%`} color="#10b981" />
          <StatBox icon="🔄" label="Total Replans" value={totalReplans} color="#f59e0b" />
          <StatBox icon="💬" label="Agent Messages" value={simState?.analytics?.total_messages ?? (simState ? Object.values(simState?.agent_states || {}).length : 0)} color="#8b5cf6" />
        </div>

        <div className="grid-2" style={{ marginBottom: 20, gap: 16 }}>

          {/* Emergency breakdown */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: 14 }}>Emergency Status</div>
            <SimpleBar label="Active" value={active} max={emergencies.length || 1} color="#3b82f6" />
            <SimpleBar label="Completed" value={completed} max={emergencies.length || 1} color="#10b981" />
            <SimpleBar label="Failed" value={failed} max={emergencies.length || 1} color="#ef4444" />
            <div style={{ marginTop: 12, padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 6, fontSize: '0.75rem' }}>
              {emergencies.map(e => (
                <div key={e.emergency_id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontFamily: 'monospace', color: '#60a5fa' }}>{e.emergency_id}</span>
                  <span style={{ color: 'var(--text-muted)' }}>{e.severity}</span>
                  <span className={`badge ${e.status === 'COMPLETED' ? 'badge-green' : e.status === 'FAILED' ? 'badge-red' : 'badge-blue'}`}>{e.status}</span>
                  <span style={{ color: 'var(--text-muted)' }}>Replans: {e.replan_count || 0}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Hospital Utilization */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: 14 }}>Hospital Utilization</div>
            {hospitals.map(h => {
              const bedPct = h.total_beds > 0 ? Math.round((1 - h.available_beds / h.total_beds) * 100) : 0;
              const icuPct = h.icu_total > 0 ? Math.round((1 - h.icu_available / h.icu_total) * 100) : 0;
              return (
                <div key={h.hospital_id} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 4 }}>
                    <strong>{h.hospital_id}</strong>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{h.name}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: 2 }}>Beds {bedPct}%</div>
                      <div style={{ height: 4, background: 'rgba(255,255,255,0.07)', borderRadius: 2 }}>
                        <div style={{ width: `${bedPct}%`, height: '100%', background: bedPct > 80 ? '#ef4444' : '#3b82f6', borderRadius: 2 }} />
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: 2 }}>ICU {icuPct}%</div>
                      <div style={{ height: 4, background: 'rgba(255,255,255,0.07)', borderRadius: 2 }}>
                        <div style={{ width: `${icuPct}%`, height: '100%', background: icuPct > 80 ? '#ef4444' : '#8b5cf6', borderRadius: 2 }} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Ambulance Utilization */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Ambulance Utilization</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {ambulances.map(a => (
              <div key={a.ambulance_id} style={{
                padding: '8px 14px', borderRadius: 8, fontSize: '0.75rem', fontWeight: 600,
                background: a.status === 'IDLE' ? 'rgba(255,255,255,0.04)' : 'rgba(59,130,246,0.12)',
                border: `1px solid ${a.status === 'IDLE' ? 'var(--border)' : 'rgba(59,130,246,0.3)'}`,
                color: a.status === 'IDLE' ? 'var(--text-muted)' : '#60a5fa'
              }}>
                🚑 {a.ambulance_id}
                <div style={{ fontWeight: 400, fontSize: '0.68rem', marginTop: 2, color: 'var(--text-muted)' }}>
                  {a.status?.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search Algorithm Performance */}
        {Object.keys(searchByAlgo).length > 0 && (
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="card-title" style={{ marginBottom: 12 }}>Search Algorithm Performance</div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Algorithm</th><th>Runs</th><th>Avg Nodes Expanded</th><th>Avg Cost</th><th>Avg Time (ms)</th></tr>
                </thead>
                <tbody>
                  {Object.entries(searchByAlgo).map(([algo, stats]) => (
                    <tr key={algo}>
                      <td><strong style={{ color: '#60a5fa' }}>{algo}</strong></td>
                      <td>{stats.runs}</td>
                      <td>{Math.round(stats.totalNodes / stats.runs)}</td>
                      <td>{(stats.totalCost / stats.runs).toFixed(2)}</td>
                      <td>{(stats.totalTime / stats.runs).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Environment Characteristics */}
        <div className="card">
          <div style={{ fontWeight: 700, marginBottom: 12 }}>🌐 Environment Characteristics</div>
          <div className="grid-3" style={{ gap: 10 }}>
            {[
              { name: 'Partially Observable', desc: 'Each agent has limited view of the world', icon: '👁️' },
              { name: 'Multi-Agent', desc: '6 agent types cooperating simultaneously', icon: '🤝' },
              { name: 'Dynamic', desc: 'Road conditions, hospital capacity change at runtime', icon: '⚡' },
              { name: 'Stochastic', desc: 'Traffic and load values have uncertainty factors', icon: '🎲' },
              { name: 'Sequential', desc: 'Emergency plans execute step-by-step', icon: '📋' },
              { name: 'Cooperative', desc: 'All agents work toward shared goal', icon: '🎯' },
            ].map(c => (
              <div key={c.name} style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '1.2rem', marginBottom: 4 }}>{c.icon}</div>
                <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: 2 }}>{c.name}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{c.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
