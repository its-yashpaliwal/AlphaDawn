"""
Paper Trading API routes — manual watchlist with real-time price tracking.
"""

import json
import os
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.intelligence.stock_data_agent import StockDataAgent
from loguru import logger

router = APIRouter()
DATA_FILE = "data/paper_trades.json"

class WatchlistItem(BaseModel):
    symbol: str
    entry_price: float
    target_price: float
    stop_loss: float
    direction: str
    catalyst_summary: str = ""

def load_watchlist() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_watchlist(data: list[dict]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@router.post("/add")
async def add_to_watchlist(item: WatchlistItem):
    watchlist = load_watchlist()
    # Check if already exists
    if any(i["symbol"].upper() == item.symbol.upper() for i in watchlist):
        return {"status": "exists", "message": f"{item.symbol} is already in watchlist"}
    
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
            
            # Calculate ROI %
            roi = 0.0
            if current_price and item["entry_price"]:
                if item["direction"].upper() == "LONG":
                    roi = ((current_price - item["entry_price"]) / item["entry_price"]) * 100
                else:
                    roi = ((item["entry_price"] - current_price) / item["entry_price"]) * 100
            
            updated_watchlist.append({
                **item,
                "current_price": current_price,
                "roi_pct": round(roi, 2),
                "status": "HIT TARGET" if current_price >= item["target_price"] and item["direction"] == "LONG" else 
                          "STOP LOSS" if current_price <= item["stop_loss"] and item["direction"] == "LONG" else "ACTIVE"
            })
        except Exception as e:
            logger.warning(f"Failed to update price for {item['symbol']}: {e}")
            updated_watchlist.append({**item, "current_price": None, "roi_pct": None, "status": "ERROR"})

    return {"watchlist": updated_watchlist}

@router.delete("/remove/{symbol}")
async def remove_from_watchlist(symbol: str):
    watchlist = load_watchlist()
    new_watchlist = [i for i in watchlist if i["symbol"].upper() != symbol.upper()]
    
    if len(new_watchlist) == len(watchlist):
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
        
    save_watchlist(new_watchlist)
    return {"status": "success", "message": f"Removed {symbol} from paper trades"}
