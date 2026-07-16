# create_issues.py
import subprocess
import json

issues = [
    {
        "title": "🏆 [Bounty: 0.05 ETH] Integrate Pyth / Chainlink Oracles for Real-Time Gold & Silver Valuation",
        "body": """### Objective
We need to upgrade our `CommunityTrust` contract to support real-time price feeds for precious metal assets (like Gold and Silver) using Pyth Network or Chainlink Oracles. Currently, our gold/silver reserves use mock valuations.

### Requirements
1. **Smart Contract Modification**:
   - Update [CommunityTrust.sol](contracts/CommunityTrust.sol) or create a pricing oracle adapter to read feeds for `XAU/USD` (Gold) and `XAG/USD` (Silver).
   - Integrate Pyth Network's `IPyth` interface or Chainlink's `AggregatorV3Interface`.
2. **Backend Web3 Helper**:
   - Update `web3_helper.py` to query these oracle prices and calculate the current USD valuation of the trust reserves dynamically.
3. **Frontend Integration**:
   - Display the real-time oracle price updates on the frontend dashboard under the "🏦 Trust Bank" reserves tracker.

### How to Claim the Bounty
1. Fork this repository.
2. Implement the oracle integration.
3. Add a test suite verifying oracle price reading.
4. Submit a Pull Request. Once merged, the 0.05 ETH bounty will be sent directly to your payout wallet.

---
*Note: This issue is **ai-agent-friendly**. AI coding assistants (like Antigravity, Claude Code, Sweep, etc.) are welcome to attempt and submit PRs.*
""",
        "labels": ["bounty", "ai-agent-friendly"]
    },
    {
        "title": "🏆 [Bounty: 0.03 ETH] Implement Native Token ($ROBIN_MCP) Staking & Yield Distribution Contract",
        "body": """### Objective
Build a Solidity contract that allows users to stake the native launchpad token `$ROBIN_MCP` (`0xCFD635f82B75ab6c1a6725a54e9146FEe2c5A421`) and receive proportional rewards/yield from platform fees.

### Requirements
1. **Solidity Contract**:
   - Implement `StakingYield.sol` supporting `stake(uint256 amount)`, `unstake(uint256 amount)`, and `claimRewards()`.
   - Distribute rewards based on user's share of the total staked pool over time.
2. **Web3 Python Helper & CLI Tools**:
   - Extend `web3_helper.py` and `mcp_server.py` with methods to interact with the staking contract (`stake_tokens`, `unstake_tokens`, `claim_rewards`, `get_staking_info`).
3. **Frontend Workspace Integration**:
   - Update the web launchpad dashboard to show a new Staking interface with APY calculation, total staked, and interactive stake/unstake forms.

### How to Claim the Bounty
1. Implement the staking contract and compile it.
2. Write unit tests for staking, reward distribution, and emergency unstake.
3. Submit a Pull Request. The 0.03 ETH bounty is paid out instantly upon merge.

---
*Note: This issue is **ai-agent-friendly**. AI coding assistants are welcome to attempt and submit PRs.*
""",
        "labels": ["bounty", "ai-agent-friendly"]
    },
    {
        "title": "🏆 [Bounty: 0.04 ETH] Create a Telegram Mini-App for Launching Meme Coins & Tracking Trusts",
        "body": """### Objective
Create a lightweight Telegram Mini-App / Bot that connects with our Python MCP server to let users deploy tokens, check community trusts, and view their portfolios from inside Telegram.

### Requirements
1. **Telegram Bot**:
   - Implement a Telegram Bot using `python-telegram-bot` or similar.
   - Support commands like `/launch` (launches token), `/trust` (deploys trust), and `/reserves` (view gold/silver stats).
2. **Mini-App UI**:
   - Build a clean Telegram Webapp / Mini-App interface.
   - Use our existing `index.html` structure or a styled lightweight design.
3. **Integration**:
   - Connect the Telegram backend directly with our local `mcp_server.py` APIs.

### How to Claim the Bounty
1. Build the bot and Webapp interface.
2. Provide simple setup instructions in a README.
3. Submit a Pull Request. The 0.04 ETH bounty is paid out upon successful merge.

---
*Note: This issue is **ai-agent-friendly**. AI coding assistants are welcome to attempt and submit PRs.*
""",
        "labels": ["bounty", "ai-agent-friendly"]
    }
]

def create_issue(title, body, labels):
    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--label", ",".join(labels)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ Created issue: {title}")
        print(f"   URL: {res.stdout.strip()}")
    else:
        print(f"❌ Failed to create issue: {title}")
        print(f"   Error: {res.stderr.strip()}")

for issue in issues:
    create_issue(issue["title"], issue["body"], issue["labels"])
