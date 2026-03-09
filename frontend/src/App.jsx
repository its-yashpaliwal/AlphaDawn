import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import PaperTrading from './pages/PaperTrading';

export default function App() {
    return (
        <BrowserRouter>
            <div className="app-layout">
                {/* ── Sidebar ── */}
                <nav className="sidebar">
                    <div className="sidebar-logo">
                        📈 AlphaDawn
                        <span>AI Trade Intelligence</span>
                    </div>

                    <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">🏠</span> Dashboard
                    </NavLink>
                    <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">📊</span> History
                    </NavLink>
                    <NavLink to="/paper-trading" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">🚀</span> Paper Trading
                    </NavLink>
                    <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span className="icon">⚙️</span> Settings
                    </NavLink>
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
