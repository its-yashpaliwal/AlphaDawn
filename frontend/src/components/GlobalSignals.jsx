import React from 'react';

export default function GlobalSignals({ signals }) {
    const data = signals || {};
    const hasData = Object.keys(data).length > 0;

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">🌍 Global Signals</span>
                <span className="badge info">Live</span>
            </div>
            <div className="signals-grid">
                {!hasData && (
                    <div style={{ padding: '20px', color: 'var(--text-secondary)' }}>
                        Loading real-time signals...
                    </div>
                )}
                {hasData && Object.entries(data).map(([key, signal]) => {
                    const change = signal.change_pct || 0;
                    const isPositive = change >= 0;
                    return (
                        <div className="signal-item" key={key}>
                            <div className="signal-label">{signal.label || key.replace(/_/g, ' ')}</div>
                            <div className="signal-value">{formatPrice(signal.price)}</div>
                            <div className={`signal-change ${isPositive ? 'positive' : 'negative'}`}>
                                {isPositive ? '▲' : '▼'} {Math.abs(change).toFixed(2)}%
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function formatPrice(price) {
    if (price == null) return '—';
    if (price >= 1000) return price.toLocaleString('en-IN', { maximumFractionDigits: 2 });
    return price.toFixed(2);
}
