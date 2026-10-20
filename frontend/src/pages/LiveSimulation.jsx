import React, { useState } from 'react';
import CityGrid from '../components/CityGrid';
import DecisionPanel from '../components/DecisionPanel';
import MessageFeed from '../components/MessageFeed';
import '../styles/simulation.css';
import { api } from '../services/api';

const SEVERITIES = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL'];
const SPECIALISTS = ['Cardiologist', 'Neurologist', 'Orthopedic', 'General Surgeon', 'Oncologist', 'Pediatrician'];
const EMERGENCY_TYPES = ['Cardiac Arrest', 'Stroke', 'Trauma', 'Fracture', 'Burns', 'Poisoning'];
let patientCounter = 100;

const inputStyle = {
  background: 'var(--bg-deep)', color: 'var(--text-primary)',
  border: '1px solid var(--border)', borderRadius: 6,
  padding: '6px 10px', fontSize: '0.82rem', width: '100%'
};

export default function LiveSimulation({ simState, messages, status, start, pause, resume, reset, injectEvent }) {
  const [scenario, setScenario] = useState('scenario_1');
  const [newPatient, setNewPatient] = useState({
    severity: 'CRITICAL', specialist: 'Cardiologist',
    row: 4, col: 4, type: 'Cardiac Arrest'
  });
  const [showNewPatient, setShowNewPatient] = useState(false);

  const emergencies = simState?.emergencies || [];
  const plans = simState?.active_plans || {};

  const handleNewEmergency = async () => {
    patientCounter++;
    const pid = `P${patientCounter}`;
    await api.addEmergency({
      patient_id: pid,
      name: `Patient ${pid}`,
      location: { row: parseInt(newPatient.row), col: parseInt(newPatient.col) },
      emergency_type: newPatient.type,
      severity: newPatient.severity,
      required_specialist: newPatient.specialist,
      required_resources: (newPatient.severity === 'CRITICAL' || newPatient.severity === 'HIGH') ? ['ICU'] : [],
    });
    setShowNewPatient(false);
  };

  const completed = emergencies.filter(e => e.status === 'COMPLETED').length;
  const active = emergencies.filter(e => e.status === 'ACTIVE').length;
  const totalReplans = emergencies.reduce((sum, e) => sum + (e.replan_count || 0), 0);

  return (
    <div className="page-root">
      <div className="page-header">
        <div>
          <div className="page-title">🗺️ Live Simulation</div>
          <div className="page-subtitle">
            Real-time multi-agent city grid — Tick #{simState?.tick || 0}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            ✅ {completed} done | 🔴 {active} active | 🔄 {totalReplans} replans
          </span>
          <span className={`badge ${status === 'RUNNING' ? 'badge-green' : status === 'PAUSED' ? 'badge-yellow' : 'badge-gray'}`}>
            {status}
          </span>
        </div>
      </div>

      <div className="page-body">
        {/* Simulation Controls */}
        <div className="sim-controls mb-4">
          <select value={scenario} onChange={e => setScenario(e.target.value)}
            style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 10px', fontSize: '0.82rem' }}>
            {['scenario_1','scenario_2','scenario_3','scenario_4','scenario_5','scenario_6','scenario_7'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
            ))}
          </select>

          {(status === 'IDLE' || status === 'PAUSED' || !status) ? (
            <button className="btn btn-success btn-sm" onClick={() => status === 'PAUSED' ? resume() : start(scenario)}>
              ▶ {status === 'PAUSED' ? 'Resume' : 'Start'}
            </button>
          ) : (
            <button className="btn btn-warning btn-sm" onClick={pause}>⏸ Pause</button>
          )}
          <button className="btn btn-ghost btn-sm" onClick={() => reset(scenario)}>↺ Reset</button>

          <div className="divider" />

          <button className="btn btn-danger btn-sm" onClick={() => injectEvent('ROAD_CONGESTED', { road_id: 'R045' })}>🚦 Traffic Jam</button>
          <button className="btn btn-danger btn-sm" onClick={() => injectEvent('HOSPITAL_ICU_FULL', { hospital_id: 'H1' })}>🏥 ICU Full</button>
          <button className="btn btn-danger btn-sm" onClick={() => injectEvent('DOCTOR_UNAVAILABLE', { doctor_id: 'D01' })}>👨‍⚕️ Dr. Unavailable</button>
          <button className="btn btn-warning btn-sm" onClick={() => setShowNewPatient(true)}>➕ New Emergency</button>
        </div>

        {/* New Patient Modal */}
        {showNewPatient && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <div className="card" style={{ width: 400, padding: 24 }}>
              <h3 style={{ marginBottom: 16 }}>➕ New Emergency Patient</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Emergency Type</label>
                  <select value={newPatient.type} onChange={e => setNewPatient(p => ({...p, type: e.target.value}))} style={inputStyle}>
                    {EMERGENCY_TYPES.map(t => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Severity</label>
                  <select value={newPatient.severity} onChange={e => setNewPatient(p => ({...p, severity: e.target.value}))} style={inputStyle}>
                    {SEVERITIES.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Required Specialist</label>
                  <select value={newPatient.specialist} onChange={e => setNewPatient(p => ({...p, specialist: e.target.value}))} style={inputStyle}>
                    {SPECIALISTS.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <div>
                    <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Row (0–9)</label>
                    <input type="number" min={0} max={9} value={newPatient.row}
                      onChange={e => setNewPatient(p => ({...p, row: e.target.value}))} style={inputStyle} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>Col (0–9)</label>
                    <input type="number" min={0} max={9} value={newPatient.col}
                      onChange={e => setNewPatient(p => ({...p, col: e.target.value}))} style={inputStyle} />
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                <button className="btn btn-primary btn-sm" onClick={handleNewEmergency}>Add Emergency</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowNewPatient(false)}>Cancel</button>
              </div>
            </div>
          </div>
        )}

        <div className="sim-page">
          {/* City Grid Canvas */}
          <div className="city-grid-wrap">
            <div className="city-grid-canvas">
              <CityGrid simState={simState} />
            </div>
            {/* Ambulance Status Strip */}
            <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '10px 14px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Live Ambulance Status
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {(simState?.ambulances || []).map(a => (
                  <div key={a.ambulance_id} style={{
                    fontSize: '0.72rem', padding: '4px 10px', borderRadius: 6,
                    background: a.status === 'IDLE' ? 'rgba(255,255,255,0.04)' : 'rgba(59,130,246,0.12)',
                    border: `1px solid ${a.status === 'IDLE' ? 'var(--border)' : 'rgba(59,130,246,0.3)'}`
                  }}>
                    🚑 <strong>{a.ambulance_id}</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{a.status?.replace(/_/g, ' ')}</span>
                    {a.assigned_patient && <span style={{ color: '#93c5fd' }}> → {a.assigned_patient}</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel: Decisions + Messages */}
          <div className="sim-panel">
            <DecisionPanel emergencies={emergencies} plans={plans} />
            <div className="decision-panel">
              <div className="decision-panel-header">
                💬 Agent Communication
                <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>{messages.length} msgs</span>
              </div>
              <MessageFeed messages={messages.slice(0, 40)} maxHeight={280} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
