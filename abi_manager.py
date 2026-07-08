# abi_manager.py
# SQLite cache for smart contract ABIs and simplified human-readable signature generators

import os
import json
import sqlite3
import aiosqlite
from constants import PREPACKAGED_ABIS

DB_DIR = os.path.expanduser("~/.config/robinhood-evm-mcp")
DB_PATH = os.path.join(DB_DIR, "abi_cache.db")

async def init_db():
    """Initializes the SQLite database schema for ABI caching and token registry."""
    os.makedirs(DB_DIR, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS abi_cache (
                contract_address TEXT PRIMARY KEY,
                abi_json TEXT NOT NULL,
                simplified_signatures TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS token_registry (
                ticker TEXT PRIMARY KEY,
                address TEXT NOT NULL,
                name TEXT,
                decimals INTEGER DEFAULT 18,
                is_scanned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

def extract_signatures(abi):
    """Converts a standard JSON ABI to a list of clean, human-readable signatures."""
    signatures = []
    try:
        if isinstance(abi, str):
            abi = json.loads(abi)
        
        for item in abi:
            if item.get("type") == "function":
                name = item.get("name")
                inputs = item.get("inputs", [])
                outputs = item.get("outputs", [])
                
                # Format inputs: type name, e.g., "address _to, uint256 _value"
                input_params = []
                for inp in inputs:
                    param = inp.get("type", "")
                    name_str = inp.get("name", "")
                    if name_str:
                        param += f" {name_str}"
                    input_params.append(param)
                
                # Format outputs: type name
                output_params = []
                for outp in outputs:
                    param = outp.get("type", "")
                    name_str = outp.get("name", "")
                    if name_str:
                        param += f" {name_str}"
                    output_params.append(param)
                
                stateMutability = item.get("stateMutability", "")
                mutability_str = f" [{stateMutability}]" if stateMutability in ["view", "pure", "payable"] else ""
                
                inputs_str = ", ".join(input_params)
                outputs_str = f" returns ({', '.join(output_params)})" if output_params else ""
                
                sig = f"{name}({inputs_str}){outputs_str}{mutability_str}"
                signatures.append(sig)
    except Exception as e:
        signatures.append(f"Error parsing signatures: {str(e)}")
    
    return signatures

async def save_abi(contract_address, abi):
    """Saves a JSON ABI for a given contract address to the local SQLite database."""
    await init_db()
    contract_address = contract_address.lower()
    
    if isinstance(abi, list):
        abi_json = json.dumps(abi)
    else:
        abi_json = abi
        abi = json.loads(abi)
        
    signatures = "\n".join(extract_signatures(abi))
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO abi_cache (contract_address, abi_json, simplified_signatures)
            VALUES (?, ?, ?)
        """, (contract_address, abi_json, signatures))
        await db.commit()
    
    return signatures

async def get_abi(contract_address):
    """Retrieves the ABI and human-readable signatures for a contract address."""
    contract_address = contract_address.lower()
    
    # 1. Check pre-packaged constants
    # (Checking if matches a known ticker)
    for ticker, addr in PREPACKAGED_ABIS.items():
        # Just simple mapping checker for ERC20 as fallback
        pass
        
    # 2. Check local SQLite cache
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT abi_json, simplified_signatures FROM abi_cache WHERE contract_address = ?
        """, (contract_address,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0]), row[1]
                
    # 3. Fallback: Return standard ERC20 if address is a known ticker mapping
    return None, None

async def register_token(ticker, address, name=None, decimals=18, is_scanned=0):
    """Saves a token to the local registry database."""
    await init_db()
    ticker = ticker.upper()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO token_registry (ticker, address, name, decimals, is_scanned)
            VALUES (?, ?, ?, ?, ?)
        """, (ticker, address, name, decimals, is_scanned))
        await db.commit()

async def get_registered_tokens():
    """Retrieves all registered/scanned tokens."""
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT ticker, address, name, decimals, is_scanned FROM token_registry") as cursor:
            rows = await cursor.fetchall()
            return [{"ticker": r[0], "address": r[1], "name": r[2], "decimals": r[3], "is_scanned": r[4]} for r in rows]

async def resolve_ticker_to_address(ticker):
    """Checks constants first, then local SQLite token registry to resolve a ticker symbol to its address."""
    ticker = ticker.upper()
    from constants import TICKER_MAPPINGS
    if ticker in TICKER_MAPPINGS:
        return TICKER_MAPPINGS[ticker]
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT address FROM token_registry WHERE ticker = ?", (ticker,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return None
