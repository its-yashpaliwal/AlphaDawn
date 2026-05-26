import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import PaperTrading from './pages/PaperTrading';

export default function App() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    return (
        <BrowserRouter>
            <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                {/* ── Sidebar ── */}
                <nav className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
                    <div className="sidebar-logo">
                        📈 {!sidebarCollapsed && 'AlphaDawn'}
                        {!sidebarCollapsed && <span>AI Trade Intelligence</span>}
                    </div>

                    <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">🏠</span> {!sidebarCollapsed && 'Dashboard'}
                    </NavLink>
                    <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">📊</span> {!sidebarCollapsed && 'History'}
                    </NavLink>
                    <NavLink to="/paper-trading" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">🚀</span> {!sidebarCollapsed && 'Paper Trading'}
                    </NavLink>
                    <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">⚙️</span> {!sidebarCollapsed && 'Settings'}
                    </NavLink>

                    {/* Toggle Button */}
                    <button
                        className="sidebar-toggle"
                        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                        title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                    >
                        <svg
                            width="16"
                            height="16"
                            viewBox="0 0 16 16"
                            fill="none"
                            style={{
                                transform: sidebarCollapsed ? 'rotate(180deg)' : 'rotate(0deg)',
                                transition: 'transform 0.3s ease',
                            }}
                        >
                            <path
                                d="M10 12L6 8L10 4"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            />
                        </svg>
                    </button>
                </nav>

                {/* ── Main content ── */}
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/history" element={<History />} />
                        <Route path="/paper-trading" element={<PaperTrading />} />
                        <Route path="/settings" element={<Settings />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}
