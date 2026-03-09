import { useState, useEffect } from 'react';

const API_BASE = '/api/v1';

export function usePicks() {
    const [picks, setPicks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchPicks() {
            try {
                setLoading(true);
                const res = await fetch(`${API_BASE}/picks`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setPicks(data.picks || []);
            } catch (err) {
                setError(err.message);
                setPicks([]);
            } finally {
                setLoading(false);
            }
        }
        fetchPicks();
    }, []);

    return { picks, loading, error };
}

export function useNews() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchNews() {
            try {
                const res = await fetch(`${API_BASE}/news`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setNews(data.items || []);
            } catch {
                setNews([]);
            } finally {
                setLoading(false);
            }
        }
        fetchNews();
    }, []);

    return { news, loading };
}

export function useSignals() {
    const [signals, setSignals] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchSignals() {
            try {
                const res = await fetch(`${API_BASE}/signals`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setSignals(data || {});
            } catch {
                setSignals({});
            } finally {
                setLoading(false);
            }
        }
        fetchSignals();
    }, []);

    return { signals, loading };
}

export function usePickHistory() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchHistory() {
            try {
                const res = await fetch(`${API_BASE}/picks/history?days=30`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setHistory(data.picks || []);
            } catch {
                setHistory([]);
            } finally {
                setLoading(false);
            }
        }
        fetchHistory();
    }, []);

    return { history, loading };
}

export function usePaperTrade() {
    const [watchlist, setWatchlist] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchWatchlist = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/paper-trade/watchlist`);
            const data = await res.json();
            setWatchlist(data.watchlist || []);
        } catch (err) {
            console.error('Failed to fetch watchlist:', err);
        } finally {
            setLoading(false);
        }
    };

    const addToWatchlist = async (pick) => {
        try {
            const res = await fetch(`${API_BASE}/paper-trade/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: pick.symbol,
                    entry_price: pick.entry_price,
                    target_price: pick.target_price,
                    stop_loss: pick.stop_loss,
                    direction: pick.direction,
                    catalyst_summary: pick.catalyst_summary || pick.catalyst || ''
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                await fetchWatchlist();
                return true;
            }
            return false;
        } catch (err) {
            console.error('Failed to add to watchlist:', err);
            return false;
        }
    };

    const removeFromWatchlist = async (symbol) => {
        try {
            await fetch(`${API_BASE}/paper-trade/remove/${symbol}`, { method: 'DELETE' });
            await fetchWatchlist();
        } catch (err) {
            console.error('Failed to remove from watchlist:', err);
        }
    };

    useEffect(() => {
        fetchWatchlist();
    }, []);

    return { watchlist, loading, addToWatchlist, removeFromWatchlist, refresh: fetchWatchlist };
}
