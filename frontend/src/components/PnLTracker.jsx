import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PnLTracker({ history = [] }) {
    // Compute PnL stats
    const resolved = history.filter((p) => p.actual_return_pct != null);
    const totalPnL = resolved.reduce((sum, p) => sum + (p.actual_return_pct || 0), 0);
    const wins = resolved.filter((p) => p.outcome === 'hit_target').length;
    const losses = resolved.filter((p) => p.outcome === 'hit_sl').length;
    const winRate = resolved.length > 0 ? ((wins / resolved.length) * 100).toFixed(0) : '—';

    // Build cumulative PnL chart data
    const chartData = [];
    let cumulative = 0;
    resolved.forEach((pick, i) => {
        cumulative += pick.actual_return_pct || 0;
        chartData.push({
            name: `#${i + 1}`,
            pnl: parseFloat(cumulative.toFixed(2)),
        });
    });

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">💰 P&L Tracker</span>
            </div>

            <div className="pnl-summary">
                <div className="pnl-stat">
                    <div className="label">Total P&L</div>
                    <div className={`value ${totalPnL >= 0 ? 'positive' : 'negative'}`}>
                        {totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(2)}%
                    </div>
                </div>
                <div className="pnl-stat">
                    <div className="label">Win Rate</div>
                    <div className="value">{winRate}%</div>
                </div>
                <div className="pnl-stat">
                    <div className="label">Wins</div>
                    <div className="value positive">{wins}</div>
                </div>
                <div className="pnl-stat">
                    <div className="label">Losses</div>
                    <div className="value negative">{losses}</div>
                </div>
            </div>

            {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#7c5cff" stopOpacity={0.3} />
                                <stop offset="100%" stopColor="#7c5cff" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="name" stroke="#555577" fontSize={11} />
                        <YAxis stroke="#555577" fontSize={11} tickFormatter={(v) => `${v}%`} />
                        <Tooltip
                            contentStyle={{
                                background: '#1a1a2e',
                                border: '1px solid rgba(124,92,255,0.2)',
                                borderRadius: '8px',
                                color: '#eaeaf4',
                                fontSize: '0.8rem',
                            }}
                            formatter={(value) => [`${value}%`, 'Cumulative P&L']}
                        />
                        <Area
                            type="monotone"
                            dataKey="pnl"
                            stroke="#7c5cff"
                            strokeWidth={2}
                            fill="url(#pnlGradient)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            ) : (
                <div className="empty-state">
                    <p>No resolved picks yet to track P&L.</p>
                </div>
            )}
        </div>
    );
}
