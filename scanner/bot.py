import os, asyncio, time, json, aiohttp, websockets, itertools
from web3 import Web3
from dotenv import load_dotenv
import requests as req

load_dotenv("/home/ubuntu/flasharb/scanner/.env")

# ── WSS: Alchemy only (cheap, just block notifications) ─────────
WSS_URLS = [
    os.getenv("WSS_URL_1"),
    os.getenv("WSS_URL_2"),
    os.getenv("WSS_URL_3"),
    os.getenv("WSS_URL_4"),
]

# ── HTTP: Free unlimited RPCs for heavy batch eth_call work ─────
RPC_URLS = [
    os.getenv("RPC_URL_2"),
    os.getenv("RPC_URL_1"),
]

_rpc_cycle = itertools.cycle(RPC_URLS)
_wss_cycle = itertools.cycle(WSS_URLS)
def get_rpc(): return next(_rpc_cycle)
def get_wss(): return next(_wss_cycle)
# ────────────────────────────────────────────────────────────────

# w3 uses Alchemy for reliable tx sending (rare, low CU)
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL_1")))

print("ArbBot V11 | Free RPC Batch + Alchemy WSS | Zero-Loss Shield")
print(f"Connected: {w3.is_connected()} | Block: {w3.eth.block_number}")

WETH   = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
DEGEN  = Web3.to_checksum_address("0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed")
AERO   = Web3.to_checksum_address("0x940181a94A35A4569E4529A3CDfB74e38FD98631")
USDC   = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
cbBTC  = Web3.to_checksum_address("0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf")
ZORA   = Web3.to_checksum_address("0x1111111111166b7fe7bd91427724b487980afc69")
FAI    = Web3.to_checksum_address("0xb33ff54b9f7242ef1593d2c9bcd8f9df46c77935")
REI    = Web3.to_checksum_address("0x6b2504a03ca4d43d0d73776f6ad46dab2f2a4cfd")
VVV    = Web3.to_checksum_address("0xacfe6019ed1a7dc6f7b508c02d1b04ec88cc21bf")
ZRO    = Web3.to_checksum_address("0x6985884c4392d348587b19cb9eaaf157f13271cd")
BRETT  = Web3.to_checksum_address("0x532f27101965dd16442E59d40670FaF5eBB142E4")
TOSHI  = Web3.to_checksum_address("0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4")
HIGHER = Web3.to_checksum_address("0x0578d8A44db98B23BF096A382e016e29a5Ce0ffe")
WELL   = Web3.to_checksum_address("0xA88594D404727625A9437C3f886C7643872296AE")

LOAN           = Web3.to_wei(float(os.getenv("LOAN_WETH", "0.025")), "ether")
MIN_PROFIT_WEI = Web3.to_wei(float(os.getenv("MIN_PROFIT_WETH", "0.00003")), "ether")
DEBT           = int(LOAN * 1.0005)
CONTRACT       = os.getenv("CONTRACT_ADDRESS")
CHAIN_ID       = 8453
wallet         = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

Q_UNI  = Web3.to_checksum_address("0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a")
Q_AERO = Web3.to_checksum_address("0x254cF9E1E6e233aa1AC962CB9B05b2cfeAaE15b0")
Q_CAKE = Web3.to_checksum_address("0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997")

UNI_ABI  = [{"inputs": [{"components": [{"internalType": "address","name": "tokenIn","type": "address"},{"internalType": "address","name": "tokenOut","type": "address"},{"internalType": "uint256","name": "amountIn","type": "uint256"},{"internalType": "uint24","name": "fee","type": "uint24"},{"internalType": "uint160","name": "sqrtPriceLimitX96","type": "uint160"}],"internalType": "struct IQuoterV2.QuoteExactInputSingleParams","name": "params","type": "tuple"}],"name": "quoteExactInputSingle","outputs": [{"internalType": "uint256","name": "amountOut","type": "uint256"},{"internalType": "uint160","name": "sqrtPriceX96After","type": "uint160"},{"internalType": "uint32","name": "initializedTicksCrossed","type": "uint32"},{"internalType": "uint256","name": "gasEstimate","type": "uint256"}],"stateMutability": "nonpayable","type": "function"}]
AERO_ABI = [{"inputs": [{"components": [{"internalType": "address","name": "tokenIn","type": "address"},{"internalType": "address","name": "tokenOut","type": "address"},{"internalType": "uint256","name": "amountIn","type": "uint256"},{"internalType": "int24","name": "tickSpacing","type": "int24"},{"internalType": "uint160","name": "sqrtPriceLimitX96","type": "uint160"}],"internalType": "struct ISlipstreamQuoter.QuoteExactInputSingleParams","name": "params","type": "tuple"}],"name": "quoteExactInputSingle","outputs": [{"internalType": "uint256","name": "amountOut","type": "uint256"},{"internalType": "uint160","name": "sqrtPriceX96After","type": "uint160"},{"internalType": "uint32","name": "initializedTicksCrossed","type": "uint32"},{"internalType": "uint256","name": "gasEstimate","type": "uint256"}],"stateMutability": "nonpayable","type": "function"}]
ARB_ABI  = [{"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"params","type":"bytes"}],"name":"executeArb","outputs":[],"stateMutability":"nonpayable","type":"function"}]

q_uni  = w3.eth.contract(address=Q_UNI,  abi=UNI_ABI)
q_aero = w3.eth.contract(address=Q_AERO, abi=AERO_ABI)
q_cake = w3.eth.contract(address=Q_CAKE, abi=UNI_ABI)
arb    = w3.eth.contract(address=CONTRACT, abi=ARB_ABI)

TARGETS = [
    (USDC,  100,  100, 1,   "USDC"),
    (cbBTC, 500,  100, 100, "cbBTC"),
    (DEGEN, 3000, 500, 200, "DEGEN"),
    (AERO,  3000, 100, 200, "AERO"),
    (BRETT, 3000, 500, 200, "BRETT"),
    (TOSHI, 3000, 500, 200, "TOSHI"),
    (WELL,  3000, 500, 200, "WELL"),
    (ZRO,   3000, 2500,100, "ZRO"),
]

def make_calldata():
    calls = []
    for (tok, uni_fee, cake_fee, tick, label) in TARGETS:
        cd = q_uni.encode_abi("quoteExactInputSingle", [{"tokenIn":WETH,"tokenOut":tok,"amountIn":LOAN,"fee":uni_fee,"sqrtPriceLimitX96":0}])
        calls.append((Q_UNI,  cd, tok, uni_fee, cake_fee, tick, label, "UNI"))
        cd = q_cake.encode_abi("quoteExactInputSingle", [{"tokenIn":WETH,"tokenOut":tok,"amountIn":LOAN,"fee":cake_fee,"sqrtPriceLimitX96":0}])
        calls.append((Q_CAKE, cd, tok, uni_fee, cake_fee, tick, label, "CAKE"))
        cd = q_aero.encode_abi("quoteExactInputSingle", [{"tokenIn":WETH,"tokenOut":tok,"amountIn":LOAN,"tickSpacing":tick,"sqrtPriceLimitX96":0}])
        calls.append((Q_AERO, cd, tok, uni_fee, cake_fee, tick, label, "AERO"))
    return calls

LEG1_CALLS = make_calldata()

def notify(msg):
    t = os.getenv("TELEGRAM_TOKEN",""); c = os.getenv("TELEGRAM_CHAT_ID","")
    if not t or not c: return
    try: req.post(f"https://api.telegram.org/bot{t}/sendMessage", json={"chat_id":c,"text":msg,"parse_mode":"HTML"}, timeout=5)
    except: pass

count=0; tx_count=0; gas_saved=0; best_ever=-10**18; best_label='?'; scanning=False

async def scan_block(session, block_num):
    global count, tx_count, gas_saved, best_ever, best_label, scanning
    if scanning: return
    scanning = True
    rpc = get_rpc()  # free RPC for batch calls
    try:
        start = time.time()
        batch1 = [
            {"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":to,"data":cd},"latest"]}
            for i,(to,cd,*_) in enumerate(LEG1_CALLS)
        ]
        mid = len(batch1) // 2
        chunk_a, chunk_b = batch1[:mid], batch1[mid:]
        async def fetch(b):
            async with session.post(rpc, json=b) as r:
                res = await r.json()
                return res if isinstance(res, list) else []
        results = await asyncio.gather(fetch(chunk_a), fetch(chunk_b))
        raw1 = results[0] + results[1]

        batch2=[]; meta={}
        for res in raw1:
            if "result" not in res or len(res["result"]) < 66: continue
            mid_out = int(res["result"][:66], 16)
            if mid_out == 0: continue
            i = res["id"]
            _, _, tok, uni_fee, cake_fee, tick, label, source = LEG1_CALLS[i]
            nid = len(batch2)
            if source in ("UNI", "CAKE"):
                cd2 = q_aero.encode_abi("quoteExactInputSingle", [{"tokenIn":tok,"tokenOut":WETH,"amountIn":mid_out,"tickSpacing":tick,"sqrtPriceLimitX96":0}])
                batch2.append({"jsonrpc":"2.0","id":nid,"method":"eth_call","params":[{"to":Q_AERO,"data":cd2},"latest"]})
            else:
                cd2 = q_uni.encode_abi("quoteExactInputSingle", [{"tokenIn":tok,"tokenOut":WETH,"amountIn":mid_out,"fee":uni_fee,"sqrtPriceLimitX96":0}])
                batch2.append({"jsonrpc":"2.0","id":nid,"method":"eth_call","params":[{"to":Q_UNI,"data":cd2},"latest"]})
            meta[nid] = (tok, uni_fee, cake_fee, tick, label, source, mid_out)

        if not batch2:
            print(f"[Block {block_num}] No valid leg1 quotes")
            return

        async with session.post(rpc, json=batch2) as r:
                raw2 = await r.json()
                if not isinstance(raw2, list):
                    print(f"RPC leg2 rejected, skipping")
                    return

        best_p=-10**18; best_m=None
        for res in raw2:
            if "result" not in res or len(res["result"]) < 66: continue
            weth_back = int(res["result"][:66], 16)
            profit = weth_back - DEBT
            if profit > best_p:
                best_p = profit
                best_m = meta[res["id"]]

        count += 1
        if best_p > best_ever:
            best_ever = best_p
            if best_m: best_label = f"{best_m[5]}->{'AERO' if best_m[5] != 'AERO' else 'UNI'} {best_m[4]}"
        ping = (time.time()-start)*1000
        print(f"[Block {block_num} | {ping:.0f}ms | {tx_count}tx {gas_saved}saves] Gap: {best_p/10**18:.6f} | Best: {best_ever/10**18:.6f} WETH | {best_label}")

        if best_p > MIN_PROFIT_WEI and best_m:
            tok,uni_fee,cake_fee,tick,label,source,_ = best_m
            from eth_abi import encode as abi_encode
            buy_on_uni = (source != "AERO")
            params = abi_encode(["bool","address","uint24","int24"],[buy_on_uni,tok,uni_fee,tick])
            route  = f"{source}->{'AERO' if buy_on_uni else 'UNI'} {label}"
            print(f"\n🚀 FIRING: {route} | profit={best_p/10**18:.6f} WETH")
            notify(f"🚀 Attempting fire: {route} | {best_p/10**18:.6f} WETH")
            try:
                nonce = w3.eth.get_transaction_count(wallet.address)
                base_fee = w3.eth.get_block('latest')['baseFeePerGas']
                tx = arb.functions.executeArb(WETH, LOAN, params).build_transaction({
                    "from":wallet.address,"nonce":nonce,
                    "maxFeePerGas":int(base_fee * 2),
                    "maxPriorityFeePerGas":w3.to_wei("0.001","gwei"),
                    "chainId":CHAIN_ID
                })
                try:
                    tx["gas"] = int(w3.eth.estimate_gas(tx)*1.1)
                    print(f"Gas estimated: {tx['gas']}")
                except Exception as gas_err:
                    gas_saved+=1
                    print(f"SHIELD blocked #{gas_saved} | reason: {gas_err}")
                    notify(f"🛡 Shield #{gas_saved} — {route} | gap gone by tx time")
                    return
                signed = wallet.sign_transaction(tx)
                txh    = w3.eth.send_raw_transaction(signed.raw_transaction)
                tx_count+=1
                link = f"https://basescan.org/tx/{txh.hex()}"
                print(f"✅ TX #{tx_count}: {link}")
                notify(f"✅ TX #{tx_count} | {route} | {best_p/10**18:.6f} WETH | {link}")
            except Exception as tx_err:
                print(f"TX ERROR: {tx_err}")
                notify(f"❌ TX failed: {route} | {tx_err}")
    except Exception as e:
        print(f"ERR: {e}")
    finally:
        scanning = False

async def main():
    bal = w3.eth.get_balance(wallet.address)
    print(f"Wallet: {wallet.address} | ETH: {w3.from_wei(bal, 'ether'):.6f}")
    print(f"Loan: {LOAN/10**18} WETH | Min profit: {MIN_PROFIT_WEI/10**18} WETH")
    print(f"Targets: {len(LEG1_CALLS)} routes | Contract: {CONTRACT}")
    print(f"Free RPCs: {RPC_URLS}")
    notify(f"ArbBot V11 Live | {len(LEG1_CALLS)} routes | Free RPC batch | Alchemy WSS")
    async with aiohttp.ClientSession() as session:
        while True:
            wss = get_wss()
            try:
                async with websockets.connect(wss) as ws:
                    await ws.send(json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["newHeads"]}))
                    await ws.recv()
                    print(f"WebSocket live → {wss[-14:]}")
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "params" in data:
                            asyncio.create_task(scan_block(session, int(data["params"]["result"]["number"],16)))
            except Exception as e:
                print(f"WSS dropped: {e} reconnecting...")
                await asyncio.sleep(3)

if __name__=="__main__":
    asyncio.run(main())
