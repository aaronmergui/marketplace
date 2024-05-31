import json
from solcx import compile_standard, install_solc
from web3 import Web3


infura_url = "https://polygon-amoy.infura.io/v3/2b52df7f89e64d01a7460cef5d48324f"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Install the Solidity compiler version
install_solc('0.8.25')

# Solidity source code
with open('MyToken.sol', 'r') as file:
    mytoken_sol = file.read()

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "MyToken.sol": {
            "content": mytoken_sol
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version='0.8.25')

# Extract ABI and bytecode
abi = compiled_sol['contracts']['MyToken.sol']['MyToken']['abi']
bytecode = compiled_sol['contracts']['MyToken.sol']['MyToken']['evm']['bytecode']['object']


# Check if connection is successful
print(f"Is connected: {w3.is_connected()}")

# Set up account details
account_address = '0x60753fee8A753E5D6F0d0e42a74E1ad0DE0EcD6f'
private_key = 'db157516457f94319772029afcc07b1639a7c10d9e141cdee500af990797c9fe'
second_account_address = '0xcA6D6492373110DD49644719a54A249d257E20ab'
second_private_key = '597859c569ecc97c7f6f2f78eb10636fbb4fba6761366140cb9a0851435193cf'

# Deploy the contract
MyToken = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account_address)
transaction = MyToken.constructor(account_address).build_transaction({
    'chainId': 80002,  # Adjust according to your local network's chain ID
    'gas': 5000000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce,
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Contract deployed at address: {tx_receipt.contractAddress}")

# Create contract instance
mytoken = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Interacting with the contract
# Mint a new token
balance = mytoken.functions.balanceOf(account_address).call()

nonce = w3.eth.get_transaction_count(account_address)
transaction = mytoken.functions.safeMint(account_address, 1,"https://black-eldest-reptile-209.mypinata.cloud/ipfs/QmU5etbnXgeWCkTyVLddHDfMtKmboUKPNeSdKQpzX5bMbk").build_transaction({
    'chainId': 80002,
    'gas': 500000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce,
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

owner = mytoken.functions.ownerOf(1).call()
print(f"New owner of token 1: {owner}")
# Create a proposal
nonce = w3.eth.get_transaction_count(account_address)
transaction = mytoken.functions.createProposal(1, w3.to_wei(100, 'gwei'), second_account_address).build_transaction({
    'chainId': 80002,
    'gas': 500000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce,
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
w3.eth.wait_for_transaction_receipt(tx_hash)
proposals_ids = mytoken.functions.getProposalsIds(second_account_address).call()
print(proposals_ids)
# Accept a proposal
nonce = w3.eth.get_transaction_count(second_account_address)
transaction = mytoken.functions.acceptProposal(0).build_transaction({
    'chainId': 80002,
    'gas': 500000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce,
    'value': w3.to_wei(100, 'gwei')
})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=second_private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

# Check token owner
balance = mytoken.functions.balanceOf(account_address).call()

owner = mytoken.functions.ownerOf(1).call()
print(f"New owner of token 1: {owner}")
