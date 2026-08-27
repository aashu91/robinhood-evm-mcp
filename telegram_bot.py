import os
import json
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from mcp_server import launch_token, deploy_trust, get_reserves

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Mini-App URL (deployed separately, e.g., via GitHub Pages or Vercel)
MINI_APP_URL = os.environ.get("TELEGRAM_MINI_APP_URL", "https://robin-mcp-miniapp.vercel.app")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with Mini-App button."""
    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini-App", web_app=WebAppInfo(url=MINI_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Robin MCP Bot!\n\n"
        "Use /launch, /trust, or /reserves commands,\n"
        "or open the Mini-App for full UI.",
        reply_markup=reply_markup
    )

async def launch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Launch a new meme token via MCP server."""
    try:
        # Expecting args: name symbol initial_supply
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage: /launch <name> <symbol> <initial_supply>\n"
                "Example: /launch DogeCoin DOGE 1000000"
            )
            return
        
        name, symbol, supply = context.args[0], context.args[1], int(context.args[2])
        result = launch_token(name=name, symbol=symbol, initial_supply=supply)
        
        if result.get("success"):
            await update.message.reply_text(
                f"✅ Token launched!\n"
                f"Name: {result['name']}\n"
                f"Symbol: {result['symbol']}\n"
                f"Address: `{result['address']}`\n"
                f"Tx: {result['tx_hash']}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Launch failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Launch error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def trust_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deploy a community trust."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /trust <beneficiary_address> <vault_amount>\n"
                "Example: /trust 0x123...abc 5000"
            )
            return
        
        beneficiary = context.args[0]
        amount = int(context.args[1])
        result = deploy_trust(beneficiary=beneficiary, vault_amount=amount)
        
        if result.get("success"):
            await update.message.reply_text(
                f"✅ Trust deployed!\n"
                f"Trust Address: `{result['trust_address']}`\n"
                f"Beneficiary: `{beneficiary}`\n"
                f"Vault: {amount} tokens",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Trust deployment failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Trust error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def reserves_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View gold/silver reserve stats."""
    try:
        stats = get_reserves()
        text = (
            "🏦 Reserve Stats:\n"
            f"Gold: {stats.get('gold', 0):,.2f} oz\n"
            f"Silver: {stats.get('silver', 0):,.2f} oz\n"
            f"Last Updated: {stats.get('timestamp', 'N/A')}"
        )
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Reserves error: {e}")
        await update.message.reply_text(f"⚠️ Could not fetch reserves: {str(e)}")

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("launch", launch_command))
    app.add_handler(CommandHandler("trust", trust_command))
    app.add_handler(CommandHandler("reserves", reserves_command))
    
    logger.info("Bot started. Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
# telegram_bot.py
# Zero-dependency Telegram Bot backend using stdlib urllib.request
# ponytail: simple, self-contained polling loop, no third-party package dependencies.

import os
import sys
import json
import urllib.request
import urllib.error

# Load environment
def load_all_envs():
    for path in [os.path.expanduser("~/.env"), ".env"]:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_all_envs()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBAPP_URL = "https://robinhood-evm-mcp.vercel.app" # Replace with user's vercel deploy url

def send_api_request(method, payload):
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return None
        
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error calling {method}: {e.code} - {e.read().decode('utf-8')}")
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
