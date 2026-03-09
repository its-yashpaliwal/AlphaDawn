import React, { useState } from 'react';
import { usePaperTrade } from '../hooks/usePicks';

export default function PickCard({ pick }) {
    const { addToWatchlist } = usePaperTrade();
    const [adding, setAdding] = useState(false);
    const [added, setAdded] = useState(false);

    const handlePaperTrade = async (e) => {
        e.preventDefault();
        setAdding(true);
        const success = await addToWatchlist(pick);
        setAdding(false);
        if (success) {
            setAdded(true);
            setTimeout(() => setAdded(false), 2000);
        }
    };

    const isLong = pick.direction === 'LONG';
    const dirClass = isLong ? 'long' : 'short';

    return (
        <div className={`card pick-card ${dirClass}`}>
            <div className="card-header">
                <div>
                    <div className="pick-symbol">{pick.symbol}</div>
                    <span className={`pick-direction ${dirClass}`}>
                        {isLong ? '▲' : '▼'} {pick.direction}
                    </span>
                </div>
                <span className="badge info">{pick.exchange}</span>
            </div>

            <div className="pick-levels">
                <div className="pick-level">
                    <div className="label">Entry</div>
                    <div className="value entry">₹{pick.entry_price?.toFixed(2)}</div>
                </div>
                <div className="pick-level">
                    <div className="label">Target</div>
                    <div className="value target">₹{pick.target_price?.toFixed(2)}</div>
                </div>
                <div className="pick-level">
                    <div className="label">Stop Loss</div>
                    <div className="value sl">₹{pick.stop_loss?.toFixed(2)}</div>
                </div>
            </div>

            <div className="pick-confidence">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Confidence</span>
                    <span style={{ fontWeight: 600 }}>{(pick.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="confidence-bar">
                    <div className="fill" style={{ width: `${pick.confidence * 100}%` }} />
                </div>
            </div>

            {pick.catalyst && (
                <div className="pick-catalyst">💡 {pick.catalyst}</div>
            )}

            <button
                onClick={handlePaperTrade}
                disabled={adding || added}
                className={`paper-trade-btn ${added ? 'added' : ''}`}
                style={{
                    width: '100%',
                    marginTop: '12px',
                    padding: '8px',
                    borderRadius: '6px',
                    border: '1px solid rgba(124, 92, 255, 0.3)',
                    background: added ? 'var(--accent-green)' : 'rgba(124, 92, 255, 0.1)',
                    color: added ? 'white' : 'var(--accent)',
                    fontWeight: '600',
                    cursor: (adding || added) ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                }}
            >
                {adding ? '⏳ Adding...' : added ? '✅ Added to Watchlist' : '🚀 Paper Trade'}
            </button>
        </div>
    );
}
