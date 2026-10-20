import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import './styles/global.css';
import Sidebar from './components/Sidebar';
import { useSimulation } from './hooks/useSimulation';

import Dashboard from './pages/Dashboard';
import LiveSimulation from './pages/LiveSimulation';
import Agents from './pages/Agents';
import SearchLab from './pages/SearchLab';
import KnowledgeBase from './pages/KnowledgeBase';
import Communication from './pages/Communication';
import Scenarios from './pages/Scenarios';
import Analytics from './pages/Analytics';

export default function App() {
  const { simState, messages, connected, status, start, pause, resume, reset, injectEvent } = useSimulation();

  const activeEmergencies = simState?.emergencies?.filter(e => e.status === 'ACTIVE').length || 0;

  const sharedProps = { simState, messages, connected, status, start, pause, resume, reset, injectEvent };

  return (
    <BrowserRouter>
      <div className="layout">
        <Sidebar connected={connected} activeEmergencies={activeEmergencies} />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard {...sharedProps} />} />
            <Route path="/simulation" element={<LiveSimulation {...sharedProps} />} />
            <Route path="/agents" element={<Agents {...sharedProps} />} />
            <Route path="/search" element={<SearchLab />} />
            <Route path="/knowledge" element={<KnowledgeBase {...sharedProps} />} />
            <Route path="/communication" element={<Communication messages={messages} connected={connected} />} />
            <Route path="/scenarios" element={<Scenarios onStart={start} onReset={reset} />} />
            <Route path="/analytics" element={<Analytics {...sharedProps} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
