import React from 'react';
import { usePaperTrade } from '../hooks/usePicks';

export default function PaperTrading() {
    const { watchlist, loading, removeFromWatchlist, refresh } = usePaperTrade();

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>🚀 Paper Trading Watchlist</h1>
                    <p>Track your active picks and real-time performance</p>
                </div>
                <button
                    onClick={refresh}
                    className="btn-secondary"
                    style={{ padding: '8px 16px', borderRadius: '8px' }}
                >
                    🔄 Refresh Prices
                </button>
            </div>

            <div className="card">
                <div className="card-header">
                    <span className="card-title">📱 Live Performance</span>
                    <span className="badge info">{watchlist.length} active</span>
                </div>

                {loading ? (
                    <div className="skeleton" style={{ height: 300 }} />
                ) : watchlist.length > 0 ? (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Direction</th>
                                    <th>Entry</th>
                                    <th>Target</th>
                                    <th>SL</th>
                                    <th>Live Price</th>
                                    <th>ROI %</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {watchlist.map((item) => (
                                    <tr key={item.symbol}>
                                        <td style={{ fontWeight: 600 }}>{item.symbol}</td>
                                        <td>
                                            <span className={`pick-direction ${item.direction?.toLowerCase()}`}>
                                                {item.direction}
                                            </span>
                                        </td>
                                        <td>₹{item.entry_price?.toFixed(2)}</td>
                                        <td>₹{item.target_price?.toFixed(2)}</td>
                                        <td>₹{item.stop_loss?.toFixed(2)}</td>
                                        <td style={{ fontWeight: 700, color: 'var(--accent)' }}>
                                            {item.current_price ? `₹${item.current_price.toFixed(2)}` : '—'}
                                        </td>
                                        <td style={{
                                            fontWeight: 700,
                                            color: item.roi_pct > 0 ? 'var(--accent-green)' :
                                                item.roi_pct < 0 ? 'var(--accent-red)' : 'inherit'
                                        }}>
                                            {item.roi_pct != null ? `${item.roi_pct > 0 ? '+' : ''}${item.roi_pct}%` : '—'}
                                        </td>
                                        <td>
                                            <span className={`badge ${item.status === 'HIT TARGET' ? 'success' :
                                                    item.status === 'STOP LOSS' ? 'danger' : 'info'
                                                }`}>
                                                {item.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                onClick={() => removeFromWatchlist(item.symbol)}
                                                style={{
                                                    background: 'none',
                                                    border: 'none',
                                                    color: 'var(--accent-red)',
                                                    cursor: 'pointer',
                                                    fontSize: '1.2rem'
                                                }}
                                                title="Remove from watchlist"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="icon">🔭</div>
                        <p>Your watchlist is empty. Go to the dashboard and click "Paper Trade" on a pick!</p>
                    </div>
                )}
            </div>

            <div style={{ marginTop: '24px' }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                    Note: Prices are fetched in real-time from Yahoo Finance whenever you refresh this page.
                </p>
            </div>
        </div>
    );
}
