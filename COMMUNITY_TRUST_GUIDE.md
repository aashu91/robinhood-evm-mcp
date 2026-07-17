# Sovereign Community Trust Bank templates & Guides
This document provides step-by-step scaffolding guides and operational templates showing how Families, Local Businesses, and Churches can set up their own Community Trust pools, accumulate tokenized gold/silver reserves, and distribute dividends to bypass traditional banking systems.

---

## Template 1: The Family Vault (Generational Estate Pool)
**Ideal for:** Families looking to secure joint wealth, teach children about asset management, and distribute allowances or inheritance programmatically.

### 1.1. Parameter Configuration
- **Name:** `Fernandez Family Heritage Vault`
- **Managing Directors:** Mother (`0x71C...4e8B`), Father (`0x8bF...73b1`)
- **Required Signatures:** `2` (Requires both parents to sign off on any asset withdrawals or investments)
- **Stakeholders:** Children (Hold trust pool deposit shares)

### 1.2. Operational Flow
1. **Setup:** Deploy the trust using `deploy_community_trust` with both parents' EVM addresses as directors and threshold set to 2.
2. **Wealth Pooling:** Parents deposit ETH or stablecoins into the trust address monthly.
3. **Reserves Allocation (Gold Hedging):** 
   - Father proposes an investment transaction to swap 1 ETH for `cGOLD` (tokenized Paxos Gold) via the Uniswap/Meme Curve target pool.
   - Mother signs the proposal using `sign_trust_proposal`.
   - Once threshold (2/2) is met, either parent calls `execute_trust_proposal` to perform the on-chain swap, locking gold into the family vault.
4. **Dividends Distribution:**
   - On the 1st of every month, parents call `distribute_trust_dividends` to release 0.05 ETH proportionally to children's addresses based on their pool shares.

---

## Template 2: Local Business Co-Op (Consortium Treasury)
**Ideal for:** A small group of local merchants or farm cooperatives looking to pool capital for inventory financing, hedge inflation, and share profits.

### 2.1. Parameter Configuration
- **Name:** `Downtown Merchants Cooperative Trust`
- **Managing Directors:** 5 Member Businesses (`0xMerchant1...`, `0xMerchant2...`, etc.)
- **Required Signatures:** `3` (Simple majority 3-of-5 threshold)

### 2.2. Operational Flow
1. **Setup:** Deploy the trust naming the 5 merchant addresses as directors and signature threshold to 3.
2. **Wealth Pooling:** Members deposit 10% of weekly business revenue into the trust.
3. **Reserves Allocation:**
   - Any member proposes a transaction to buy tokenized silver (`cSILVER`) to hedge cash inflation.
   - Once 3 members sign, the transaction executes, minting/buying silver tokens directly into the trust ledger.
4. **Dividends (Profit Share):**
   - At the end of each quarter, members run `distribute_trust_dividends` for custom stablecoins (e.g. `USDG`) to distribute accumulated swap yield profits back to all merchant depositors.

---

## Template 3: Church & Charity Trust (Sovereign Endowment Pool)
**Ideal for:** Non-profits, community programs, or religious organizations collecting public donations, staking them to earn interest, and funding community programs.

### 3.1. Parameter Configuration
- **Name:** `Grace Sanctuary Community Trust`
- **Managing Directors:** Board of 4 Trustees
- **Required Signatures:** `3` (Super-majority 3-of-4 threshold)

### 3.2. Operational Flow
1. **Setup:** Deploy the trust with the 4 Trustees as directors and threshold set to 3.
2. **Donation Pooling:** Public publishes the trust address. Donors send ETH or ERC-20 tokens directly to the contract.
3. **Yield Staking:**
   - Trustees propose a transaction to deposit pooled ETH into the platform's native `StakingYield` vault, staking `$ROBIN_MCP` to earn yield fees.
   - Once 3 of 4 sign, the transaction executes, securing passive interest yield.
4. **Dividend Outreach Distribution:**
   - Accumulated yield is distributed weekly. The board calls `distribute_trust_dividends` targeting community food banks or shelter addresses.
