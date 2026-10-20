import { useState, useEffect } from 'react';
import { api } from '../services/api';

const DIFFICULTY_COLOR = { Basic: '#10b981', Intermediate: '#f59e0b', Advanced: '#f97316', Expert: '#ef4444' };

export default function Scenarios({ onStart, onReset }) {
  const [scenarios, setScenarios] = useState({});
  const [selected, setSelected] = useState(null);
  const [running, setRunning] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getScenarios().then(setScenarios).catch(() => {});
  }, []);

  const handleRun = async (scenarioId) => {
    setLoading(true);
    setRunning(scenarioId);
    try {
      await onReset(scenarioId);
      await new Promise(r => setTimeout(r, 500));
      await onStart(scenarioId);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const SCENARIO_ICONS = {
    scenario_1: '🚨', scenario_2: '🆘', scenario_3: '🏥',
    scenario_4: '🚦', scenario_5: '👨‍⚕️', scenario_6: '🚑', scenario_7: '⚡'
  };

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">📋 Scenario Generator</div>
          <div className="page-subtitle">Predefined scenarios demonstrating different AI challenges</div>
        </div>
      </div>

      <div className="page-body fade-in">
        {/* AI Concepts Coverage */}
        <div className="card mb-4" style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.2)' }}>
          <div style={{ fontWeight: 700, marginBottom: 10, color: '#60a5fa' }}>🎓 FOAI Concepts Demonstrated by Scenarios</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {['BFS/DFS/UCS/Greedy/A*', 'Forward Chaining', 'Backward Chaining', 'Utility-Based Decisions',
              'Planning & Replanning', 'Multi-Agent Coordination', 'Dynamic Environment', 'Uncertainty',
              'PEAS Framework', 'Ambulance Conflict Resolution', 'Knowledge Representation'].map(c => (
              <span key={c} className="badge badge-blue" style={{ fontSize: '0.72rem' }}>{c}</span>
            ))}
          </div>
        </div>

        <div className="grid-2" style={{ gap: 16 }}>
          {Object.entries(scenarios).map(([id, sc]) => (
            <div key={id}
              className="card"
              style={{
                cursor: 'pointer',
                border: selected === id ? '1px solid rgba(59,130,246,0.5)' : '1px solid var(--border)',
                background: selected === id ? 'rgba(59,130,246,0.06)' : 'var(--bg-card)',
              }}
              onClick={() => setSelected(id)}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: '1.8rem' }}>{SCENARIO_ICONS[id] || '📋'}</span>
                  <div>
                    <div style={{ fontWeight: 700 }}>{sc.name}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{id.replace('_', ' ').toUpperCase()}</div>
                  </div>
                </div>
                <span className="badge" style={{ background: `${DIFFICULTY_COLOR[sc.difficulty]}22`, color: DIFFICULTY_COLOR[sc.difficulty] }}>
                  {sc.difficulty}
                </span>
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.6 }}>
                {sc.description}
              </p>

              {sc.auto_events?.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>AUTO-EVENTS</div>
                  {sc.auto_events.map((ev, i) => (
                    <div key={i} style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(239,68,68,0.1)', color: '#f87171', marginBottom: 2 }}>
                      ⚡ {ev.type.replace(/_/g, ' ')} (at tick {ev.delay_ticks})
                    </div>
                  ))}
                </div>
              )}

              <button
                className={`btn btn-sm w-full ${running === id ? 'btn-ghost' : 'btn-primary'}`}
                disabled={loading}
                onClick={(e) => { e.stopPropagation(); handleRun(id); }}>
                {running === id && loading ? '⟳ Running...' : `▶ Run ${sc.name}`}
              </button>
            </div>
          ))}
        </div>

        {Object.keys(scenarios).length === 0 && (
          <div className="empty-state">
            <div className="icon">📋</div>
            <p>Loading scenarios... Make sure the backend is running.</p>
          </div>
        )}

        {/* Demo Procedure */}
        <div className="card mt-4">
          <div style={{ fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            🎬 Demo Procedure (24-Step Flow)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            {[
              '1. Start application & open Simulation',
              '2. Run Scenario 1 or Scenario 7',
              '3. Patient Agent generates CRITICAL emergency',
              '4. Patient requires ICU + Cardiologist',
              '5. Ambulance Agent accepts dispatch',
              '6. Hospital Agents report availability',
              '7. Knowledge Base loads facts',
              '8. Forward Chaining derives eligibility',
              '9. Decision Engine ranks hospitals (utility)',
              '10. Search Engine calculates A* route',
              '11. Ambulance starts navigating',
              '12. Click "Inject Traffic" button',
              '13. Traffic Agent updates road state',
              '14. Click "Hospital Failure" button',
              '15. Hospital Agent reports ICU unavailable',
              '16. Coordinator invalidates old plan',
              '17. Ambulance requests replanning',
              '18. Search Engine generates new route',
              '19. New hospital selected (replan visible)',
              '20. Doctor Agent confirms specialist',
              '21. Patient arrives at new hospital',
              '22. Resources reserved, treatment begins',
              '23. Emergency marked COMPLETED',
              '24. View Analytics for performance metrics',
            ].map((step, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, fontSize: '0.75rem', padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <span style={{ color: 'var(--text-muted)', minWidth: 18 }}>{i+1}.</span>
                <span style={{ color: 'var(--text-secondary)' }}>{step.replace(/^\d+\. /, '')}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
