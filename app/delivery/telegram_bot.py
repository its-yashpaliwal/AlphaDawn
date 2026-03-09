"""
Telegram Bot — sends today's picks via Telegram.
"""

from loguru import logger

from app.config import settings


async def send_picks_to_telegram(picks: list[dict]):
    """Format and send trade picks to the configured Telegram chat."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("⚠️  Telegram not configured — skipping delivery")
        return

    try:
        from telegram import Bot

        bot = Bot(token=settings.telegram_bot_token)

        message = _format_picks_message(picks)
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode="HTML",
        )
        logger.info(f"📬  Sent {len(picks)} picks to Telegram")

    except Exception as exc:
        logger.error(f"❌  Telegram delivery failed: {exc}")


def _format_picks_message(picks: list[dict]) -> str:
    """Format picks into a readable Telegram message."""
    if not picks:
        return "📈 <b>AlphaDawn</b>\n\nNo actionable picks today. Sit tight! 🧘"

    lines = ["📈 <b>AlphaDawn — Today's Picks</b>\n"]

    for i, pick in enumerate(picks, 1):
        direction_emoji = "🟢" if pick.get("direction") == "LONG" else "🔴"
        lines.append(
            f"{direction_emoji} <b>{i}. {pick.get('symbol', '?')} "
            f"({pick.get('exchange', 'NSE')})</b>\n"
            f"   Direction: {pick.get('direction', 'LONG')}\n"
            f"   Entry: ₹{pick.get('entry_price', 0):.2f}\n"
            f"   Target: ₹{pick.get('target_price', 0):.2f}\n"
            f"   SL: ₹{pick.get('stop_loss', 0):.2f}\n"
            f"   Confidence: {pick.get('confidence', 0):.0%}\n"
            f"   Catalyst: {pick.get('catalyst_summary', 'N/A')}\n"
        )

    lines.append("\n⚠️ <i>Not financial advice. DYOR.</i>")
    return "\n".join(lines)
