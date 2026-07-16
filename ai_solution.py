"""
Telegram Bot + Mini-App for Robinhood EVM MCP
==============================================

A Telegram bot that connects with the local mcp_server.py to let users:
  - /launch   — deploy a meme coin token
  - /trust    — deploy a community trust
  - /reserves — view gold / silver reserve stats
  - /portfolio — check their holdings
  - /webapp   — open the Telegram Mini-App UI

Setup:
  1. pip install python-telegram-bot httpx
  2. Set env vars: TELEGRAM_BOT_TOKEN, MCP_SERVER_URL, WEBAPP_URL
  3. python ai_solution.py

The Mini-App HTML page lives at WEBAPP_URL (serve telegram_miniapp.html
from any static host — GitHub Pages, Vercel, or your own domain).
"""

from __future__ import annotations

import logging
import os

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com/telegram-miniapp.html")


# ---------------------------------------------------------------------------
# MCP server helpers
# ---------------------------------------------------------------------------

async def _mcp(method: str, path: str, **kwargs) -> dict:
    """Call the local MCP server and return the JSON response."""
    url = f"{MCP_SERVER_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            fn = getattr(client, method)
            r = await fn(url, **kwargs)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("MCP %s %s → %s", method.upper(), path, exc.response.status_code)
        return {"error": f"Server error {exc.response.status_code}"}
    except Exception as exc:
        logger.error("MCP call failed: %s", exc)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Bot command handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message with Mini-App launch button."""
    keyboard = [[
        InlineKeyboardButton("🚀 Open Mini-App", web_app=WebAppInfo(url=WEBAPP_URL))
    ]]
    text = (
        "🏦 *Welcome to Robinhood Chain MCP Bot!*\n\n"
        "Launch meme coins, track community trusts, and manage your portfolio "
        "directly from Telegram.\n\n"
        "*Commands:*\n"
        "/launch `<name> <symbol> <supply>` — deploy a token\n"
        "/trust — deploy a community trust\n"
        "/reserves — view gold & silver stats\n"
        "/portfolio — check your holdings\n"
        "/webapp — open the full Mini-App\n\n"
        "Tap the button below to open the Mini-App 👇"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a button that opens the Telegram Mini-App."""
    keyboard = [[
        InlineKeyboardButton("🚀 Open Mini-App", web_app=WebAppInfo(url=WEBAPP_URL))
    ]]
    await update.message.reply_text(
        "Click below to open the full Mini-App interface:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_launch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deploy a new meme coin: /launch <name> <symbol> <totalSupply>"""
    args = context.args or []
    if len(args) < 3:
        await update.message.reply_text(
            "❌ *Usage:* `/launch <name> <symbol> <totalSupply>`\n\n"
            "Example: `/launch DogeCoin DOGE 1000000000`",
            parse_mode="Markdown",
        )
        return

    name, symbol = args[0], args[1]
    try:
        total_supply = int(args[2])
    except ValueError:
        await update.message.reply_text("❌ totalSupply must be a whole number.")
        return

    await update.message.reply_text(f"⏳ Deploying *{name}* ({symbol})…", parse_mode="Markdown")

    result = await _mcp("post", "/launch_token", json={
        "name": name,
        "symbol": symbol,
        "total_supply": total_supply,
    })

    if "error" in result:
        await update.message.reply_text(f"❌ Launch failed: {result['error']}")
        return

    contract = result.get("contract_address", "N/A")
    tx = result.get("transaction_hash", "N/A")
    await update.message.reply_text(
        f"✅ *{name} ({symbol}) deployed!*\n\n"
        f"📄 Contract: `{contract}`\n"
        f"🔗 Tx: `{tx}`\n"
        f"💰 Supply: {total_supply:,}",
        parse_mode="Markdown",
    )


async def cmd_trust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deploy a community trust."""
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "❌ *Usage:* `/trust <name>`\n\nExample: `/trust CommunityFund`",
            parse_mode="Markdown",
        )
        return

    trust_name = " ".join(args)
    await update.message.reply_text(f"⏳ Deploying trust *{trust_name}*…", parse_mode="Markdown")

    result = await _mcp("post", "/deploy_trust", json={"name": trust_name})

    if "error" in result:
        await update.message.reply_text(f"❌ Trust deployment failed: {result['error']}")
        return

    contract = result.get("contract_address", "N/A")
    await update.message.reply_text(
        f"✅ *Community Trust deployed!*\n\n"
        f"🏦 Name: {trust_name}\n"
        f"📄 Contract: `{contract}`",
        parse_mode="Markdown",
    )


async def cmd_reserves(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View current gold and silver reserve stats."""
    await update.message.reply_text("⏳ Fetching reserve data…")

    result = await _mcp("get", "/reserves")

    if "error" in result:
        await update.message.reply_text(f"❌ Could not fetch reserves: {result['error']}")
        return

    gold = result.get("gold", {})
    silver = result.get("silver", {})
    await update.message.reply_text(
        "📊 *Reserve Status*\n\n"
        f"🟡 Gold\n"
        f"   Balance: {gold.get('balance', 'N/A')} oz\n"
        f"   Price:   ${gold.get('price_usd', 'N/A')}/oz\n"
        f"   Total:   ${gold.get('total_usd', 'N/A')}\n\n"
        f"⬜ Silver\n"
        f"   Balance: {silver.get('balance', 'N/A')} oz\n"
        f"   Price:   ${silver.get('price_usd', 'N/A')}/oz\n"
        f"   Total:   ${silver.get('total_usd', 'N/A')}",
        parse_mode="Markdown",
    )


async def cmd_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the caller's token portfolio."""
    # Use the Telegram user ID as the wallet identifier (adjust if the MCP
    # server identifies users differently)
    user_id = str(update.effective_user.id)
    await update.message.reply_text("⏳ Loading your portfolio…")

    result = await _mcp("get", f"/portfolio/{user_id}")

    if "error" in result:
        await update.message.reply_text(f"❌ Could not load portfolio: {result['error']}")
        return

    tokens: list[dict] = result.get("tokens", [])
    if not tokens:
        await update.message.reply_text("📊 Your portfolio is empty.")
        return

    lines = ["📊 *Your Portfolio*\n"]
    for token in tokens[:10]:  # cap at 10 to avoid message length limits
        lines.append(
            f"• *{token.get('name', '?')}* ({token.get('symbol', '?')}): "
            f"{token.get('balance', 0):,}"
        )

    total_usd = result.get("total_usd")
    if total_usd is not None:
        lines.append(f"\n💵 Total value: *${total_usd:,.2f}*")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive data posted back from the Mini-App."""
    data = update.effective_message.web_app_data.data if update.effective_message.web_app_data else ""
    logger.info("Mini-App data received: %s", data[:200])
    await update.message.reply_text(f"✅ Received from Mini-App:\n`{data[:500]}`", parse_mode="Markdown")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set. Export it before running.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("webapp", cmd_webapp))
    app.add_handler(CommandHandler("launch", cmd_launch))
    app.add_handler(CommandHandler("trust", cmd_trust))
    app.add_handler(CommandHandler("reserves", cmd_reserves))
    app.add_handler(CommandHandler("portfolio", cmd_portfolio))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    logger.info("Bot starting — polling for updates…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
