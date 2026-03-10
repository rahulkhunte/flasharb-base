import requests, json, time
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv("/home/ubuntu/flasharb/scanner/.env")
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
print(f"RPC connected: {w3.is_connected()}")

WETH    = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
MIN_TVL = 30_000
MAX_TVL = 2_000_000
MIN_VOL = 5_000

KNOWN = {
    "0x4ed4e862860bed51a9570b96d89af5e1b0efefed",
    "0x940181a94a35a4569e4529a3cdfb74e38fd98631",
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
    "0x532f27101965dd16442e59d40670faf5ebb142e4",
    "0xac1bd2486aaf3b5c0fc3fd868558b082a531b2b4",
    "0x0b3e328455c4059eeb9e3f84b5543f74e24e7020",
    "0x0578d8a44db98b23bf096a382e016e29a5ce0ffe",
    "0xa88594d404727625a9437c3f886c7643872296ae",
}

# Aerodrome Slipstream (CL) Factory on Base
AERO_FACTORY = Web3.to_checksum_address("0x5e7BB104d84c7CB9B682AaC2F3d509f5F406809A")
AERO_ABI = [{"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"},{"name":"tickSpacing","type":"int24"}],"name":"getPool","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"}]
aero_factory = w3.eth.contract(address=AERO_FACTORY, abi=AERO_ABI)

TICK_SPACINGS = [1, 50, 100, 200]

# Step 1: Get Uni V3 tokens from GeckoTerminal (working)
print("=== Step 1: Uni V3 tokens from GeckoTerminal ===")
BASE_GT = "https://api.geckoterminal.com/api/v2"
HDR = {"Accept": "application/json;version=20230302"}
uni_tokens = {}
for page in range(1, 11):
    url = f"{BASE_GT}/networks/base/dexes/uniswap-v3-base/pools?page={page}"
    r = requests.get(url, headers=HDR, timeout=15).json()
    pools = r.get("data", [])
    if not pools: break
    for p in pools:
        attrs = p.get("attributes", {})
        tvl = float(attrs.get("reserve_in_usd") or 0)
        vol = float((attrs.get("volume_usd") or {}).get("h24") or 0)
        if tvl < MIN_TVL or tvl > MAX_TVL or vol < MIN_VOL: continue
        rels = p.get("relationships", {})
        t0 = rels.get("base_token",{}).get("data",{}).get("id","").split("_")[-1].lower()
        t1 = rels.get("quote_token",{}).get("data",{}).get("id","").split("_")[-1].lower()
        name = attrs.get("name","")
        if t0 == WETH.lower():
            mid, sym = t1, name.split("/")[0].strip()
        elif t1 == WETH.lower():
            mid, sym = t0, name.split("/")[-1].strip()
        else:
            continue
        if mid in KNOWN: continue
        uni_tokens[mid] = {"sym": sym, "tvl": tvl, "vol": vol}
    time.sleep(0.3)
print(f"  Found {len(uni_tokens)} Uni V3 tokens in TVL/vol range")

# Step 2: Check each token against Aerodrome factory ON-CHAIN
print("=== Step 2: On-chain Aerodrome factory lookup ===")
ZERO = "0x0000000000000000000000000000000000000000"
results = []
for i, (mid, info) in enumerate(uni_tokens.items()):
    token = Web3.to_checksum_address(mid)
    found_tick = None
    for tick in TICK_SPACINGS:
        try:
            pool = aero_factory.functions.getPool(WETH, token, tick).call()
            if pool != ZERO:
                found_tick = tick
                break
            pool = aero_factory.functions.getPool(token, WETH, tick).call()
            if pool != ZERO:
                found_tick = tick
                break
        except:
            continue
    if found_tick:
        results.append({**info, "mid": mid, "aero_tick": found_tick})
        print(f"  ✅ {info['sym']:<12} tick={found_tick} | TVL ${info['tvl']:>8,.0f} | Vol ${info['vol']:>8,.0f}")
    if (i+1) % 5 == 0:
        print(f"  [{i+1}/{len(uni_tokens)}] checked...")

results.sort(key=lambda x: x["vol"], reverse=True)
print(f"\n=== ✅ {len(results)} tokens on BOTH DEXes ===\n")
print(f"{'SYM':<14} {'TVL':>10} {'24H VOL':>12} TICK  ADDRESS")
print("-"*76)
for r in results[:20]:
    print(f"{r['sym']:<14} ${r['tvl']:>9,.0f} ${r['vol']:>11,.0f}  {r['aero_tick']:>3}  {r['mid']}")

print("\n\n=== PASTE INTO bot.py ===\n")
for r in results[:8]:
    vn = r["sym"].upper().replace("-","_").replace(".","")[:10]
    print(f'{vn:<10} = Web3.to_checksum_address("{r["mid"]}")')
print("\n# Add to TARGETS:")
for r in results[:8]:
    vn = r["sym"].upper().replace("-","_").replace(".","")[:10]
    print(f'    ({vn:<10}, 3000, {r["aero_tick"]}, "{r["sym"]}"),')

with open("new_pools.json","w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to new_pools.json")
