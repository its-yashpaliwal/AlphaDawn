import React, { useState } from 'react';

const DEFAULT_SOURCES = {
    twitter: { label: 'Twitter / X', enabled: true },
    moneycontrol: { label: 'MoneyControl', enabled: true },
    economictimes: { label: 'Economic Times', enabled: true },
    business_standard: { label: 'Business Standard', enabled: true },
    nse: { label: 'NSE Announcements', enabled: true },
    bse: { label: 'BSE Announcements', enabled: true },
    global_signals: { label: 'Global Signals (Crude, Gold, SGX)', enabled: true },
};

const DEFAULT_DELIVERY = {
    telegram: { label: 'Telegram Bot', enabled: false },
    email: { label: 'Email Report', enabled: false },
};

export default function Settings() {
    const [sources, setSources] = useState(DEFAULT_SOURCES);
    const [delivery, setDelivery] = useState(DEFAULT_DELIVERY);
    const [cron, setCron] = useState('0 7 * * 1-5');

    const toggleSource = (key) => {
        setSources((prev) => ({
            ...prev,
            [key]: { ...prev[key], enabled: !prev[key].enabled },
        }));
    };

    const toggleDelivery = (key) => {
        setDelivery((prev) => ({
            ...prev,
            [key]: { ...prev[key], enabled: !prev[key].enabled },
        }));
    };

    return (
        <div>
            <div className="page-header">
                <h1>⚙️ Settings</h1>
                <p>Configure agent sources, delivery channels, and schedule</p>
            </div>

            {/* Data Sources */}
            <div className="card settings-section" style={{ marginBottom: 24 }}>
                <h3>📡 Data Sources</h3>
                {Object.entries(sources).map(([key, source]) => (
                    <div className="settings-row" key={key}>
                        <label>{source.label}</label>
                        <label className="toggle">
                            <input
                                type="checkbox"
                                checked={source.enabled}
                                onChange={() => toggleSource(key)}
                            />
                            <span className="slider" />
                        </label>
                    </div>
                ))}
            </div>

            {/* Delivery Channels */}
            <div className="card settings-section" style={{ marginBottom: 24 }}>
                <h3>📬 Delivery Channels</h3>
                {Object.entries(delivery).map(([key, channel]) => (
                    <div className="settings-row" key={key}>
                        <label>{channel.label}</label>
                        <label className="toggle">
                            <input
                                type="checkbox"
                                checked={channel.enabled}
                                onChange={() => toggleDelivery(key)}
                            />
                            <span className="slider" />
                        </label>
                    </div>
                ))}
            </div>

            {/* Schedule */}
            <div className="card settings-section" style={{ marginBottom: 24 }}>
                <h3>⏰ Schedule</h3>
                <div className="settings-row">
                    <label>Cron Expression</label>
                    <input
                        type="text"
                        value={cron}
                        onChange={(e) => setCron(e.target.value)}
                        style={{
                            background: 'var(--bg-glass)',
                            border: '1px solid var(--border-color)',
                            borderRadius: 'var(--radius-sm)',
                            padding: '8px 12px',
                            color: 'var(--text-primary)',
                            fontFamily: 'monospace',
                            fontSize: '0.85rem',
                            width: '200px',
                        }}
                    />
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', padding: '8px 16px' }}>
                    Default: <code>0 7 * * 1-5</code> — runs at 7:00 AM IST on weekdays
                </p>
            </div>

            {/* Save */}
            <button className="btn btn-primary">Save Settings</button>
        </div>
    );
}
