"""
Tests for trade setup heuristic (no-LLM fallback).
"""

import pytest

from app.agents.intelligence.trade_setup_agent import TradeSetupAgent


def test_heuristic_setup_long():
    """When price > 50-DMA, heuristic should produce a LONG setup."""
    catalyst = {"headline": "RELIANCE beats Q3 estimates", "related_symbols": "RELIANCE"}
    technicals = {
        "symbol": "RELIANCE",
        "current_price": 2500.0,
        "prev_close": 2480.0,
        "dma_50": 2400.0,
        "dma_200": 2300.0,
        "rsi": 55.0,
    }

    result = TradeSetupAgent._heuristic_setup(catalyst, technicals)

    assert result["symbol"] == "RELIANCE"
    assert result["direction"] == "LONG"
    assert result["entry_price"] == 2500.0
    assert result["target_price"] > result["entry_price"]
    assert result["stop_loss"] < result["entry_price"]


def test_heuristic_setup_short():
    """When price < 50-DMA, heuristic should produce a SHORT setup."""
    catalyst = {"headline": "XYZ misses earnings"}
    technicals = {
        "symbol": "XYZ",
        "current_price": 100.0,
        "prev_close": 105.0,
        "dma_50": 110.0,
        "dma_200": 120.0,
        "rsi": 35.0,
    }

    result = TradeSetupAgent._heuristic_setup(catalyst, technicals)

    assert result["direction"] == "SHORT"
    assert result["target_price"] < result["entry_price"]
    assert result["stop_loss"] > result["entry_price"]


def test_heuristic_setup_zero_price():
    """Zero price should return empty dict."""
    result = TradeSetupAgent._heuristic_setup(
        {"headline": "test"},
        {"symbol": "X", "current_price": 0, "dma_50": 0},
    )
    assert result == {}
