import React, { useState } from 'react';
import { usePicks, useNews, useSignals } from '../hooks/usePicks';
import PickCard from '../components/PickCard';
import NewsFeed from '../components/NewsFeed';
import AgentStatus from '../components/AgentStatus';
import GlobalSignals from '../components/GlobalSignals';

export default function Dashboard() {
    const { picks, loading: picksLoading } = usePicks();
    const { news, loading: newsLoading } = useNews();
    const { signals } = useSignals();

    const [running, setRunning] = useState(false);
    const handleRunPipeline = async () => {
        setRunning(true);
        try {
            const res = await fetch('/api/v1/pipeline/run', { method: 'POST' });
            if (!res.ok) throw new Error('Failed to run pipeline');
            // The API now waits for completion. Reload the page to fetch fresh data.
            window.location.reload();
        } catch (err) {
            alert(err.message || 'Error running pipeline');
            setRunning(false);
        }
    };

    return (
        <div>
            {/* Full-screen loading overlay */}
            {running && (
                <div style={{
                    position: 'fixed',
                    top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(15, 23, 42, 0.85)',
                    backdropFilter: 'blur(8px)',
                    zIndex: 9999,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    color: 'white'
                }}>
                    <div className="icon" style={{ fontSize: '3rem', marginBottom: '1rem', animation: 'pulse 2s infinite' }}>🤖</div>
                    <h2 style={{ margin: '0 0 10px 0' }}>AlphaDawn Agents Running...</h2>
                    <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', textAlign: 'center' }}>
                        The pipeline is ingesting data, classifying catalysts, and generating fresh trade setups. This may take a minute or two.
                    </p>
                </div>
            )}

            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>📈 Today's Dashboard</h1>
                    <p>{new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
                <button
                    onClick={handleRunPipeline}
                    disabled={running}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: running ? '#374151' : 'var(--accent)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: running ? 'not-allowed' : 'pointer',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        transition: 'background-color 0.2s',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                >
                    {running ? '⏳ Starting...' : '▶️ Run Pipeline'}
                </button>
            </div>

            {/* Global Signals */}
            <div style={{ marginBottom: 24 }}>
                <GlobalSignals signals={signals} />
            </div>

            {/* Today's Picks */}
            <div style={{ marginBottom: 24 }}>
                <div className="card-header" style={{ marginBottom: 12, padding: '0 4px' }}>
                    <span className="card-title">🎯 Today's Trade Setups</span>
                    <span className="badge success">{picks.length} picks</span>
                </div>

                {picksLoading ? (
                    <div className="grid-2">
                        {[1, 2].map((i) => (
                            <div key={i} className="card skeleton" style={{ height: 220 }} />
                        ))}
                    </div>
                ) : picks.length > 0 ? (
                    <div className="grid-2">
                        {picks.map((pick) => (
                            <PickCard key={pick.id || pick.symbol} pick={pick} />
                        ))}
                    </div>
                ) : (
                    <div className="card">
                        <div className="empty-state">
                            <div className="icon">🧘</div>
                            <p>No trade setups today. The pipeline hasn't run yet.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* News + Agent Status side-by-side */}
            <div className="grid-2" style={{ alignItems: 'start' }}>
                <NewsFeed news={news} />
                <AgentStatus />
            </div>
        </div>
    );
}
