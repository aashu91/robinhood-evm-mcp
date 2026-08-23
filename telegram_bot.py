#!/usr/bin/env python3
"""Robinhood EVM MCP - Telegram Bot + Mini-App (Issue #6).

Commands
--------
/start      Welcome message + Mini-App launcher button
/launch     Deploy a new meme-coin token
/trust      Deploy a community trust
/reserves   Gold / silver reserve stats
/portfolio  Your holdings

The bot also runs a tiny stdlib HTTP server that serves
``telegram_mini_app.html`` at ``/`` and proxies ``/api/*`` calls to
``mcp_server.py`` so the Mini-App can talk to the MCP backend with no
extra web framework.

Setup
-----
    pip install python-telegram-bot
    export TELEGRAM_BOT_TOKEN="<token from @BotFather>"
    export MINI_APP_URL="https://<your-host>:8080"   # HTTPS in production
    python telegram_bot.py
"""

import json
import logging
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# --------------------------------------------------------------- MCP --------
try:
    import mcp_server  # type: ignore
    _MCP_OK = True
except Exception:
    mcp_server = None
    _MCP_OK = False

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("robin-tg")

HERE = os.path.dirname(os.path.abspath(__file__))
MINI_APP_HTML = os.path.join(HERE, "telegram_mini_app.html")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
MINI_APP_URL = os.getenv("MINI_APP_URL", f"https://localhost:{HTTP_PORT}")

# Each action maps to candidate mcp_server function names tried in order.
MCP_CANDIDATES = {
    "launch":    ["launch_token", "deploy_token", "launch", "deploy_launchpad"],
    "trust":     ["deploy_trust", "create_trust", "trust"],
    "reserves":  ["get_reserves", "reserves", "gold_silver_stats", "get_stats"],
    "portfolio": ["get_portfolio", "portfolio", "get_balances", "balances"],
}

ACTION_LABEL = {
    "launch": "\U0001F680 Launch",
    "trust": "\U0001F6E1\uFE0F Trust",
    "reserves": "\U0001F4B0 Reserves",
    "portfolio": "\U0001F4CA Portfolio",
}


def _to_text(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, default=str)
    return str(value)


def call_mcp(action, *args):
    """Run an MCP action. Returns (ok, payload_text)."""
    if not _MCP_OK:
        return False, "mcp_server.py could not be imported. Run the bot from the repo root."
    for name in MCP_CANDIDATES.get(action, []):
        fn = getattr(mcp_server, name, None)
        if not callable(fn):
            continue
        try:
            return True, _to_text(fn(*args))
        except TypeError:
            try:
                return True, _to_text(fn())
            except Exception as exc:
                return False, f"{name}() failed: {exc}"
        except Exception as exc:
            return False, f"{name}() failed: {exc}"
    return False, f"No mcp_server function found for '{action}'."


# ---------------------------------------------------------- Bot handlers -----
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("\U0001F680 Open Mini-App", web_app=WebAppInfo(url=MINI_APP_URL))]]
    )
    await update.message.reply_text(
        "\U0001F3F9 Robinhood EVM MCP\n\n"
        "Launch meme-coins, deploy community trusts and track your reserves — "
        "all inside Telegram.\n\n"
        "/launch — deploy a token\n"
        "/trust — deploy a community trust\n"
        "/reserves — gold / silver stats\n"
        "/portfolio — your holdings",
        reply_markup=kb,
    )


async def _run_action(action, update, context):
    args = context.args or []
    ok, payload = call_mcp(action, *args)
    prefix = ACTION_LABEL[action]
    await update.message.reply_text(f"{prefix}\n{payload}")


async def cmd_launch(update, context):
    await _run_action("launch", update, context)


async def cmd_trust(update, context):
    await _run_action("trust", update, context)


async def cmd_reserves(update, context):
    await _run_action("reserves", update, context)


async def cmd_portfolio(update, context):
    await _run_action("portfolio", update, context)


# ------------------------------------------------------- Mini-App server -----
class MiniAppHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_html(self):
        try:
            with open(MINI_APP_HTML, "rb") as fh:
                body = fh.read()
        except FileNotFoundError:
            body = b"<h1>telegram_mini_app.html not found</h1>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _action_from_path(self):
        action = self.path.split("/api/", 1)[1].strip("/").split("?", 1)[0]
        return action if action in MCP_CANDIDATES else None

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._serve_html()
        if self.path.startswith("/api/"):
            action = self._action_from_path()
            if action:
                ok, payload = call_mcp(action)
                return self._send_json(200 if ok else 500, {"ok": ok, "result": payload})
            return self._send_json(404, {"ok": False, "result": "unknown action"})
        return self._send_json(404, {"ok": False, "result": "not found"})

    def do_POST(self):
        if not self.path.startswith("/api/"):
            return self._send_json(404, {"ok": False, "result": "not found"})
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except (json.JSONDecodeError, ValueError):
            data = {}
        action = self._action_from_path()
        if not action:
            return self._send_json(404, {"ok": False, "result": "unknown action"})
        args = data.get("args", []) if isinstance(data, dict) else []
        ok, payload = call_mcp(action, *args)
        return self._send_json(200 if ok else 500, {"ok": ok, "result": payload})

    def log_message(self, fmt, *args):
        log.info("http: " + (fmt % args))


def start_http_server():
    server = ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), MiniAppHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log.info("Mini-App + API listening on http://0.0.0.0:%s", HTTP_PORT)


# ---------------------------------------------------------------- main -------
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        log.error("Set TELEGRAM_BOT_TOKEN (get one from @BotFather).")
        sys.exit(1)

    start_http_server()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("launch", cmd_launch))
    app.add_handler(CommandHandler("trust", cmd_trust))
    app.add_handler(CommandHandler("reserves", cmd_reserves))
    app.add_handler(CommandHandler("portfolio", cmd_portfolio))

    log.info("Telegram bot polling…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
