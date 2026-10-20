import { useMemo } from 'react';

function StatCard({ icon, title, value, sub, color = 'blue' }) {
  const colors = { blue: '#3b82f6', green: '#10b981', red: '#ef4444', yellow: '#f59e0b', purple: '#8b5cf6', orange: '#f97316' };
  return (
    <div className="card" style={{ borderLeft: `3px solid ${colors[color]}` }}>
      <div className="card-title">{icon} {title}</div>
      <div className="card-value" style={{ color: colors[color] }}>{value}</div>
      {sub && <div className="card-sub">{sub}</div>}
    </div>
  );
}

export default function Dashboard({ simState, connected, status }) {
  const stats = useMemo(() => {
    if (!simState) return null;
    const hospitals = simState.hospitals || [];
    const ambulances = simState.ambulances || [];
    const doctors = simState.doctors || [];
    const emergencies = simState.emergencies || [];
    return {
      activeEmergencies: emergencies.filter(e => e.status === 'ACTIVE').length,
      completedEmergencies: emergencies.filter(e => e.status === 'COMPLETED').length,
      idleAmbulances: ambulances.filter(a => a.status === 'IDLE').length,
      totalAmbulances: ambulances.length,
      availableDoctors: doctors.filter(d => d.availability).length,
      totalDoctors: doctors.length,
      totalICU: hospitals.reduce((s, h) => s + (h.icu_total || 0), 0),
      availableICU: hospitals.reduce((s, h) => s + (h.icu_available || 0), 0),
      totalBeds: hospitals.reduce((s, h) => s + (h.total_beds || 0), 0),
      availableBeds: hospitals.reduce((s, h) => s + (h.available_beds || 0), 0),
      totalMessages: simState.analytics?.total_messages || 0,
      totalReplans: simState.analytics?.total_replans || 0 || simState.coordinator_stats?.total_replans || 0,
    };
  }, [simState]);

  const hospitals = simState?.hospitals || [];
  const ambulances = simState?.ambulances || [];
  const emergencies = simState?.emergencies || [];

  const severityBadge = (sev) => {
    const map = { CRITICAL: 'badge-red', HIGH: 'badge-orange', MODERATE: 'badge-yellow', LOW: 'badge-green' };
    return <span className={`badge ${map[sev] || 'badge-gray'}`}>{sev}</span>;
  };

  const statusBadge = (st) => {
    const map = { IDLE: 'badge-gray', DISPATCHED: 'badge-blue', EN_ROUTE_TO_PATIENT: 'badge-blue', PATIENT_PICKED_UP: 'badge-yellow', EN_ROUTE_TO_HOSPITAL: 'badge-orange', ARRIVED: 'badge-green' };
    return <span className={`badge ${map[st] || 'badge-gray'}`}>{st?.replace(/_/g,' ')}</span>;
  };

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">🏥 Emergency Response Dashboard</div>
          <div className="page-subtitle">AI-Driven Multi-Agent System — Real-time Overview</div>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span className={`badge ${connected ? 'badge-green' : 'badge-red'}`}>
            {connected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          <span className="badge badge-blue">Tick #{simState?.tick || 0}</span>
          <span className={`badge ${status === 'RUNNING' ? 'badge-green' : status === 'PAUSED' ? 'badge-yellow' : 'badge-gray'}`}>
            {status}
          </span>
        </div>
      </div>

      <div className="page-body fade-in">
        {/* KPI Stats */}
        <div className="stat-grid">
          <StatCard icon="🚨" title="Active Emergencies" value={stats?.activeEmergencies ?? '—'} color="red" sub={`${stats?.completedEmergencies ?? 0} completed`} />
          <StatCard icon="🚑" title="Idle Ambulances" value={`${stats?.idleAmbulances ?? '—'}/${stats?.totalAmbulances ?? '—'}`} color="blue" sub="Available for dispatch" />
          <StatCard icon="🏥" title="ICU Beds Available" value={`${stats?.availableICU ?? '—'}/${stats?.totalICU ?? '—'}`} color="purple" />
          <StatCard icon="🛏️" title="Total Beds Available" value={`${stats?.availableBeds ?? '—'}/${stats?.totalBeds ?? '—'}`} color="orange" />
          <StatCard icon="👨‍⚕️" title="Available Doctors" value={`${stats?.availableDoctors ?? '—'}/${stats?.totalDoctors ?? '—'}`} color="green" />
          <StatCard icon="🔄" title="Total Replans" value={stats?.totalReplans ?? '—'} color="yellow" sub="Dynamic replanning events" />
        </div>

        {/* PEAS Framework Display */}
        <div className="section">
          <div className="section-header"><h3 className="section-title">🔬 Agent Types (PEAS Framework)</h3></div>
          <div className="grid-3" style={{ gap: 10 }}>
            {[
              { icon: '👤', name: 'Patient Agent', perf: 'Receive treatment fast', env: 'City, hospitals, ambulances', act: 'Generate emergency, update status', sens: 'Own location, severity' },
              { icon: '🚑', name: 'Ambulance Agent', perf: 'Minimise transport time', env: 'City grid, roads, hospitals', act: 'Navigate, pick up, replan', sens: 'Location, road states, patient' },
              { icon: '🏥', name: 'Hospital Agent', perf: 'Maximise treated patients', env: 'Hospital building, doctors', act: 'Accept/reject, reserve bed', sens: 'Bed count, ICU, specialists' },
              { icon: '👨‍⚕️', name: 'Doctor Agent', perf: 'Treat assigned patients', env: 'Hospital, patient list', act: 'Accept patient, become busy/free', sens: 'Own availability, workload' },
              { icon: '🚦', name: 'Traffic Agent', perf: 'Accurate road data', env: 'City road network', act: 'Update road states, broadcast alerts', sens: 'Road sensors, incidents' },
              { icon: '🎯', name: 'Coordinator Agent', perf: 'All emergencies resolved', env: 'All agents + city', act: 'Dispatch, coordinate, replan', sens: 'All agent messages, global state' },
            ].map(a => (
              <div key={a.name} className="card" style={{ fontSize: '0.78rem' }}>
                <div style={{ fontSize: '1.2rem', marginBottom: 6 }}>{a.icon} <strong>{a.name}</strong></div>
                <div style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                  <div><strong style={{ color: '#60a5fa' }}>P</strong> {a.perf}</div>
                  <div><strong style={{ color: '#34d399' }}>E</strong> {a.env}</div>
                  <div><strong style={{ color: '#fb923c' }}>A</strong> {a.act}</div>
                  <div><strong style={{ color: '#a78bfa' }}>S</strong> {a.sens}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Emergencies */}
        <div className="section">
          <div className="section-header"><h3 className="section-title">🚨 Active Emergencies</h3></div>
          {emergencies.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px' }}>
              No emergencies. Start a simulation scenario.
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>ID</th><th>Patient</th><th>Severity</th><th>Status</th><th>Ambulance</th><th>Hospital</th><th>Replans</th></tr></thead>
                <tbody>
                  {emergencies.map(e => (
                    <tr key={e.emergency_id}>
                      <td><span className="mono" style={{ color: '#60a5fa' }}>{e.emergency_id}</span></td>
                      <td>{e.patient_id}</td>
                      <td>{severityBadge(e.severity)}</td>
                      <td><span className={`badge ${e.status === 'COMPLETED' ? 'badge-green' : e.status === 'FAILED' ? 'badge-red' : 'badge-blue'}`}>{e.status}</span></td>
                      <td>{e.assigned_ambulance || '—'}</td>
                      <td>{e.assigned_hospital || '—'}</td>
                      <td>{e.replan_count || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Hospitals Status */}
        <div className="section">
          <div className="section-header"><h3 className="section-title">🏥 Hospital Status</h3></div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Hospital</th><th>Beds</th><th>ICU</th><th>Specialists</th><th>Status</th></tr></thead>
              <tbody>
                {hospitals.map(h => (
                  <tr key={h.hospital_id}>
                    <td><strong>{h.name || h.hospital_id}</strong></td>
                    <td>{h.available_beds}/{h.total_beds}</td>
                    <td>
                      <span style={{ color: h.icu_available === 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                        {h.icu_available}/{h.icu_total}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.75rem' }}>{(h.available_specialists || []).join(', ')}</td>
                    <td><span className={`badge ${h.status === 'OPERATIONAL' ? 'badge-green' : 'badge-red'}`}>{h.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
