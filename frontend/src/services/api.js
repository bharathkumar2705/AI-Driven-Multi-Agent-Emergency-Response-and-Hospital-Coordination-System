const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const req = async (method, path, body) => {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) throw new Error(`${method} ${path} → ${res.status}`);
  return res.json();
};

export const api = {
  // Simulation
  startSim: (scenario) => req('POST', '/simulation/start', { scenario }),
  pauseSim: () => req('POST', '/simulation/pause', {}),
  resumeSim: () => req('POST', '/simulation/resume', {}),
  resetSim: (scenario) => req('POST', '/simulation/reset', { scenario }),
  getSimState: () => req('GET', '/simulation/state'),
  injectEvent: (event_type, data) => req('POST', '/simulation/event', { event_type, data }),
  addEmergency: (patient) => req('POST', '/simulation/emergency', patient),
  getScenarios: () => req('GET', '/simulation/scenarios'),
  getAnalytics: () => req('GET', '/simulation/analytics'),

  // Resources
  getHospitals: () => req('GET', '/hospitals'),
  getAmbulances: () => req('GET', '/ambulances'),
  getPatients: () => req('GET', '/patients'),
  getDoctors: () => req('GET', '/doctors'),
  getRoads: () => req('GET', '/roads'),
  getEmergencies: () => req('GET', '/emergencies'),

  // Agents
  getAgents: () => req('GET', '/agents'),
  getMessages: (limit = 100) => req('GET', `/agents/messages/all?limit=${limit}`),

  // Search
  runSearch: (algorithm, start, goal) => req('POST', '/search/run', { algorithm, start, goal }),
  compareSearch: (start, goal) => req('POST', '/search/compare', { algorithm: 'astar', start, goal }),
  getGraph: () => req('GET', '/search/graph'),

  // Knowledge
  getKnowledge: () => req('GET', '/knowledge/snapshot'),
  runForwardChain: () => req('POST', '/knowledge/forward-chain', {}),
  runBackwardChain: (hospital_id, patient_id) =>
    req('POST', '/knowledge/backward-chain', { hospital_id, patient_id }),
};
