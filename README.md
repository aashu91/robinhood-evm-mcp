# MCP Telegram Mini-App/Bot

## Objective
Create a lightweight Telegram Mini-App / Bot that connects with our Python MCP server to let users deploy tokens, check community trusts, and view their portfolios from inside Telegram.

## Requirements
1. **Telegram Bot**:
   - Implement a Telegram Bot using `python-telegram-bot`.
   - Support commands like `/launch` (launches token), `/trust` (deploys trust), and `/reserves` (view gold/silver stats).
2. **Mini-App UI**:
   - Build a clean Telegram Webapp / Mini-App interface.
   - Use our existing `index.html` structure or a styled lightweight design.
3. **Integration**:
   - Connect the Telegram backend directly with our local `mcp_server.py` APIs.

## Setup Instructions

### Prerequisites
- Python 3.x
- `python-telegram-bot` library
- Local MCP server running on `http://localhost:5000`

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/mcp-telegram-app.git
   cd mcp-telegram-app
   ```
2. Install the required dependencies:
   ```sh
   pip install python-telegram-bot
   ```
3. Set up the Telegram Bot:
   - Create a new Telegram Bot and get the token.
   - Replace `YOUR_TELEGRAM_BOT_TOKEN` in `telegram_bot.py` with your actual token.
4. Run the Telegram Bot:
   ```sh
   python telegram_bot.py
   ```

### Usage
- Open Telegram and start a chat with your bot.
- Use the commands `/launch`, `/trust`, and `/reserves` to interact with the MCP server.
- Access the Mini-App by clicking on the "Open Web App" button in the chat.

## Bounty Claim
- Wallet: 0x...

## License
This project is licensed under the MIT License.
