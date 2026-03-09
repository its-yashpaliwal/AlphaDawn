import React from 'react';

export default function NewsFeed({ news }) {
    if (!news || news.length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <span className="card-title">📰 Latest News</span>
                </div>
                <div className="empty-state">
                    <div className="icon">📭</div>
                    <p>No news items yet. Run the pipeline to fetch latest news.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">📰 Latest News</span>
                <span className="badge info">{news.length} items</span>
            </div>
            <div className="news-list">
                {news.map((item, idx) => (
                    <div className="news-item" key={item.id || idx}>
                        <span className="news-source">{formatSource(item.source)}</span>
                        <div>
                            <div className="news-headline">{item.headline}</div>
                            <div className="news-meta">
                                {item.is_catalyst && (
                                    <span className={`sentiment-tag ${item.is_catalyst === 'CATALYST' ? 'catalyst' : 'noise'}`}>
                                        {item.is_catalyst}
                                    </span>
                                )}
                                {item.relevance_score != null && (
                                    <span>Score: {(item.relevance_score * 100).toFixed(0)}</span>
                                )}
                                {item.scraped_at && (
                                    <span>{formatTime(item.scraped_at)}</span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function formatSource(source) {
    const map = {
        moneycontrol: 'MC',
        economictimes: 'ET',
        business_standard: 'BS',
        nse_announcement: 'NSE',
        bse_announcement: 'BSE',
        nse_bulk_deal: 'DEAL',
        twitter: 'X',
        global_signals: 'GLOBAL',
    };
    return map[source] || source?.toUpperCase()?.slice(0, 4) || '—';
}

function formatTime(isoString) {
    try {
        const d = new Date(isoString);
        return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    } catch {
        return '';
    }
}
