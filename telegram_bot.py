
import os
import json
import asyncio
from typing import Optional

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
# ponytail: simple, self-contained polling loop, no third-party package dependencies.
try:
    from mcp_server import deploy_token, get_trust_status, get_reserves
except ImportError:
    # Fallback stubs if mcp_server is not in path during testing
    async def deploy_token(name: str, symbol: str, creator: str) -> dict:
        return {"status": "error", "message": "mcp_server not available"}
    async def get_trust_status(address: str) -> dict:
        return {"trust_score": 0, "verified": False}
    async def get_reserves() -> dict:
        return {"gold": 0, "silver": 0}
import sys
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("MINI_APP_URL", "https://robin-mcp-mini-app.vercel.app")
import urllib.request
import urllib.error
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini-App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Robinhood EVM MCP Bot!\n"
        "Use the button below or commands:\n"
        "/launch <name> <symbol> - Deploy a meme coin\n"
        "/trust <address> - Check community trust\n"
        "/reserves - View gold/silver stats",
        reply_markup=reply_markup
    )
        if os.path.exists(path):
            with open(path, "r") as f:
async def launch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /launch <token_name> <symbol>")
        return
    name, symbol = context.args[0], context.args[1]
    user_addr = str(update.effective_user.id)  # Placeholder for wallet binding
    await update.message.reply_text(f"🚀 Deploying {name} ({symbol})...")
    try:
        result = await deploy_token(name=name, symbol=symbol, creator=user_addr)
        await update.message.reply_text(f"✅ Launch Result:\n```json\n{json.dumps(result, indent=2)}\n```")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")

async def trust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /trust <contract_address>")
        return
    address = context.args[0]
    await update.message.reply_text(f"🛡️ Checking trust for {address}...")
    try:
        result = await get_trust_status(address=address)
        await update.message.reply_text(f"📊 Trust Status:\n```json\n{json.dumps(result, indent=2)}\n```")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
WEBAPP_URL = "https://robinhood-evm-mcp.vercel.app" # Replace with user's vercel deploy url

async def reserves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Fetching reserve stats...")
    try:
        result = await get_reserves()
        await update.message.reply_text(f"🏦 Reserves:\n```json\n{json.dumps(result, indent=2)}\n```")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        
    data = json.dumps(payload).encode('utf-8')
def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    req = urllib.request.Request(
        url,
        data=data,
    
    print("🤖 Robinhood MCP Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
        headers={"Content-Type": "application/json"}
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
