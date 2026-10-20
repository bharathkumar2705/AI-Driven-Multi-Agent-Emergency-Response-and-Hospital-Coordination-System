const SEVERITY_COLOR = { CRITICAL: '#ef4444', HIGH: '#f97316', MODERATE: '#f59e0b', LOW: '#10b981' };
const STEP_ICON = { completed: '✓', in_progress: '⟳', pending: '○', failed: '✗', invalid: '⚠' };

function PlanStep({ step }) {
  const st = step.status?.toLowerCase().replace('_progress','_progress') || 'pending';
  const norm = st === 'in_progress' ? 'in_progress' : st;
  return (
    <div className="plan-step">
      <div className={`step-icon ${norm}`}>{STEP_ICON[norm] || '○'}</div>
      <div className="step-content">
        <div className="step-name">{step.description}</div>
        {step.details && <div className="step-detail">{step.details}</div>}
      </div>
    </div>
  );
}

export default function DecisionPanel({ emergencies, plans, utilityScores }) {
  const activeEmergency = emergencies?.find(e => e.status === 'ACTIVE');
  if (!activeEmergency) {
    return (
      <div className="decision-panel">
        <div className="decision-panel-header">🧠 AI Decision Engine</div>
        <div className="decision-panel-body" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px 16px' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>💤</div>
          No active emergency. Start a simulation.
        </div>
      </div>
    );
  }

  const plan = plans?.[activeEmergency.emergency_id];
  const scores = activeEmergency.utility_scores || {};
  const scoreList = Object.values(scores);

  const severityColor = SEVERITY_COLOR[activeEmergency.severity] || '#94a3b8';

  return (
    <div className="decision-panel">
      <div className="decision-panel-header">
        🧠 AI Decision Engine
        <span style={{ marginLeft: 'auto', fontSize: '0.72rem' }}>
          {activeEmergency.emergency_id}
        </span>
      </div>
      <div className="decision-panel-body">

        {/* Patient Info */}
        <div style={{ marginBottom: 12, padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, fontSize: '0.78rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>{activeEmergency.patient_id}</strong>
            <span className="badge" style={{ background: `${severityColor}22`, color: severityColor }}>
              {activeEmergency.severity}
            </span>
          </div>
          {activeEmergency.assigned_hospital && (
            <div style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
              → {activeEmergency.assigned_hospital}
              {activeEmergency.replan_count > 0 && (
                <span className="badge badge-yellow" style={{ marginLeft: 6 }}>Replanned ×{activeEmergency.replan_count}</span>
              )}
            </div>
          )}
        </div>

        {/* Hospital Utility Scores */}
        {scoreList.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Hospital Utility Scores
            </div>
            {scoreList.sort((a, b) => b.utility_score - a.utility_score).map(s => (
              <div key={s.hospital_id} className={`hospital-score ${s.hospital_id === activeEmergency.assigned_hospital ? 'selected' : ''} ${!s.eligible ? 'rejected' : ''}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <strong style={{ fontSize: '0.78rem' }}>{s.hospital_name || s.hospital_id}</strong>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: s.eligible ? '#34d399' : '#f87171' }}>
                    {s.eligible ? '✅' : '❌'} {(s.utility_score * 100).toFixed(1)}
                  </span>
                </div>
                {s.rejection_reason && (
                  <div style={{ fontSize: '0.7rem', color: '#f87171' }}>✗ {s.rejection_reason}</div>
                )}
                {s.eligible && (
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    {(s.resource_reasons || []).join(' · ')}
                  </div>
                )}
                <div className="score-bar">
                  <div className="score-fill" style={{ width: `${Math.max(0, s.utility_score * 100)}%`, background: s.eligible ? 'var(--accent-green)' : 'var(--accent-red)' }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plan Steps */}
        {plan && (
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: 6 }}>
              Emergency Plan
              {plan.version > 1 && <span className="badge badge-yellow">v{plan.version} (Replanned)</span>}
              <span className={`badge ${plan.status === 'ACTIVE' ? 'badge-blue' : plan.status === 'COMPLETED' ? 'badge-green' : 'badge-yellow'}`}>{plan.status}</span>
            </div>
            {plan.status === 'INVALID' && plan.invalidation_reason && (
              <div className="replan-alert">
                <strong>⚠️ Plan Invalidated</strong>: {plan.invalidation_reason}
                <div className="replan-flow">
                  <span className="replan-flow-item">OLD PLAN</span>
                  <span className="replan-arrow">→</span>
                  <span className="replan-flow-item" style={{ color: '#fbbf24' }}>INVALIDATED</span>
                  <span className="replan-arrow">→</span>
                  <span className="replan-flow-item" style={{ color: '#34d399' }}>NEW PLAN</span>
                </div>
              </div>
            )}
            <div className="plan-timeline">
              {(plan.steps || []).map(step => (
                <PlanStep key={step.step_number} step={step} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
