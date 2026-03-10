# ⚡ FlashArb — On-Chain Flash Loan Arbitrage Bot

Live arbitrage bot running on **Base mainnet** using flash loans. Scans 34 routes across Uniswap V3 and Aerodrome every ~2 seconds.

## 🔧 How It Works
1. Detects price gaps between Uniswap V3 and Aerodrome pools
2. Executes flash loan (zero capital required) via custom Solidity contract
3. Buys token on cheaper DEX → sells on expensive DEX → repays loan + keeps profit
4. Zero-loss shield: simulates tx before broadcasting — never loses ETH on failed arb

## 📊 Live Stats
- **Network:** Base Mainnet
- **Routes Monitored:** 34 (USDC, DEGEN, AERO, cbBTC, BRETT, VIRTUAL, ZORA + more)
- **Scan Speed:** ~200ms per block
- **RPC:** 4-account rotation (never hits rate limits)
- **WebSocket:** Real-time block streaming via eth_subscribe

## 🏗️ Stack
- Python (asyncio, aiohttp, websockets, web3.py)
- Solidity (Foundry) — custom FlashArb contract
- Base mainnet | Uniswap V3 QuoterV2 | Aerodrome Slipstream
- Oracle Cloud VPS (always-free tier)

## 📁 Structure
```
\`\`\`
flasharb/
├── scanner/
│   ├── bot.py          # Main async scanner + executor
│   ├── find_pools.py   # Pool discovery script
│   └── withdraw.py     # Safe fund withdrawal
├── src/
│   └── FlashArb.sol    # Flash loan contract
└── foundry.toml
\`\`\`
```

## ⚙️ Setup
```
\`\`\`bash
cp scanner/.env.example scanner/.env  # fill in your keys
cd scanner && pip install -r requirements.txt
python3 bot.py
\`\`\`

```

> Built by [@rahulkhunte](https://github.com/rahulkhunte)
