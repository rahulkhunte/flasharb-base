import os, asyncio, time, json, aiohttp, websockets, itertools
from web3 import Web3
from dotenv import load_dotenv
import requests as req

load_dotenv("/home/ubuntu/flasharb/scanner/.env")

# ── 4-RPC Rotation (from .env) ──────────────────────────────────
RPC_URLS = [
    os.getenv("RPC_URL_1"),
    os.getenv("RPC_URL_2"),
    os.getenv("RPC_URL_3"),
    os.getenv("RPC_URL_4"),
]
WSS_URLS = [
    os.getenv("WSS_URL_1"),
    os.getenv("WSS_URL_2"),
    os.getenv("WSS_URL_3"),
    os.getenv("WSS_URL_4"),
]
_rpc_cycle = itertools.cycle(RPC_URLS)
_wss_cycle = itertools.cycle(WSS_URLS)
def get_rpc(): return next(_rpc_cycle)
def get_wss(): return next(_wss_cycle)
# ────────────────────────────────────────────────────────────────

w3 = Web3(Web3.HTTPProvider(RPC_URLS[0]))

print("ArbBot V10 | WebSocket + Batch RPC + Zero-Loss Shield | 4-RPC Rotation")
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
VIRTUAL= Web3.to_checksum_address("0x0b3e328455c4059EEb9e3f84b5543F74E24e7020")
HIGHER = Web3.to_checksum_address("0x0578d8A44db98B23BF096A382e016e29a5Ce0ffe")
WELL   = Web3.to_checksum_address("0xA88594D404727625A9437C3f886C7643872296AE")

LOAN           = Web3.to_wei(float(os.getenv("LOAN_WETH", "0.5")), "ether")
MIN_PROFIT_WEI = Web3.to_wei(float(os.getenv("MIN_PROFIT_WETH", "0.0003")), "ether")
DEBT           = int(LOAN * 1.0005)
CONTRACT       = os.getenv("CONTRACT_ADDRESS")
CHAIN_ID       = 8453
wallet         = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

Q_UNI  = Web3.to_checksum_address("0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a")
Q_AERO = Web3.to_checksum_address("0x254cF9E1E6e233aa1AC962CB9B05b2cfeAaE15b0")

UNI_ABI  = [{"inputs": [{"components": [{"internalType": "address","name": "tokenIn","type": "address"},{"internalType": "address","name": "tokenOut","type": "address"},{"internalType": "uint256","name": "amountIn","type": "uint256"},{"internalType": "uint24","name": "fee","type": "uint24"},{"internalType": "uint160","name": "sqrtPriceLimitX96","type": "uint160"}],"internalType": "struct IQuoterV2.QuoteExactInputSingleParams","name": "params","type": "tuple"}],"name": "quoteExactInputSingle","outputs": [{"internalType": "uint256","name": "amountOut","type": "uint256"},{"internalType": "uint160","name": "sqrtPriceX96After","type": "uint160"},{"internalType": "uint32","name": "initializedTicksCrossed","type": "uint32"},{"internalType": "uint256","name": "gasEstimate","type": "uint256"}],"stateMutability": "nonpayable","type": "function"}]
AERO_ABI = [{"inputs": [{"components": [{"internalType": "address","name": "tokenIn","type": "address"},{"internalType": "address","name": "tokenOut","type": "address"},{"internalType": "uint256","name": "amountIn","type": "uint256"},{"internalType": "int24","name": "tickSpacing","type": "int24"},{"internalType": "uint160","name": "sqrtPriceLimitX96","type": "uint160"}],"internalType": "struct ISlipstreamQuoter.QuoteExactInputSingleParams","name": "params","type": "tuple"}],"name": "quoteExactInputSingle","outputs": [{"internalType": "uint256","name": "amountOut","type": "uint256"},{"internalType": "uint160","name": "sqrtPriceX96After","type": "uint160"},{"internalType": "uint32","name": "initializedTicksCrossed","type": "uint32"},{"internalType": "uint256","name": "gasEstimate","type": "uint256"}],"stateMutability": "nonpayable","type": "function"}]
ARB_ABI  = [{"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"params","type":"bytes"}],"name":"executeArb","outputs":[],"stateMutability":"nonpayable","type":"function"}]

q_uni  = w3.eth.contract(address=Q_UNI,  abi=UNI_ABI)
q_aero = w3.eth.contract(address=Q_AERO, abi=AERO_ABI)
arb    = w3.eth.contract(address=CONTRACT, abi=ARB_ABI)

TARGETS = [
    (USDC,    500,   100, "USDC-500"),
    (USDC,    3000,  200, "USDC-3000"),
    (DEGEN,   3000,  200, "DEGEN"),
    (DEGEN,   10000, 200, "DEGEN-10k"),
    (AERO,    3000,  200, "AERO"),
    (cbBTC,   500,   100, "cbBTC"),
    (ZORA,    500,   100, "ZORA"),
    (FAI,     500,   200, "FAI"),
    (REI,     500,   200, "REI"),
    (VVV,     3000,  100, "VVV"),
    (ZRO,     3000,  100, "ZRO"),
    (BRETT,   3000,  200, "BRETT"),
    (BRETT,   10000, 200, "BRETT-10k"),
    (TOSHI,   3000,  200, "TOSHI"),
    (VIRTUAL, 3000,  200, "VIRTUAL"),
    (HIGHER,  3000,  200, "HIGHER"),
    (WELL,    3000,  200, "WELL"),
]

def make_calldata():
    calls = []
    for (tok, fee, tick, label) in TARGETS:
        cd = q_uni.encode_abi("quoteExactInputSingle", [{"tokenIn":WETH,"tokenOut":tok,"amountIn":LOAN,"fee":fee,"sqrtPriceLimitX96":0}])
        calls.append((Q_UNI, cd, tok, fee, tick, label, True))
        cd = q_aero.encode_abi("quoteExactInputSingle", [{"tokenIn":WETH,"tokenOut":tok,"amountIn":LOAN,"tickSpacing":tick,"sqrtPriceLimitX96":0}])
        calls.append((Q_AERO, cd, tok, fee, tick, label, False))
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
    rpc = get_rpc()  # rotate HTTP RPC per block
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
                return await r.json()
        results = await asyncio.gather(fetch(chunk_a), fetch(chunk_b))
        raw1 = results[0] + results[1]

        batch2=[]; meta={}
        for res in raw1:
            if "result" not in res or len(res["result"]) < 66: continue
            mid_out = int(res["result"][:66], 16)
            if mid_out == 0: continue
            i = res["id"]
            _, _, tok, fee, tick, label, buy_on_uni = LEG1_CALLS[i]
            nid = len(batch2)
            if buy_on_uni:
                cd2 = q_aero.encode_abi("quoteExactInputSingle", [{"tokenIn":tok,"tokenOut":WETH,"amountIn":mid_out,"tickSpacing":tick,"sqrtPriceLimitX96":0}])
                batch2.append({"jsonrpc":"2.0","id":nid,"method":"eth_call","params":[{"to":Q_AERO,"data":cd2},"latest"]})
            else:
                cd2 = q_uni.encode_abi("quoteExactInputSingle", [{"tokenIn":tok,"tokenOut":WETH,"amountIn":mid_out,"fee":fee,"sqrtPriceLimitX96":0}])
                batch2.append({"jsonrpc":"2.0","id":nid,"method":"eth_call","params":[{"to":Q_UNI,"data":cd2},"latest"]})
            meta[nid] = (tok, fee, tick, label, buy_on_uni, mid_out)

        if not batch2:
            print(f"[Block {block_num}] No valid leg1 quotes")
            return

        async with session.post(rpc, json=batch2) as r:
            raw2 = await r.json()

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
            if best_m: best_label = best_m[3]
        ping = (time.time()-start)*1000
        print(f"[Block {block_num} | {ping:.0f}ms | {tx_count}tx {gas_saved}saves] Gap: {best_p/10**18:.6f} | Best: {best_ever/10**18:.6f} WETH | {best_label}")

        if best_p > MIN_PROFIT_WEI and best_m:
            tok,fee,tick,label,buy_on_uni,_ = best_m
            from eth_abi import encode as abi_encode
            params = abi_encode(["bool","address","uint24","int24"],[buy_on_uni,tok,fee,tick])
            route  = f"{'Uni->Aero' if buy_on_uni else 'Aero->Uni'} {label} fee={fee}"
            print(f"\nFIRING: {route} | {best_p/10**18:.6f} WETH")
            nonce = w3.eth.get_transaction_count(wallet.address)
            tx = arb.functions.executeArb(WETH, LOAN, params).build_transaction({
                "from":wallet.address,"nonce":nonce,
                "maxFeePerGas":w3.to_wei("0.05","gwei"),
                "maxPriorityFeePerGas":w3.to_wei("0.005","gwei"),
                "chainId":CHAIN_ID
            })
            try:
                tx["gas"] = int(w3.eth.estimate_gas(tx)*1.1)
            except:
                gas_saved+=1
                print(f"SHIELD blocked #{gas_saved}")
                notify(f"Shield #{gas_saved} — gap gone")
                return
            signed  = wallet.sign_transaction(tx)
            txh     = w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_count+=1
            link = f"https://basescan.org/tx/{txh.hex()}"
            print(f"TX #{tx_count}: {link}")
            notify(f"TX #{tx_count} | {route} | {best_p/10**18:.6f} WETH | {link}")
    except Exception as e:
        print(f"ERR: {e}")
    finally:
        scanning = False

async def main():
    bal = w3.eth.get_balance(wallet.address)
    print(f"Wallet: {wallet.address} | ETH: {w3.from_wei(bal, 'ether'):.6f}")
    print(f"Loan: {LOAN/10**18} WETH | Min profit: {MIN_PROFIT_WEI/10**18} WETH")
    print(f"Targets: {len(LEG1_CALLS)} routes | Contract: {CONTRACT}")
    notify(f"ArbBot V10 Live | {len(LEG1_CALLS)} routes | {LOAN/10**18} WETH loan | 4-RPC Rotation")
    async with aiohttp.ClientSession() as session:
        while True:
            wss = get_wss()  # rotate WSS on every reconnect
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
