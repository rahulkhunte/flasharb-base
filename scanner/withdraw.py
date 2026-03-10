import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
wallet = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
contract_address = w3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))

print(f"🔌 Connected to Base: {w3.is_connected()}")

# Token to withdraw (WETH)
WETH = w3.to_checksum_address("0x4200000000000000000000000000000000000006")

# Minimal ABIs to check balance and execute the rescue function
ERC20_ABI = [{
    "inputs": [{"name": "account", "type": "address"}],
    "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
    "stateMutability": "view", "type": "function"
}]
RESCUE_ABI = [{
    "inputs": [{"name": "token", "type": "address"}],
    "name": "rescue", "outputs": [],
    "stateMutability": "nonpayable", "type": "function"
}]

weth_contract = w3.eth.contract(address=WETH, abi=ERC20_ABI)
arb = w3.eth.contract(address=contract_address, abi=RESCUE_ABI)

print(f"🔍 Scanning Vault: {contract_address}")
balance_wei = weth_contract.functions.balanceOf(contract_address).call()
balance_eth = w3.from_wei(balance_wei, 'ether')

if balance_wei == 0:
    print("⚠️ Vault is currently empty. Let the bot keep hunting!")
    exit()

print(f"💰 SECURED BAG DETECTED: {balance_eth:.6f} WETH")
print(f"Initiating sweep to your wallet: {wallet.address}...")

# Build the withdrawal transaction
nonce = w3.eth.get_transaction_count(wallet.address)
tx = arb.functions.rescue(WETH).build_transaction({
    'from': wallet.address,
    'nonce': nonce,
    'maxFeePerGas': w3.to_wei('0.1', 'gwei'),
    'maxPriorityFeePerGas': w3.to_wei('0.01', 'gwei'),
    'chainId': 8453
})

try:
    # Estimate gas to ensure it doesn't fail
    estimated_gas = w3.eth.estimate_gas(tx)
    tx['gas'] = int(estimated_gas * 1.2)
    
    # Sign and broadcast
    signed_tx = wallet.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"✅ Sweep transaction fired successfully!")
    print(f"🔗 https://basescan.org/tx/{tx_hash.hex()}")
    
except Exception as e:
    print(f"❌ Transaction failed: {e}")

