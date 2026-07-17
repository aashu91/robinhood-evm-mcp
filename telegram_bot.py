#!/usr/bin/env python3
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
