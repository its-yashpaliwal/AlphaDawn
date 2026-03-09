"""
Stock Data Agent — fetches technical data for shortlisted catalyst stocks.
"""

from typing import Any

import httpx
from loguru import logger

from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResult


class StockDataAgent(BaseAgent):
    """Fetches technical indicators for symbols identified as catalysts."""

    name = "StockDataAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        catalysts: list[dict] = kwargs.get("catalysts", [])

        # Extract unique symbols
        symbols: set[str] = set()
        for item in catalysts:
            for sym in (item.get("related_symbols", "") or "").split(","):
                sym = sym.strip().upper()
                if sym:
                    symbols.add(sym)

        if not symbols:
            logger.info("  ⚠️  No symbols to fetch technicals for")
            return AgentResult(agent_name=self.name, data={"technicals": {}})

        logger.info(f"  📈  Fetching technicals for {len(symbols)} symbols: {symbols}")

        technicals: dict[str, dict] = {}
        for symbol in symbols:
            try:
                data = await self._fetch_technicals(symbol)
                technicals[symbol] = data
            except Exception as exc:
                logger.warning(f"  ⚠️  {symbol}: {exc}")
                technicals[symbol] = {"error": str(exc)}

        return AgentResult(agent_name=self.name, data={"technicals": technicals})

    async def _fetch_technicals(self, symbol: str) -> dict:
        """Fetch key technical data from Yahoo Finance for an NSE-listed stock."""
        # Map common index names to Yahoo Finance tickers
        symbol_map = {
            "NIFTY": "^NSEI",
            "SENSEX": "^BSESN",
            "NIFTY50": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
        }
        ticker = symbol_map.get(symbol.upper(), f"{symbol}.NS")

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            # Quote data
            quote_resp = await client.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                params={"interval": "1d", "range": "1y"},
            )
            quote_resp.raise_for_status()
            result = quote_resp.json()["chart"]["result"][0]
            meta = result["meta"]
            closes = result["indicators"]["quote"][0].get("close", [])

        # Compute basic technicals from close prices
        closes_clean = [c for c in closes if c is not None]

        current_price = meta.get("regularMarketPrice", 0)
        prev_close = meta.get("chartPreviousClose", 0)
        high_52w = max(closes_clean) if closes_clean else 0
        low_52w = min(closes_clean) if closes_clean else 0

        dma_50 = self._sma(closes_clean, 50)
        dma_200 = self._sma(closes_clean, 200)
        rsi = self._rsi(closes_clean, 14)

        # Simple support/resistance from recent pivots
        supports, resistances = self._support_resistance(closes_clean, current_price)

        avg_volume_raw = result["indicators"]["quote"][0].get("volume", [])
        avg_vol_clean = [v for v in avg_volume_raw[-20:] if v is not None]
        avg_volume = int(sum(avg_vol_clean) / len(avg_vol_clean)) if avg_vol_clean else 0

        return {
            "symbol": symbol,
            "current_price": current_price,
            "prev_close": prev_close,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "dma_50": dma_50,
            "dma_200": dma_200,
            "rsi": rsi,
            "avg_volume": avg_volume,
            "supports": supports,
            "resistances": resistances,
        }

    @staticmethod
    def _sma(closes: list[float], period: int) -> float:
        if len(closes) < period:
            return 0.0
        return round(sum(closes[-period:]) / period, 2)

    @staticmethod
    def _rsi(closes: list[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        recent = deltas[-period:]
        gains = [d for d in recent if d > 0]
        losses = [abs(d) for d in recent if d < 0]
        avg_gain = sum(gains) / period if gains else 0.001
        avg_loss = sum(losses) / period if losses else 0.001
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)

    @staticmethod
    def _support_resistance(
        closes: list[float], current: float
    ) -> tuple[list[float], list[float]]:
        if not closes:
            return [], []
        # Simple: pick round-number levels near current price
        step = max(round(current * 0.02, -1), 10)  # ~2% band
        supports = [round(current - step * i, 2) for i in range(1, 4)]
        resistances = [round(current + step * i, 2) for i in range(1, 4)]
        return supports, resistances
