import React from 'react';

const AGENTS = [
    { name: 'TwitterAgent', icon: '🐦' },
    { name: 'NewsScraperAgent', icon: '📰' },
    { name: 'ExchangeAgent', icon: '🏛️' },
    { name: 'GlobalSignalsAgent', icon: '🌍' },
    { name: 'CleanerAgent', icon: '🧹' },
    { name: 'RankerAgent', icon: '📊' },
    { name: 'CatalystAgent', icon: '🔬' },
    { name: 'StockDataAgent', icon: '📈' },
    { name: 'TradeSetupAgent', icon: '🎯' },
    { name: 'Orchestrator', icon: '🧠' },
];

export default function AgentStatus({ statuses = {} }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">🤖 Agent Status</span>
            </div>
            <div className="agent-grid">
                {AGENTS.map((agent) => {
                    const status = statuses[agent.name] || 'idle';
                    const duration = statuses[`${agent.name}_ms`];
                    return (
                        <div className="agent-item" key={agent.name}>
                            <span className={`agent-status-dot ${status}`} />
                            <span className="agent-name">{agent.icon} {agent.name}</span>
                            {duration != null && (
                                <span className="agent-duration">{duration.toFixed(0)}ms</span>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
