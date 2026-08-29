
"""Telegram Bot & Mini-App for Robinhood EVM MCP.

Commands:
    /launch <name> <symbol> <supply> - deploy a meme token via mcp_server
    /trust <beneficiary>            - create a community trust
    /reserves                       - show gold/silver reserve stats
    /app                            - open the Mini-App UI
"""

import asyncio
import json
import logging
import os
from pathlib import Path

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# ponytail: simple, self-contained polling loop, no third-party package dependencies.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://robin-mcp.example.com/app")
import urllib.request
# ---------------------------------------------------------------------------
# Helpers to call into mcp_server (imported lazily so tests can stub it)
# ---------------------------------------------------------------------------

def _get_mcp():
    """Return the mcp_server module; imported here to allow monkey-patching."""
    import mcp_server  # local import keeps test isolation simple
    return mcp_server
                    line = line.strip()

# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def cmd_launch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deploy a new meme token."""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: /launch <name> <symbol> <initial_supply>\n"
            "Example: /launch DogeCoin DOGE 1000000"
        )
        return
    name, symbol = args[0], args[1]
    try:
        supply = float(args[2])
    except ValueError:
        await update.message.reply_text("Supply must be a number.")
        return

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _get_mcp().launch_token, name, symbol, supply)
    await update.message.reply_text(f"🚀 Token launched:\n<pre>{json.dumps(result, indent=2)}</pre>", parse_mode="HTML")
WEBAPP_URL = "https://robinhood-evm-mcp.vercel.app" # Replace with user's vercel deploy url

async def cmd_trust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a community trust for a beneficiary address."""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /trust <beneficiary_address>")
        return
    beneficiary = args[0]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _get_mcp().create_trust, beneficiary)
    await update.message.reply_text(f"🤝 Trust created:\n<pre>{json.dumps(result, indent=2)}</pre>", parse_mode="HTML")
        return None

async def cmd_reserves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display current gold/silver reserve statistics."""
    loop = asyncio.get_running_loop()
    stats = await loop.run_in_executor(None, _get_mcp().get_reserves)
    lines = [f"• {k}: {v}" for k, v in stats.items()]
    await update.message.reply_text("📊 Reserves:\n" + "\n".join(lines))
        url,

async def cmd_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send an inline button that opens the Mini-App."""
    button = InlineKeyboardButton(
        "📱 Open Mini-App",
        web_app=WebAppInfo(url=MINI_APP_URL),
    )
    markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(
        "Manage launches, trusts & portfolio inside Telegram:",
        reply_markup=markup,
    )


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("launch", cmd_launch))
    application.add_handler(CommandHandler("trust", cmd_trust))
    application.add_handler(CommandHandler("reserves", cmd_reserves))
    application.add_handler(CommandHandler("app", cmd_app))

    logger.info("Starting Telegram bot…")
    application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Generic error calling {method}: {str(e)}")
    return None

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return send_api_request("sendMessage", payload)

def handle_start(chat_id):
    welcome_text = (
        "🚀 Welcome to Robinhood L2 Web3 Launchpad Bot!\n\n"
        "Deploy tokens, trade virtual bonding curves, and manage community multi-sig "
        "trust reserves directly from Telegram."
    )
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📱 Open Launchpad Mini-App", "web_app": {"url": WEBAPP_URL}}],
            [{"text": "📊 View Reserves", "callback_data": "view_reserves"}]
        ]
    }
    send_message(chat_id, welcome_text, reply_markup)

def handle_reserves(chat_id):
    res_text = (
        "🏦 Community Trust Reserves:\n"
        "• PAxOS Gold (cGOLD): 120.00 cGOLD\n"
        "• cSILVER: 350.00 cSILVER\n"
        "• Total Pooled Balance: 1.45 ETH\n\n"
        "Manage these assets inside the Trust Bank tab in the Mini-App."
    )
    send_message(chat_id, res_text)

def handle_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()
        
        if text.startswith("/start"):
            handle_start(chat_id)
        elif text.startswith("/reserves"):
            handle_reserves(chat_id)
        else:
            send_message(chat_id, "Command not recognized. Type /start to open the Mini-App.")
            
    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data")
        
        if data == "view_reserves":
            handle_reserves(chat_id)
            
        # Answer callback query to stop loading indicator
        send_api_request("answerCallbackQuery", {"callback_query_id": cb["id"]})

def main():
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is not set in environment (.env). Exiting.")
        sys.exit(1)
        
    print("🤖 Starting Telegram Launchpad Bot (polling updates)...")
    offset = 0
    while True:
        try:
            payload = {"timeout": 30, "offset": offset}
            res = send_api_request("getUpdates", payload)
            if res and res.get("ok"):
                for update in res.get("result", []):
                    handle_update(update)
                    offset = update["update_id"] + 1
        except KeyboardInterrupt:
            print("\nShutting down Telegram Bot daemon.")
            break
        except Exception as err:
            print(f"Error in polling loop: {str(err)}")
            # Avoid tight error loop
            import time
            time.sleep(5)

if __name__ == "__main__":
    main()
