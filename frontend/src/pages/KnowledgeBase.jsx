import { useState, useEffect } from 'react';
import { api } from '../services/api';

function FactRow({ fact }) {
  return (
    <div style={{ padding: '6px 10px', borderRadius: 6, background: 'rgba(255,255,255,0.03)', marginBottom: 4, fontSize: '0.76rem', fontFamily: 'monospace' }}>
      <span style={{ color: '#60a5fa', fontWeight: 600 }}>{fact.predicate}</span>
      <span style={{ color: 'var(--text-muted)' }}>(</span>
      {Object.entries(fact.args || {}).map(([k, v], i, arr) => (
        <span key={k}>
          <span style={{ color: '#a78bfa' }}>{k}</span>
          <span style={{ color: 'var(--text-muted)' }}>=</span>
          <span style={{ color: '#34d399' }}>{v}</span>
          {i < arr.length - 1 && <span style={{ color: 'var(--text-muted)' }}>, </span>}
        </span>
      ))}
      <span style={{ color: 'var(--text-muted)' }}>)</span>
    </div>
  );
}

function ProofTree({ step, depth = 0 }) {
  if (!step) return null;
  const proved = step.result === 'PROVED';
  return (
    <div style={{ marginLeft: depth * 16, marginBottom: 6 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRadius: 6,
        background: proved ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
        border: `1px solid ${proved ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
        fontSize: '0.76rem', fontFamily: 'monospace' }}>
        <span>{proved ? '✅' : '❌'}</span>
        <span style={{ color: proved ? '#34d399' : '#f87171' }}>{step.goal}</span>
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.68rem' }}>{step.method}</span>
      </div>
      {(step.children || []).map((child, i) => (
        <ProofTree key={i} step={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function KnowledgeBase({ simState }) {
  const [snapshot, setSnapshot] = useState(null);
  const [fcResult, setFcResult] = useState(null);
  const [bcResult, setBcResult] = useState(null);
  const [bcHospital, setBcHospital] = useState('H1');
  const [bcPatient, setBcPatient] = useState('P001');
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('facts');

  const loadSnapshot = async () => {
    try { setSnapshot(await api.getKnowledge()); } catch {}
  };

  const runFC = async () => {
    setLoading(true);
    try { setFcResult(await api.runForwardChain()); } catch {}
    setLoading(false);
    await loadSnapshot();
  };

  const runBC = async () => {
    setLoading(true);
    try { setBcResult(await api.runBackwardChain(bcHospital, bcPatient)); } catch {}
    setLoading(false);
  };

  useEffect(() => { loadSnapshot(); }, [simState?.tick]);

  const inputStyle = { background: 'var(--bg-deep)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '5px 10px', fontSize: '0.82rem' };

  const facts = snapshot?.facts || [];
  const rules = snapshot?.rules || [];
  const derivedPreds = new Set(['hospital_satisfies_icu','hospital_satisfies_specialist','hospital_eligible_for_patient','hospital_rejects_patient','doctor_can_treat','road_high_cost','road_unavailable']);
  const baseFacts = facts.filter(f => !derivedPreds.has(f.predicate));
  const derivedFacts = facts.filter(f => derivedPreds.has(f.predicate));

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">🧠 Knowledge Base</div>
          <div className="page-subtitle">Facts, rules, and reasoning inference engine</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-primary btn-sm" onClick={runFC} disabled={loading}>
            {loading ? '⟳' : '▶'} Forward Chain
          </button>
          <button className="btn btn-ghost btn-sm" onClick={loadSnapshot}>↺ Refresh</button>
        </div>
      </div>

      <div className="page-body fade-in">
        <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 180px)' }}>

          {/* Left: Facts + Rules */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12, overflow: 'hidden' }}>
            {/* Tabs */}
            <div style={{ display: 'flex', gap: 4, background: 'var(--bg-card)', borderRadius: 8, padding: 4, border: '1px solid var(--border)' }}>
              {['facts', 'derived', 'rules'].map(t => (
                <button key={t} onClick={() => setTab(t)}
                  className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ flex: 1, textTransform: 'capitalize' }}>
                  {t === 'facts' ? `Base Facts (${baseFacts.length})` : t === 'derived' ? `Derived (${derivedFacts.length})` : `Rules (${rules.length})`}
                </button>
              ))}
            </div>

            <div style={{ flex: 1, overflow: 'hidden', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                {tab === 'facts' ? '📋 Base Facts' : tab === 'derived' ? '💡 Derived Facts (by Forward Chaining)' : '📜 Inference Rules'}
              </div>
              <div style={{ flex: 1, overflow: 'auto', padding: '12px 16px' }}>
                {tab === 'facts' && (baseFacts.length === 0 ? <div className="empty-state"><p>No facts yet. Start a simulation.</p></div> : baseFacts.map((f, i) => <FactRow key={i} fact={f} />))}
                {tab === 'derived' && (derivedFacts.length === 0 ? <div className="empty-state"><p>Run Forward Chaining to derive facts.</p></div> : derivedFacts.map((f, i) => <FactRow key={i} fact={f} />))}
                {tab === 'rules' && rules.map(r => (
                  <div key={r.rule_id} style={{ padding: '10px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.03)', marginBottom: 8, fontSize: '0.75rem' }}>
                    <div style={{ fontWeight: 700, color: '#60a5fa', marginBottom: 4 }}>{r.rule_id}</div>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>{r.description}</div>
                    <div style={{ fontFamily: 'monospace', fontSize: '0.7rem' }}>
                      <div style={{ color: '#a78bfa' }}>IF:</div>
                      {r.conditions?.map((c, i) => <div key={i} style={{ marginLeft: 12, color: '#34d399' }}>{c}</div>)}
                      <div style={{ color: '#fbbf24', marginTop: 4 }}>THEN: {r.conclusion}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Forward chain result */}
            {fcResult && (
              <div className="info-box info-box-green">
                <strong>Forward Chaining Result:</strong> Derived {fcResult.new_facts_count} new facts
                {fcResult.derivations?.slice(0,3).map((d, i) => (
                  <div key={i} style={{ marginTop: 4, fontSize: '0.72rem', fontFamily: 'monospace' }}>
                    <span style={{ color: '#fbbf24' }}>{d.by_rule}</span>: {d.derived_fact?.predicate}(...)
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right: Backward Chaining */}
          <div style={{ width: 340, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card">
              <div className="card-title" style={{ marginBottom: 12 }}>🔍 Backward Chaining Query</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 10 }}>
                Query: Can Hospital X treat Patient Y?
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: 3 }}>Hospital ID</label>
                  <input value={bcHospital} onChange={e => setBcHospital(e.target.value)} style={{ ...inputStyle, width: '100%' }} />
                </div>
                <div>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: 3 }}>Patient ID</label>
                  <input value={bcPatient} onChange={e => setBcPatient(e.target.value)} style={{ ...inputStyle, width: '100%' }} />
                </div>
                <button className="btn btn-primary btn-sm w-full" onClick={runBC} disabled={loading}>
                  Prove Goal
                </button>
              </div>
            </div>

            {bcResult && (
              <div style={{ flex: 1, overflow: 'auto', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: '1.2rem' }}>{bcResult.proved ? '✅' : '❌'}</span>
                  <div>
                    <div style={{ fontWeight: 700, color: bcResult.proved ? '#34d399' : '#f87171' }}>
                      {bcResult.proved ? 'PROVED' : 'DISPROVED'}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{bcResult.goal}</div>
                  </div>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase' }}>Proof Tree</div>
                {bcResult.proof_tree && <ProofTree step={bcResult.proof_tree} />}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
