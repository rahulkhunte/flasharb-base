# ⚡ FlashArb — On-Chain Flash Loan Arbitrage Bot

Flash-loan arbitrage bot for **Base mainnet**: a Python scanner that watches price gaps between DEX pools every block, and a Solidity contract that borrows WETH, swaps through two DEXs and repays the loan in a single transaction.

## Deployment
Deployed on Base mainnet: [`0x0db5271e5b35e9344e6be7b16d4c2817f9ae907e`](https://basescan.org/address/0x0db5271e5b35e9344e6be7b16d4c2817f9ae907e)

Known issue: this deployment's Aerodrome router address is the classic v2 router, not the Slipstream SwapRouter, so the Aerodrome leg reverts. The estimate_gas check blocks these trades before sending. Redeploy with the Slipstream router to trade.

## Zero-loss design
Every trade is simulated with `estimate_gas` before sending. If the simulation reverts, nothing is broadcast and no gas is spent. (A trade that passes simulation can still revert on-chain if prices move before it is mined.) Clone it, deploy your own `FlashArb` contract (`executeArb` is owner-only) and run it with your own wallet.

## 🔧 How It Works
1. Detects price gaps between Uniswap V3, PancakeSwap V3 and Aerodrome Slipstream pools
2. Executes a flash loan (no upfront capital) via a custom Solidity contract
3. Buys the token on the cheaper DEX → sells on the more expensive DEX → repays the loan
4. Simulates every transaction with `estimate_gas` before broadcasting

## 📊 Specs
- **Network:** Base mainnet
- **Pairs:** WETH vs USDC, cbBTC, DEGEN, AERO, BRETT, TOSHI, WELL, ZRO (24 first-leg quotes per block across 3 DEXs)
- **Quoting:** batched JSON-RPC `eth_call` to each DEX's quoter
- **RPC:** 2 HTTP endpoints rotated for batch quoting; one of them also sends transactions
- **WebSocket:** real-time block streaming via `eth_subscribe`

## 🏗️ Stack
- Python (asyncio, aiohttp, websockets, web3.py)
- Solidity (Foundry) — custom FlashArb contract
- Base mainnet | Uniswap V3 QuoterV2 | PancakeSwap V3 Quoter | Aerodrome Slipstream
- Oracle Cloud VPS (always-free tier)

## 📁 Structure
```bash
flasharb/
├── scanner/
│   ├── bot.py          # Main async scanner + executor
│   ├── find_pools.py   # Pool discovery script
│   └── withdraw.py     # Safe fund withdrawal
├── src/
│   └── FlashArb.sol    # Flash loan contract
└── foundry.toml
```

## ⚙️ Setup

```bash
cp scanner/.env.example scanner/.env  # fill in your keys
cd scanner && pip install -r requirements.txt
python3 bot.py

```

> Built by [@rahulkhunte](https://github.com/rahulkhunte)
