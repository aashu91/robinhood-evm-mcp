@@ -0,0 +1,58 @@
+# 🤖 Robin MCP Telegram Bot & Mini-App
+
+A lightweight Telegram Bot + Mini-App that talks directly to `mcp_server.py`
+so users can **launch meme tokens**, **create community trusts**, and
+**view gold/silver reserves** without leaving Telegram.
+
+## Features
+
+- `/launch <name> <symbol> <supply>` - deploy a new ERC-20 meme coin
+- `/trust <beneficiary>` - spin up a community trust
+- `/reserves` - show current reserve stats
+- `/app` - open the Mini-App UI (teal finance theme)
+
+## Quick Start
+
+```bash
+# 1. Install deps (only python-telegram-bot added)
+pip install python-telegram-bot>=21.0
+
+# 2. Export your bot token
+export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
+
+# 3. (Optional) Override Mini-App URL
+export MINI_APP_URL="https://your-domain.com/index.html"
+
+# 4. Regenerate the Mini-App front-end
+python generate_index_html.py
+
+# 5. Run the bot
+python telegram_bot.py
+```
+
+## Architecture
+
+```
+Telegram User ──► telegram_bot.py ──► mcp_server.py ──► EVM RPC
+       ▲                                       │
+       └──── Mini-App (index.html) ◄───────────┘
+```
+
+The Mini-App makes HTTP requests to `/api/*`; wire those routes in your
+favourite ASGI/WSGI wrapper around `mcp_server` (Flask, FastAPI, etc.).
+
+## Testing
+
+```bash
+pytest test_trust.py        # existing trust tests
+python -m py_compile telegram_bot.py generate_index_html.py
+```
+
+## Bounty Claim
+
+- ✅ Bot + Mini-App implemented
+- ✅ README with setup steps
+- Wallet: `0xYOUR_WALLET_HERE`
+
+Submit a PR referencing **Issue #6**. Once merged, the
+**50,000 $ROBIN_MCP** bounty is paid automatically.