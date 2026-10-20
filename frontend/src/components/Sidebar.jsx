import { useLocation, Link } from 'react-router-dom';
import '../styles/sidebar.css';

const NAV = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/simulation', icon: '🗺️', label: 'Live Simulation' },
  { path: '/agents', icon: '🤖', label: 'Agents' },
  { path: '/search', icon: '🔍', label: 'Search Lab' },
  { path: '/knowledge', icon: '🧠', label: 'Knowledge Base' },
  { path: '/communication', icon: '💬', label: 'Communication' },
  { path: '/scenarios', icon: '📋', label: 'Scenarios' },
  { path: '/analytics', icon: '📈', label: 'Analytics' },
];

export default function Sidebar({ connected, activeEmergencies = 0 }) {
  const location = useLocation();
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-title">🚨 FOAI System</span>
        <span className="logo-sub">Multi-Agent Emergency Response</span>
      </div>

      <div className="sidebar-ws">
        <span className={`dot ${connected ? 'dot-green' : 'dot-red'}`} />
        {connected ? 'Backend Connected' : 'Connecting...'}
      </div>

      <nav className="nav-section">
        <div className="nav-section-label">Navigation</div>
        {NAV.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item${location.pathname === item.path ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
            {item.path === '/simulation' && activeEmergencies > 0 && (
              <span className="nav-badge">{activeEmergencies}</span>
            )}
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        FOAI Case Study v1.0<br />
        Multi-Agent AI System
      </div>
    </aside>
  );
}
