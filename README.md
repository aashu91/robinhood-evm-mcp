# Telegram Bot + Mini-App (Issue #6)

Launch meme-coins, deploy community trusts and track gold/silver reserves from inside Telegram, backed by `mcp_server.py`.

## Files
- `telegram_bot.py` — Telegram bot + lightweight HTTP server (Mini-App + `/api/*`).
- `telegram_mini_app.html` — the Telegram Mini-App UI.

## Setup
1. Install the dependency:
   ```bash
   pip install python-telegram-bot
   ```
2. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
3. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="<token from @BotFather>"
   export MINI_APP_URL="https://<your-public-host>:8080"   # HTTPS required in prod
   export HTTP_PORT="8080"                                  # optional
   ```
4. Run the bot from the repo root (so it can import `mcp_server.py`):
   ```bash
   python telegram_bot.py
   ```

## Usage
| Command | Action |
|---------|--------|
| `/start` | Welcome + Mini-App button |
| `/launch` | Deploy a new meme-coin token |
| `/trust` | Deploy a community trust |
| `/reserves` | Gold / silver stats |
| `/portfolio` | Your holdings |

The Mini-App calls `GET /api/{launch|trust|reserves|portfolio}` on the bot's HTTP server, which proxies to `mcp_server.py`.

## Notes
- The Mini-App button requires `MINI_APP_URL` to be a public HTTPS URL. For local testing use a tunnel such as `ngrok http 8080`.
- The bot discovers `mcp_server` functions by trying common names (`launch_token`, `deploy_trust`, `get_reserves`, …). Adjust `MCP_CANDIDATES` in `telegram_bot.py` if your server uses different names.
