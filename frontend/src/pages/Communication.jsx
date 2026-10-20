import MessageFeed from '../components/MessageFeed';
import { api } from '../services/api';
import { useState, useEffect } from 'react';

const AGENT_TYPES = {
  PatientAgent: { color: '#ef4444', icon: '👤' },
  AmbulanceAgent: { color: '#3b82f6', icon: '🚑' },
  HospitalAgent: { color: '#8b5cf6', icon: '🏥' },
  DoctorAgent: { color: '#10b981', icon: '👨‍⚕️' },
  TrafficAgent: { color: '#f97316', icon: '🚦' },
  CoordinatorAgent: { color: '#f59e0b', icon: '🎯' },
  SearchEngine: { color: '#06b6d4', icon: '🔍' },
  KnowledgeBase: { color: '#a78bfa', icon: '🧠' },
  DecisionEngine: { color: '#34d399', icon: '⚖️' },
};

export default function Communication({ messages, connected }) {
  const [allMessages, setAllMessages] = useState([]);
  const [filterSender, setFilterSender] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');
  const [msgCount, setMsgCount] = useState(0);

  const loadAllMessages = async () => {
    try {
      const msgs = await api.getMessages(200);
      setAllMessages(msgs);
    } catch {}
  };

  useEffect(() => {
    loadAllMessages();
  }, [messages?.length]);

  useEffect(() => {
    api.getMessages(1).then(m => setMsgCount(m.length)).catch(() => {});
  }, [messages?.length]);

  const displayMsgs = (allMessages.length > 0 ? allMessages : messages || []);
  const senders = ['ALL', ...new Set(displayMsgs.map(m => m.sender))];
  const types = ['ALL', ...new Set(displayMsgs.map(m => m.message_type))];

  const filtered = displayMsgs.filter(m =>
    (filterSender === 'ALL' || m.sender === filterSender) &&
    (filterType === 'ALL' || m.message_type === filterType)
  );

  const selectStyle = { background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '5px 10px', fontSize: '0.8rem' };

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">💬 Agent Communication</div>
          <div className="page-subtitle">Real-time inter-agent messages — {displayMsgs.length} total</div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span className={`badge ${connected ? 'badge-green' : 'badge-red'}`}>
            {connected ? '🟢 Live' : '🔴 Offline'}
          </span>
          <button className="btn btn-ghost btn-sm" onClick={loadAllMessages}>↺ Refresh</button>
        </div>
      </div>

      <div className="page-body fade-in">
        {/* Agent legend */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
          {Object.entries(AGENT_TYPES).map(([name, info]) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 10px', borderRadius: 20, background: `${info.color}18`, border: `1px solid ${info.color}44`, fontSize: '0.72rem', fontWeight: 600, color: info.color }}>
              {info.icon} {name.replace('Agent', '')}
            </div>
          ))}
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 12, alignItems: 'center' }}>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Sender:</label>
          <select value={filterSender} onChange={e => setFilterSender(e.target.value)} style={selectStyle}>
            {senders.map(s => <option key={s}>{s}</option>)}
          </select>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Type:</label>
          <select value={filterType} onChange={e => setFilterType(e.target.value)} style={selectStyle}>
            {types.map(t => <option key={t}>{t}</option>)}
          </select>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
            Showing {filtered.length} of {displayMsgs.length}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16, height: 'calc(100vh - 280px)' }}>
          {/* Main message feed */}
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--border)', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Message Log</span>
              <span style={{ color: 'var(--text-muted)' }}>{filtered.length} messages</span>
            </div>
            <div style={{ flex: 1, overflow: 'auto' }}>
              <MessageFeed messages={filtered} maxHeight={99999} />
            </div>
          </div>

          {/* Statistics */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card">
              <div className="card-title">Message Statistics</div>
              <div style={{ fontSize: '0.78rem' }}>
                {Object.entries(
                  displayMsgs.reduce((acc, m) => ({ ...acc, [m.message_type]: (acc[m.message_type] || 0) + 1 }), {})
                ).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([type, count]) => (
                  <div key={type} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.72rem', fontFamily: 'monospace' }}>{type}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 60, height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2 }}>
                        <div style={{ width: `${(count / displayMsgs.length) * 100}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: 2 }} />
                      </div>
                      <strong style={{ minWidth: 24, textAlign: 'right' }}>{count}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-title">Agent Activity</div>
              {Object.entries(AGENT_TYPES).map(([name, info]) => {
                const count = displayMsgs.filter(m => m.sender?.includes(name.replace('Agent','')) || m.sender === name).length;
                return (
                  <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 5, fontSize: '0.75rem' }}>
                    <span style={{ color: info.color }}>{info.icon} {name.replace('Agent', '')}</span>
                    <span className="badge" style={{ background: `${info.color}22`, color: info.color }}>{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
