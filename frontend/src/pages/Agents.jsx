import { useState } from 'react';

const STATUS_COLOR = {
  IDLE: '#64748b', DISPATCHED: '#3b82f6', EN_ROUTE_TO_PATIENT: '#06b6d4',
  PATIENT_PICKED_UP: '#f59e0b', EN_ROUTE_TO_HOSPITAL: '#f97316', ARRIVED: '#10b981',
  WAITING: '#64748b', EMERGENCY_GENERATED: '#ef4444', AMBULANCE_ASSIGNED: '#3b82f6',
  EN_ROUTE: '#06b6d4', TREATED: '#10b981',
  AVAILABLE: '#10b981', TREATING_PATIENT: '#f59e0b', OFF_DUTY: '#64748b',
  OPERATIONAL: '#10b981', CRITICAL_LOAD: '#ef4444',
};

const TYPE_ICON = {
  PatientAgent: '👤', AmbulanceAgent: '🚑', HospitalAgent: '🏥',
  DoctorAgent: '👨‍⚕️', TrafficAgent: '🚦', CoordinatorAgent: '🎯',
};

function AgentCard({ agent }) {
  const icon = TYPE_ICON[agent.agent_type] || '🤖';
  
  let statusValue = agent.state?.status;
  if (!statusValue) {
    if (agent.state?.availability !== undefined) {
      statusValue = agent.state.availability ? 'AVAILABLE' : 'OFF_DUTY';
    } else {
      statusValue = 'IDLE';
    }
  }
  const statusColor = STATUS_COLOR[statusValue] || '#94a3b8';

  const stateEntries = Object.entries(agent.state || {}).filter(([k]) =>
    !['current_route', 'reserved_for', 'incidents', 'message_log'].includes(k)
  );

  return (
    <div className="card" style={{ borderLeft: `3px solid ${statusColor}` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <span style={{ fontSize: '1.3rem' }}>{icon}</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{agent.agent_id}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{agent.agent_type}</div>
        </div>
        <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
          <div className="badge" style={{ background: `${statusColor}22`, color: statusColor, fontSize: '0.68rem' }}>
            {agent.current_action || 'IDLE'}
          </div>
        </div>
      </div>

      <div style={{ fontSize: '0.72rem', color: '#60a5fa', marginBottom: 6, fontStyle: 'italic' }}>
        🎯 {agent.goal}
      </div>

      <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 6, padding: '8px 10px', fontSize: '0.73rem' }}>
        <div style={{ fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.65rem' }}>State</div>
        {stateEntries.slice(0, 8).map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, marginBottom: 2 }}>
            <span style={{ color: 'var(--text-muted)' }}>{k.replace(/_/g, ' ')}</span>
            <span style={{ color: 'var(--text-primary)', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {Array.isArray(v) ? v.join(', ') || '—' : typeof v === 'object' ? JSON.stringify(v) : String(v ?? '—')}
            </span>
          </div>
        ))}
      </div>

      {agent.current_plan && (
        <div style={{ marginTop: 6, fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
          📋 Plan: {agent.current_plan}
        </div>
      )}
    </div>
  );
}

export default function Agents({ simState }) {
  const [activeTab, setActiveTab] = useState('ALL');

  const agents = simState?.agent_states ? Object.values(simState.agent_states) : [];
  
  const byType = {
    PatientAgent: [], AmbulanceAgent: [], HospitalAgent: [],
    DoctorAgent: [], TrafficAgent: [], CoordinatorAgent: []
  };
  
  agents.forEach(a => { if (byType[a.agent_type]) byType[a.agent_type].push(a); });

  const tabs = [
    { id: 'ALL', label: 'All Agents', count: agents.length },
    { id: 'PatientAgent', label: 'Patients', count: byType.PatientAgent.length },
    { id: 'AmbulanceAgent', label: 'Ambulances', count: byType.AmbulanceAgent.length },
    { id: 'HospitalAgent', label: 'Hospitals', count: byType.HospitalAgent.length },
    { id: 'DoctorAgent', label: 'Doctors', count: byType.DoctorAgent.length },
    { id: 'TrafficAgent', label: 'Traffic', count: byType.TrafficAgent.length },
    { id: 'CoordinatorAgent', label: 'Coordinator', count: byType.CoordinatorAgent.length },
  ];

  const typesToRender = activeTab === 'ALL' 
    ? Object.keys(byType)
    : [activeTab];

  return (
    <div className="page-root">
      <div className="page-header" style={{ paddingBottom: 16 }}>
        <div>
          <div className="page-title">🤖 Agent Monitor</div>
          <div className="page-subtitle">Live state of all autonomous agents in the system</div>
        </div>
        <span className="badge badge-blue">{agents.length} Agents Active</span>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, padding: '0 24px', marginBottom: 16, overflowX: 'auto', flexShrink: 0 }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '6px 14px',
              borderRadius: '999px',
              border: 'none',
              background: activeTab === tab.id ? 'var(--accent-blue)' : 'rgba(255,255,255,0.05)',
              color: activeTab === tab.id ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
          >
            {tab.id !== 'ALL' && TYPE_ICON[tab.id]} {tab.label}
            <span style={{ 
              background: activeTab === tab.id ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)',
              padding: '2px 6px',
              borderRadius: '10px',
              fontSize: '0.65rem'
            }}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      <div className="page-body fade-in" style={{ paddingTop: 0 }}>
        {typesToRender.map(type => {
          const agentList = byType[type];
          if (agentList.length === 0) return null;
          
          return (
            <div key={type} className="section">
              <div className="section-header">
                <h3 className="section-title">{TYPE_ICON[type]} {type}s ({agentList.length})</h3>
              </div>
              <div className="grid-3" style={{ gap: 12 }}>
                {agentList.map(a => <AgentCard key={a.agent_id} agent={a} />)}
              </div>
            </div>
          );
        })}

        {agents.length === 0 && (
          <div className="empty-state">
            <div className="icon">🤖</div>
            <p>Start a simulation to see agent states</p>
          </div>
        )}
      </div>
    </div>
  );
}
