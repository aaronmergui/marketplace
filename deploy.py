from solcx import compile_standard, install_solc
import json
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

print(abi)
# Check if connection is successful
print(f"Is connected: {w3.is_connected()}")


# Account credentials
account_address = '0xcA6D6492373110DD49644719a54A249d257E20ab'
private_key = 'db157516457f94319772029afcc07b1639a7c10d9e141cdee500af990797c9fe'

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
mytoken = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
balance = mytoken.functions.balanceOf(account_address).call()
print ("the balance of this account is ",balance)

def create_nft(token_uri, contract, account_address, private_key, token_id):
    nonce = w3.eth.get_transaction_count(account_address)
    transaction = contract.functions.safeMint(account_address, token_id, token_uri).build_transaction({
        'chainId': 80002,  # Corrected chain ID for Polygon Mumbai
        'gas': 500000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,

    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Token minted! Transaction hash: {tx_hash.hex()}')

token_uri = [
    "https://black-eldest-reptile-209.mypinata.cloud/ipfs/QmfSWz3Cwj8rphQkF8hgqoM7csD4tSeHpHEKFTr88z8WcH",
    "https://black-eldest-reptile-209.mypinata.cloud/ipfs/QmU5etbnXgeWCkTyVLddHDfMtKmboUKPNeSdKQpzX5bMbk",
    "https://black-eldest-reptile-209.mypinata.cloud/ipfs/Qmbo84rph8w2R2vh87pJBrbHShGeuPENgP2wQ6bRdaefM9",
    "https://black-eldest-reptile-209.mypinata.cloud/ipfs/QmQEZDZoULnaELqBbCyiygh2opEVaaBooXFVsRVZCZYrao"
]

for i in range(15):
        balance = mytoken.functions.balanceOf(account_address).call()
        print(balance)
        create_nft(token_uri[i % 4 ], mytoken, account_address, private_key, i)


    # else:
    #     private_key2 = "597859c569ecc97c7f6f2f78eb10636fbb4fba6761366140cb9a0851435193cf"
    #     account_address2 = "0xcA6D6492373110DD49644719a54A249d257E20ab"
    #     balance = contract_instance.functions.balanceOf(account_address2).call()
    #     print(balance)
    #     if i % 2 == 0:
    #         create_nft(token_uri[0], contract_instance, account_address2, private_key2, i)
    #     else:
    #         create_nft(token_uri[1], contract_instance, account_address2, private_key2, i)


