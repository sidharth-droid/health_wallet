# health_wallet/eth_interface.py
from web3 import Web3, exceptions
import json
import time
from django.conf import settings
import os

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(settings.ETH_NODE_URL))

# Check if connected
if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node.")

# Load the contract ABI
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'smart_contract', 'contract_data.json')) as f:
    contract_data = json.load(f)

abi = contract_data['abi']
contract_address = settings.ETH_CONTRACT_ADDRESS

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

def add_health_record(condition, treatment_details):
    tx = contract.functions.addRecord(condition, treatment_details).build_transaction({
        'from': settings.ETH_ACCOUNT,
        'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    # tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    except exceptions.TimeExhausted:
            print("Transaction taking too long. Check network congestion.")
            return tx_hash.hex()
    
    # Extract `record_id` from event log
    record_id = None
    for log in tx_receipt.logs:
        if log.topics[0].hex() == Web3.keccak(text="RecordAdded(uint256,string,string,address)").hex():
            record_id = int(log.topics[1].hex(), 16)
            break
    return record_id


def get_health_record(record_id):
    return contract.functions.getRecord(record_id).call()

def delete_health_record(record_id):
    tx = contract.functions.deleteRecord(record_id).build_transaction({
        'from': settings.ETH_ACCOUNT,
        'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),  # Updated method name
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
        # 'gasPrice': w3.to_wei('10', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)
def update_health_record(record_id, condition, treatment_details):
    tx = contract.functions.updateRecord(record_id, condition, treatment_details).build_transaction({
        'from': settings.ETH_ACCOUNT,
        'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
        # 'gasPrice': w3.to_wei('10', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


# def grant_access(record_id, provider_address, can_view, can_edit, can_delete, is_permanent, expiry_time):
#     tx = contract.functions.grantAccess(
#         record_id, provider_address, can_view, can_edit, can_delete, is_permanent, expiry_time
#     ).build_transaction({
#         'from': settings.ETH_ACCOUNT,
#         'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
#         'gas': 2000000,
#         'gasPrice': w3.to_wei('20', 'gwei')
#     })
#     signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
#     return w3.eth.wait_for_transaction_receipt(tx_hash)


# def grant_access(record_id, provider_address, can_view, can_edit, can_delete, is_permanent, expiry_time):
#     # Ensure that provider_address is in the correct format (Ethereum address)
#     provider_address = Web3.to_checksum_address(provider_address)
    
#     # Convert expiry_time to a uint256 (timestamp)
#     expiry_time = int(expiry_time) if isinstance(expiry_time, str) else expiry_time
    
#     tx = contract.functions.grantAccess(
#         record_id,
#         provider_address,
#         can_view,
#         can_edit,
#         can_delete,
#         is_permanent,
#         expiry_time
#     ).build_transaction({
#         'from': settings.ETH_ACCOUNT,
#         'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
#         'gas': 2000000,
#         'gasPrice': w3.to_wei('20', 'gwei')
#     })
#     signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#     return w3.eth.wait_for_transaction_receipt(tx_hash)

def grant_access(record_id, provider_address, can_view, can_edit, can_delete, is_permanent, expiry_time):
    provider_address = Web3.to_checksum_address(provider_address)
    expiry_time = int(expiry_time) if expiry_time else 0

    tx = contract.functions.grantAccess(
        record_id,
        provider_address,
        can_view,
        can_edit,
        can_delete,
        is_permanent,
        expiry_time
    ).build_transaction({
        'from': settings.ETH_ACCOUNT,
        'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

def get_access_permissions(record_id, user_address):
    """Fetch permissions for a specific user on a given record."""
    user_address = Web3.to_checksum_address(user_address)
    return contract.functions.getAccessPermissions(record_id, user_address).call()
# def revoke_access(record_id, provider_address):
#     tx = contract.functions.revokeAccess(record_id, provider_address).build_transaction({
#         'from': settings.ETH_ACCOUNT,
#         'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
#         'gas': 2000000,
#         'gasPrice': w3.to_wei('20', 'gwei')
#     })
#     signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
#     return w3.eth.wait_for_transaction_receipt(tx_hash)

def revoke_access(record_id, provider_address):
    try:
        tx = contract.functions.revokeAccess(record_id, provider_address).build_transaction({
            'from': settings.ETH_ACCOUNT,
            'nonce': w3.eth.get_transaction_count(settings.ETH_ACCOUNT),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        except exceptions.TimeExhausted:
            print("Transaction is taking too long.")
            return tx_hash.hex()

        return tx_receipt

    except exceptions.Web3RPCError as e:
        print("Web3 RPC Error in revoke_access:", e)
        return None