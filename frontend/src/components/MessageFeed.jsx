import { useEffect, useRef } from 'react';

const AGENT_COLORS = {
  PatientAgent: '#ef4444',
  AmbulanceAgent: '#3b82f6',
  HospitalAgent: '#8b5cf6',
  DoctorAgent: '#10b981',
  TrafficAgent: '#f97316',
  CoordinatorAgent: '#f59e0b',
  SearchEngine: '#06b6d4',
  KnowledgeBase: '#a78bfa',
  DecisionEngine: '#34d399',
  Simulator: '#64748b',
};

function getColor(agentId) {
  for (const [key, col] of Object.entries(AGENT_COLORS)) {
    if (agentId?.includes(key) || agentId === key) return col;
  }
  return '#94a3b8';
}

function MessageRow({ msg }) {
  const sc = getColor(msg.sender);
  const rc = getColor(msg.receiver);
  return (
    <div style={{
      padding: '7px 12px',
      borderBottom: '1px solid rgba(255,255,255,0.05)',
      fontSize: '0.76rem',
      display: 'flex', gap: 10, alignItems: 'flex-start',
    }}>
      <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.7rem', flexShrink: 0, marginTop: 1 }}>
        {msg.timestamp}
      </span>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <span style={{ color: sc, fontWeight: 600 }}>{msg.sender}</span>
          <span style={{ color: 'var(--text-muted)' }}>→</span>
          <span style={{ color: rc, fontWeight: 600 }}>{msg.receiver}</span>
          <span className="tag" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)', fontSize: '0.65rem' }}>
            {msg.message_type}
          </span>
        </div>
        <div style={{ color: 'var(--text-secondary)' }}>{msg.content}</div>
      </div>
    </div>
  );
}

export default function MessageFeed({ messages, maxHeight = 280 }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages?.length]);

  if (!messages?.length) {
    return (
      <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        No messages yet. Start the simulation.
      </div>
    );
  }

  return (
    <div style={{ maxHeight, overflowY: 'auto' }}>
      {[...messages].reverse().map((msg, i) => (
        <MessageRow key={msg.message_id || i} msg={msg} />
      ))}
      <div ref={endRef} />
    </div>
  );
}
