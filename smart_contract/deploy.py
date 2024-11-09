import json
from web3 import Web3
import os
from dotenv import load_dotenv
# Connect to Goerli testnet (or another network)
w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_NODE_URL')))

# Check if connected
if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node.")

# Load contract data
with open('contract_data.json') as f:
    contract_data = json.load(f)

abi = contract_data['abi']
bytecode = contract_data['bytecode']

# Set up the account (from MetaMask)
private_key = os.getenv('ETH_PRIVATE_KEY')
account = w3.eth.account.from_key(private_key)  # Create an account object

# Build the transaction
transaction = w3.eth.contract(abi=abi, bytecode=bytecode).constructor().build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 2000000,
    'gasPrice': w3.to_wei('10', 'gwei')
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# Wait for transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Contract deployed at address: {tx_receipt.contractAddress}")
