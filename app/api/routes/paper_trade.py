"""
Paper Trading API routes — manual watchlist with real-time price tracking.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.intelligence.stock_data_agent import StockDataAgent
from loguru import logger

router = APIRouter()
DATA_FILE = "data/paper_trades.json"
HISTORY_FILE = "data/paper_trade_history.json"
DEFAULT_INVESTED_AMOUNT = 10000.0

class WatchlistItem(BaseModel):
    symbol: str
    entry_price: float
    target_price: float
    stop_loss: float
    direction: str
    catalyst_summary: str = ""
    buy_date: str = ""
    invested_amount: float = DEFAULT_INVESTED_AMOUNT

def load_watchlist() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        # Migration: ensure all existing trades have invested_amount
        migrated = False
        for item in data:
            if "invested_amount" not in item:
                item["invested_amount"] = DEFAULT_INVESTED_AMOUNT
                migrated = True
        if migrated:
            save_watchlist(data)
        return data
    except Exception:
        return []

def save_watchlist(data: list[dict]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(data: list[dict]):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

@router.post("/add")
async def add_to_watchlist(item: WatchlistItem):
    watchlist = load_watchlist()
    # Check if already exists
    if any(i["symbol"].upper() == item.symbol.upper() for i in watchlist):
        return {"status": "exists", "message": f"{item.symbol} is already in watchlist"}
    
    if not item.buy_date:
        item.buy_date = datetime.now(timezone.utc).isoformat()
        
    watchlist.append(item.model_dump())
    save_watchlist(watchlist)
    return {"status": "success", "message": f"Added {item.symbol} to paper trades"}

@router.get("/watchlist")
async def get_watchlist():
    watchlist = load_watchlist()
    if not watchlist:
        return {"watchlist": []}

    # Fetch real-time prices for all symbols in watchlist
    agent = StockDataAgent()
    symbols = [item["symbol"] for item in watchlist]
    
    # We'll batch fetch if StockDataAgent supported it, but for a simple paper trader,
    # we'll just loop. The agent already has some internal batching logic if we use orchestrator style,
    # but here we'll just call the technicals fetcher.
    
    updated_watchlist = []
    for item in watchlist:
        try:
            tech = await agent._fetch_technicals(item["symbol"])
            current_price = tech.get("current_price", 0)
            invested = item.get("invested_amount", DEFAULT_INVESTED_AMOUNT)
            
            # Calculate ROI %
            roi = 0.0
            if current_price and item["entry_price"]:
                if item["direction"].upper() == "LONG":
                    roi = ((current_price - item["entry_price"]) / item["entry_price"]) * 100
                else:
                    roi = ((item["entry_price"] - current_price) / item["entry_price"]) * 100
            
            # Calculate P&L based on invested amount
            pnl = (roi / 100) * invested
            
            updated_watchlist.append({
                **item,
                "current_price": current_price,
                "roi_pct": round(roi, 2),
                "pnl": round(pnl, 2),
                "invested_amount": invested,
                "status": "HIT TARGET" if current_price >= item["target_price"] and item["direction"] == "LONG" else 
                          "STOP LOSS" if current_price <= item["stop_loss"] and item["direction"] == "LONG" else "ACTIVE"
            })
        except Exception as e:
            logger.warning(f"Failed to update price for {item['symbol']}: {e}")
            updated_watchlist.append({**item, "current_price": None, "roi_pct": None, "pnl": None, "status": "ERROR"})

    return {"watchlist": updated_watchlist}

@router.delete("/remove/{symbol}")
async def remove_from_watchlist(symbol: str):
    watchlist = load_watchlist()
    trade = next((i for i in watchlist if i["symbol"].upper() == symbol.upper()), None)
    
    if not trade:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
    
    # Fetch the current price to calculate final P&L
    agent = StockDataAgent()
    try:
        tech = await agent._fetch_technicals(trade["symbol"])
        exit_price = tech.get("current_price", 0)
    except Exception as e:
        logger.warning(f"Failed to fetch exit price for {symbol}: {e}")
        exit_price = 0
    
    invested = trade.get("invested_amount", DEFAULT_INVESTED_AMOUNT)
    
    # Calculate final ROI and P&L
    roi = 0.0
    if exit_price and trade["entry_price"]:
        if trade["direction"].upper() == "LONG":
            roi = ((exit_price - trade["entry_price"]) / trade["entry_price"]) * 100
        else:
            roi = ((trade["entry_price"] - exit_price) / trade["entry_price"]) * 100
    
    pnl = (roi / 100) * invested
    
    # Build history entry
    history_entry = {
        **trade,
        "invested_amount": invested,
        "exit_price": exit_price,
        "exit_date": datetime.now(timezone.utc).isoformat(),
        "roi_pct": round(roi, 2),
        "pnl": round(pnl, 2),
        "result": "PROFIT" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN",
    }
    
    # Save to history
    history = load_history()
    history.insert(0, history_entry)  # newest first
    save_history(history)
    
    # Remove from watchlist
    new_watchlist = [i for i in watchlist if i["symbol"].upper() != symbol.upper()]
    save_watchlist(new_watchlist)
    
    return {
        "status": "success",
        "message": f"Closed {symbol} — {'Profit' if pnl > 0 else 'Loss'} of ₹{abs(round(pnl, 2))}",
        "history_entry": history_entry
    }

@router.get("/history")
async def get_trade_history():
    history = load_history()
    
    # Calculate summary stats
    total_invested = sum(h.get("invested_amount", DEFAULT_INVESTED_AMOUNT) for h in history)
    total_pnl = sum(h.get("pnl", 0) for h in history)
    winning_trades = sum(1 for h in history if h.get("pnl", 0) > 0)
    losing_trades = sum(1 for h in history if h.get("pnl", 0) < 0)
    
    return {
        "history": history,
        "summary": {
            "total_trades": len(history),
            "total_invested": round(total_invested, 2),
            "total_pnl": round(total_pnl, 2),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round((winning_trades / len(history)) * 100, 2) if history else 0,
        }
    }
