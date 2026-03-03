import { Outlet, NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Sprout,
    ShieldCheck,
    Droplet,
    LineChart,
    Map,
    Leaf,
    MessageSquare
} from 'lucide-react';
import './Layout.css';

export default function Layout() {
    const navItems = [
        { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
        { to: "/chat", icon: MessageSquare, label: "Ask AgroFix AI" },
        { to: "/disease-scanner", icon: Sprout, label: "Disease Scanner" },
        { to: "/pesticide-check", icon: ShieldCheck, label: "Pesticide Check" },
        { to: "/soil-health", icon: Droplet, label: "Soil Health" },
        { to: "/harvest-advisor", icon: LineChart, label: "Harvest Advisor" },
        { to: "/digital-twin", icon: Map, label: "Digital Twin Map" },
        { to: "/sustainability", icon: Leaf, label: "Sustainability (ESG)" },
    ];

    return (
        <div className="layout-container">
            <aside className="sidebar glass-panel">
                <div className="logo-container">
                    <h2>Agro<span>Fix</span></h2>
                </div>

                <nav className="nav-menu">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>
            </aside>

            <main className="main-content">
                <header className="top-header glass-panel">
                    <div className="header-greeting">
                        <h1>Welcome back, Farmer.</h1>
                        <p>AgroFix Intelligence Engine is online.</p>
                    </div>
                </header>
                <div className="content-area">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
