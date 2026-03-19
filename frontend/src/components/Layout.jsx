import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const farmerNav = [
  { section: 'Overview', items: [
    { to: '/dashboard', icon: '🏠', label: 'Dashboard' },
  ]},
  { section: 'AI Tools', items: [
    { to: '/chat',      icon: '💬', label: 'AI Chat' },
    { to: '/disease',   icon: '🔬', label: 'Disease Scanner' },
    { to: '/soil',      icon: '🧪', label: 'Soil Health' },
    { to: '/harvest',   icon: '🌾', label: 'Harvest Advisor' },
  ]},
  { section: 'Insights', items: [
    { to: '/esg',       icon: '📊', label: 'ESG Score' },
    { to: '/reports',   icon: '📄', label: 'Reports' },
  ]},
];

const managerNav = [
  { section: 'Overview', items: [
    { to: '/dashboard', icon: '📈', label: 'Dashboard' },
  ]},
  { section: 'Management', items: [
    { to: '/farmers',   icon: '👥', label: 'All Farmers' },
  ]},
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const navSections = user?.role === 'manager' ? managerNav : farmerNav;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = (user?.name || user?.email || 'U')
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <span className="logo-icon">🌱</span>
          <span className="logo-text">AgroFix</span>
        </div>

        <nav className="sidebar-nav">
          {navSections.map(sec => (
            <div className="sidebar-section" key={sec.section}>
              <div className="sidebar-section-title">{sec.section}</div>
              {sec.items.map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-badge">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <div className="user-name">{user?.name || user?.email}</div>
              <div className="user-role">{user?.role}</div>
            </div>
            <button className="logout-btn" onClick={handleLogout} title="Logout">
              🚪
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
