import React, { useState } from 'react';
import { usePaperTrade, usePaperTradeHistory } from '../hooks/usePicks';

export default function PaperTrading() {
    const { watchlist, loading, removeFromWatchlist, refresh } = usePaperTrade();
    const { history, summary, loading: historyLoading, refresh: refreshHistory } = usePaperTradeHistory();
    const [activeTab, setActiveTab] = useState('active');
    const [closingSymbol, setClosingSymbol] = useState(null);

    const handleCloseTrade = async (symbol) => {
        setClosingSymbol(symbol);
        try {
            await removeFromWatchlist(symbol);
            await refreshHistory();
        } finally {
            setClosingSymbol(null);
        }
    };

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>🚀 Paper Trading Watchlist</h1>
                    <p>Track your active picks and real-time performance</p>
                </div>
                <button
                    onClick={() => { refresh(); refreshHistory(); }}
                    className="btn-secondary"
                    style={{ padding: '8px 16px', borderRadius: '8px' }}
                >
                    🔄 Refresh Prices
                </button>
            </div>

            {/* Tab Navigation */}
            <div style={{
                display: 'flex',
                gap: '0',
                marginBottom: '20px',
                borderBottom: '2px solid rgba(255,255,255,0.06)',
            }}>
                <button
                    onClick={() => setActiveTab('active')}
                    style={{
                        padding: '12px 24px',
                        background: 'none',
                        border: 'none',
                        borderBottom: activeTab === 'active' ? '2px solid var(--accent)' : '2px solid transparent',
                        color: activeTab === 'active' ? 'var(--accent)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        transition: 'all 0.2s ease',
                        marginBottom: '-2px',
                    }}
                >
                    📊 Active Trades ({watchlist.length})
                </button>
                <button
                    onClick={() => setActiveTab('history')}
                    style={{
                        padding: '12px 24px',
                        background: 'none',
                        border: 'none',
                        borderBottom: activeTab === 'history' ? '2px solid var(--accent)' : '2px solid transparent',
                        color: activeTab === 'history' ? 'var(--accent)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        transition: 'all 0.2s ease',
                        marginBottom: '-2px',
                    }}
                >
                    📜 History ({history.length})
                </button>
            </div>

            {/* Active Trades Tab */}
            {activeTab === 'active' && (
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
                                        <th>Buy Date</th>
                                        <th>Direction</th>
                                        <th>Invested</th>
                                        <th>Entry</th>
                                        <th>Target</th>
                                        <th>SL</th>
                                        <th>Live Price</th>
                                        <th>ROI %</th>
                                        <th>P&L</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {watchlist.map((item) => (
                                        <tr key={item.symbol}>
                                            <td style={{ fontWeight: 600 }}>{item.symbol}</td>
                                            <td style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                                {item.buy_date ? new Date(item.buy_date).toLocaleDateString() : '—'}
                                            </td>
                                            <td>
                                                <span className={`pick-direction ${item.direction?.toLowerCase()}`}>
                                                    {item.direction}
                                                </span>
                                            </td>
                                            <td style={{ color: 'var(--text-muted)' }}>₹{(item.invested_amount || 10000).toLocaleString()}</td>
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
                                            <td style={{
                                                fontWeight: 700,
                                                color: item.pnl > 0 ? 'var(--accent-green)' :
                                                    item.pnl < 0 ? 'var(--accent-red)' : 'inherit'
                                            }}>
                                                {item.pnl != null ? `${item.pnl > 0 ? '+' : ''}₹${Math.abs(item.pnl).toFixed(2)}` : '—'}
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
                                                    onClick={() => handleCloseTrade(item.symbol)}
                                                    disabled={closingSymbol === item.symbol}
                                                    style={{
                                                        background: 'none',
                                                        border: 'none',
                                                        color: 'var(--accent-red)',
                                                        cursor: closingSymbol === item.symbol ? 'wait' : 'pointer',
                                                        fontSize: '1.2rem',
                                                        opacity: closingSymbol === item.symbol ? 0.5 : 1,
                                                    }}
                                                    title="Close trade & move to history"
                                                >
                                                    {closingSymbol === item.symbol ? '⏳' : '🗑️'}
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
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
                <>
                    {/* Summary Cards */}
                    {history.length > 0 && (
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                            gap: '16px',
                            marginBottom: '20px',
                        }}>
                            <div className="card" style={{ padding: '16px', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Total Trades</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{summary.total_trades || 0}</div>
                            </div>
                            <div className="card" style={{ padding: '16px', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Total P&L</div>
                                <div style={{
                                    fontSize: '1.5rem',
                                    fontWeight: 700,
                                    color: (summary.total_pnl || 0) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'
                                }}>
                                    {(summary.total_pnl || 0) >= 0 ? '+' : ''}₹{Math.abs(summary.total_pnl || 0).toFixed(2)}
                                </div>
                            </div>
                            <div className="card" style={{ padding: '16px', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Win Rate</div>
                                <div style={{
                                    fontSize: '1.5rem',
                                    fontWeight: 700,
                                    color: (summary.win_rate || 0) >= 50 ? 'var(--accent-green)' : 'var(--accent-red)'
                                }}>
                                    {summary.win_rate || 0}%
                                </div>
                            </div>
                            <div className="card" style={{ padding: '16px', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>W / L</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                    <span style={{ color: 'var(--accent-green)' }}>{summary.winning_trades || 0}</span>
                                    {' / '}
                                    <span style={{ color: 'var(--accent-red)' }}>{summary.losing_trades || 0}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">📜 Closed Trades</span>
                            <span className="badge info">{history.length} trades</span>
                        </div>

                        {historyLoading ? (
                            <div className="skeleton" style={{ height: 300 }} />
                        ) : history.length > 0 ? (
                            <div className="table-container">
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Symbol</th>
                                            <th>Direction</th>
                                            <th>Invested</th>
                                            <th>Entry</th>
                                            <th>Exit</th>
                                            <th>ROI %</th>
                                            <th>P&L</th>
                                            <th>Buy Date</th>
                                            <th>Closed</th>
                                            <th>Result</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {history.map((item, idx) => (
                                            <tr key={`${item.symbol}-${idx}`}>
                                                <td style={{ fontWeight: 600 }}>{item.symbol}</td>
                                                <td>
                                                    <span className={`pick-direction ${item.direction?.toLowerCase()}`}>
                                                        {item.direction}
                                                    </span>
                                                </td>
                                                <td style={{ color: 'var(--text-muted)' }}>₹{(item.invested_amount || 10000).toLocaleString()}</td>
                                                <td>₹{item.entry_price?.toFixed(2)}</td>
                                                <td style={{ fontWeight: 600 }}>₹{item.exit_price?.toFixed(2)}</td>
                                                <td style={{
                                                    fontWeight: 700,
                                                    color: item.roi_pct > 0 ? 'var(--accent-green)' :
                                                        item.roi_pct < 0 ? 'var(--accent-red)' : 'inherit'
                                                }}>
                                                    {item.roi_pct != null ? `${item.roi_pct > 0 ? '+' : ''}${item.roi_pct}%` : '—'}
                                                </td>
                                                <td style={{
                                                    fontWeight: 700,
                                                    color: item.pnl > 0 ? 'var(--accent-green)' :
                                                        item.pnl < 0 ? 'var(--accent-red)' : 'inherit'
                                                }}>
                                                    {item.pnl != null ? `${item.pnl > 0 ? '+' : '-'}₹${Math.abs(item.pnl).toFixed(2)}` : '—'}
                                                </td>
                                                <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                                    {item.buy_date ? new Date(item.buy_date).toLocaleDateString() : '—'}
                                                </td>
                                                <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                                    {item.exit_date ? new Date(item.exit_date).toLocaleDateString() : '—'}
                                                </td>
                                                <td>
                                                    <span className={`badge ${
                                                        item.result === 'PROFIT' ? 'success' :
                                                        item.result === 'LOSS' ? 'danger' : 'info'
                                                    }`} style={{
                                                        display: 'inline-flex',
                                                        alignItems: 'center',
                                                        gap: '4px',
                                                    }}>
                                                        {item.result === 'PROFIT' ? '🟢' : item.result === 'LOSS' ? '🔴' : '⚪'} {item.result}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="empty-state">
                                <div className="icon">📭</div>
                                <p>No closed trades yet. Close an active trade to see it here.</p>
                            </div>
                        )}
                    </div>
                </>
            )}

            <div style={{ marginTop: '24px' }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                    Note: Each paper trade uses a fixed ₹10,000 INR investment. Prices are fetched in real-time from Yahoo Finance.
                </p>
            </div>
        </div>
    );
}
