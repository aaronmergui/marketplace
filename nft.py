import re
from web3 import Web3
import requests
from models import NFT
from database import db
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

CHAIN_ID = 80002
nft = Blueprint('nft', __name__)
NUMBER_OF_NFT = 10
contract_address = '0x0FD8Ef470A3f33C648C583A782070cc05f36004b'
abi=[{'inputs': [{'internalType': 'address', 'name': 'initialOwner', 'type': 'address'}], 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'inputs': [{'internalType': 'address', 'name': 'sender', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}, {'internalType': 'address', 'name': 'owner', 'type': 'address'}], 'name': 'ERC721IncorrectOwner', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'operator', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'ERC721InsufficientApproval', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'approver', 'type': 'address'}], 'name': 'ERC721InvalidApprover', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'operator', 'type': 'address'}], 'name': 'ERC721InvalidOperator', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}], 'name': 'ERC721InvalidOwner', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}], 'name': 'ERC721InvalidReceiver', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'sender', 'type': 'address'}], 'name': 'ERC721InvalidSender', 'type': 'error'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'ERC721NonexistentToken', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}], 'name': 'OwnableInvalidOwner', 'type': 'error'}, {'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}], 'name': 'OwnableUnauthorizedAccount', 'type': 'error'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'approved', 'type': 'address'}, {'indexed': True, 'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'Approval', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'operator', 'type': 'address'}, {'indexed': False, 'internalType': 'bool', 'name': 'approved', 'type': 'bool'}], 'name': 'ApprovalForAll', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': '_fromTokenId', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': '_toTokenId', 'type': 'uint256'}], 'name': 'BatchMetadataUpdate', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': '_tokenId', 'type': 'uint256'}], 'name': 'MetadataUpdate', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'newOwner', 'type': 'address'}], 'name': 'OwnershipTransferred', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'from', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'to', 'type': 'address'}, {'indexed': True, 'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'Transfer', 'type': 'event'}, {'inputs': [{'internalType': 'uint256', 'name': 'proposalId', 'type': 'uint256'}], 'name': 'acceptProposal', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'approve', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'burn', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'buyerProposals', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'price', 'type': 'uint256'}, {'internalType': 'address', 'name': 'buyer', 'type': 'address'}], 'name': 'createProposal', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'getApproved', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'buyer', 'type': 'address'}], 'name': 'getProposalsIds', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}], 'name': 'getTokenIdsByOwner', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'internalType': 'address', 'name': 'operator', 'type': 'address'}], 'name': 'isApprovedForAll', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'name', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'owner', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'ownerOf', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'proposalCount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'proposals', 'outputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}, {'internalType': 'address', 'name': 'proposer', 'type': 'address'}, {'internalType': 'address', 'name': 'buyer', 'type': 'address'}, {'internalType': 'uint256', 'name': 'price', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'accepted', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'proposalId', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'proposalId', 'type': 'uint256'}], 'name': 'rejectProposal', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}, {'internalType': 'string', 'name': 'uri', 'type': 'string'}], 'name': 'safeMint', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'safeTransferFrom', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'safeTransferFrom', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'operator', 'type': 'address'}, {'internalType': 'bool', 'name': 'approved', 'type': 'bool'}], 'name': 'setApprovalForAll', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bytes4', 'name': 'interfaceId', 'type': 'bytes4'}], 'name': 'supportsInterface', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'symbol', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'tokenCount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'tokenURI', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}], 'name': 'transferFrom', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'newOwner', 'type': 'address'}], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
MIN_PRICE=10000000000
NUM_GAS=500000
STOCK_URL= "https://stockx.com/search?s="
class Proposal:

    def __init__(self,token_id,image, description, price,name,owner,proposal_id,stockX):
        self.token_id = token_id
        self.image = image
        self.description = description
        self.price = price
        self.name = name
        self.owner = owner
        self.proposal_id = proposal_id
        self.stockX=stockX

def create_contract_instance(contract_address):
    infura_url = "https://polygon-amoy.infura.io/v3/c23c1d385e94439baf439032c3dde8a2"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    return web3,web3.eth.contract(address=contract_address, abi=abi)

w3,contract_instance = create_contract_instance(contract_address)

GAS_PRICE=w3.to_wei('20', 'gwei')

def extract_value(json_string, key):
    pattern = f'"{key}"\s*:\s*"([^"]+)"'
    match = re.search(pattern, json_string)
    return match.group(1) if match else None


def get_from_uri(i):
    uri = contract_instance.functions.tokenURI(i).call()
    response = requests.get(uri)
    content = response.content.decode('utf-8')
    corrected_content = content.replace('\r\n', '').replace("'", '"')
    name = extract_value(corrected_content, 'name')
    description = extract_value(corrected_content, 'description')
    image = extract_value(corrected_content, 'image')
    stockX = STOCK_URL+name.replace(" ","+")
    return name, description, image,stockX

def get_list_nfts(account_address):
    nfts = []
    nfts_ids =contract_instance.functions.getTokenIdsByOwner(account_address).call()
    for token_id in nfts_ids:
        token_id = int(token_id)
        name, description, image,stockX = get_from_uri(token_id)
        new_nft = NFT(token_id=token_id, uri=image, description=description, name=name, stockX=stockX)
        nft = NFT.query.filter_by(token_id=token_id).first()
        if nft:
            nfts.append(new_nft)
        else:
            db.session.add(new_nft)
            db.session.commit()
            nfts.append(new_nft)
    return nfts

def get_info_from_proposal(proposals):
    final_proposals=[]
    for proposal in proposals:
        name,description,image,stockX = get_from_uri(proposal[0])
        p= Proposal(proposal[0],image, description,proposal[3],name,proposal[1],proposal[-1],stockX)
        final_proposals.append(p)
    return final_proposals
def view_proposals():
    print(current_user.eth_public_address)
    proposals_ids = contract_instance.functions.getProposalsIds(current_user.eth_public_address).call()
    proposals = []
    for id in proposals_ids:
        prop=contract_instance.functions.proposals(id).call()
        proposals.append(prop)
    return proposals
@nft.route('/list')
@login_required
def list_nfts():

    account_address = current_user.eth_public_address
    balance_wei = w3.eth.get_balance(account_address)
    nfts = get_list_nfts(account_address)
    proposals = view_proposals()
    final_proposals = get_info_from_proposal(proposals)
    return render_template('nfts.html', balance= balance_wei,nfts=nfts, proposals= final_proposals,)

@nft.route('/sell/<int:token_id>', methods=['GET', 'POST'])
@login_required
def sell(token_id):
    if request.method == 'POST':
        metamask_address = request.form['metamask_address']
        price = request.form['price']
        propose_sell(token_id, metamask_address, price)
        return list_nfts()

    return render_template('sell.html', token_id=token_id,min_price=MIN_PRICE)


def propose_sell(token_id, buyer_address, price):

    print(f"propose_sell{current_user.eth_public_address}")

    nonce = w3.eth.get_transaction_count(current_user.eth_public_address)
    txn = contract_instance.functions.createProposal(int(token_id),int(price), buyer_address).build_transaction({
        'chainId': CHAIN_ID,
        'gas': NUM_GAS,
        'gasPrice': GAS_PRICE,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=current_user.eth_private_address)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

def accept_proposal(price,proposal_id):
    # TODO try except when not enough
    print(f"accept proposal {current_user.eth_public_address}")
    print(f"price:{price},pricetype{type(price)}")
    try:
        nonce = w3.eth.get_transaction_count(current_user.eth_public_address)
        txn = contract_instance.functions.acceptProposal(int(proposal_id)).build_transaction({
            'chainId': CHAIN_ID,
            'gas': NUM_GAS,
            'gasPrice':GAS_PRICE,
            'nonce': nonce,
            'value':price
        })

        signed_txn = w3.eth.account.sign_transaction(txn, current_user.eth_private_address)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)


        balance = contract_instance.functions.balanceOf(current_user.eth_public_address).call()
        print(balance)
    except Exception as e:
        error_message = str(e)
        flash(error_message, 'danger')

def decline_proposal(proposal_id):
    print(f"decline proposal {current_user.eth_public_address}")

    nonce = w3.eth.get_transaction_count(current_user.eth_public_address)
    txn = contract_instance.functions.rejectProposal(int(proposal_id)).build_transaction({
        'chainId': CHAIN_ID,
        'gas': NUM_GAS,
        'gasPrice': GAS_PRICE,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, current_user.eth_private_address)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)



@nft.route('/accept_proposal/<int:proposal_id>/<int:price>')
@login_required
def handle_accept_proposal(proposal_id,price):
    accept_proposal(price,proposal_id)
    return redirect(url_for('nft.list_nfts'))

@nft.route('/decline_proposal/<int:proposal_id>')
@login_required
def handle_decline_proposal(proposal_id):
    decline_proposal(proposal_id)
    return redirect(url_for('nft.list_nfts'))

