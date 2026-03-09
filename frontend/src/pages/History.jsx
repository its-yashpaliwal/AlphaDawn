import React from 'react';
import { usePickHistory } from '../hooks/usePicks';
import PnLTracker from '../components/PnLTracker';

export default function History() {
    const { history, loading } = usePickHistory();

    return (
        <div>
            <div className="page-header">
                <h1>📊 Pick History</h1>
                <p>Track past picks, outcomes, and overall performance</p>
            </div>

            {/* PnL Chart */}
            <div style={{ marginBottom: 24 }}>
                <PnLTracker history={history} />
            </div>

            {/* History Table */}
            <div className="card">
                <div className="card-header">
                    <span className="card-title">📋 Past Picks</span>
                    <span className="badge info">{history.length} total</span>
                </div>

                {loading ? (
                    <div className="skeleton" style={{ height: 200 }} />
                ) : history.length > 0 ? (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Symbol</th>
                                    <th>Direction</th>
                                    <th>Entry</th>
                                    <th>Target</th>
                                    <th>SL</th>
                                    <th>Outcome</th>
                                    <th>Return</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((pick) => (
                                    <tr key={pick.id}>
                                        <td>{new Date(pick.created_at).toLocaleDateString('en-IN')}</td>
                                        <td style={{ fontWeight: 600 }}>{pick.symbol}</td>
                                        <td>
                                            <span className={`pick-direction ${pick.direction?.toLowerCase()}`}>
                                                {pick.direction}
                                            </span>
                                        </td>
                                        <td>₹{pick.entry_price?.toFixed(2)}</td>
                                        <td>₹{pick.target_price?.toFixed(2)}</td>
                                        <td>₹{pick.stop_loss?.toFixed(2)}</td>
                                        <td>
                                            <span className={`badge ${pick.outcome === 'hit_target' ? 'success' :
                                                    pick.outcome === 'hit_sl' ? 'danger' : 'warning'
                                                }`}>
                                                {pick.outcome === 'hit_target' ? '✅ Target' :
                                                    pick.outcome === 'hit_sl' ? '❌ SL Hit' : '⏳ Open'}
                                            </span>
                                        </td>
                                        <td style={{
                                            fontWeight: 600,
                                            color: pick.actual_return_pct > 0 ? 'var(--accent-green)' :
                                                pick.actual_return_pct < 0 ? 'var(--accent-red)' : 'var(--text-muted)'
                                        }}>
                                            {pick.actual_return_pct != null
                                                ? `${pick.actual_return_pct > 0 ? '+' : ''}${pick.actual_return_pct.toFixed(2)}%`
                                                : '—'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="icon">📭</div>
                        <p>No historical picks yet.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
