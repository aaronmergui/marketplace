// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "./node_modules/@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./node_modules/@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "./node_modules/@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "./node_modules/@openzeppelin/contracts/access/Ownable.sol";


contract MyToken is ERC721, ERC721URIStorage, ERC721Burnable, Ownable {

    struct Proposal {
        uint256 tokenId;
        address proposer;
        address buyer;
        uint256 price;
        bool accepted;
        uint256 proposalId;
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(address => uint256[]) public buyerProposals;
    uint256 public proposalCount;
    uint256 public tokenCount;

    constructor(address initialOwner)
        ERC721("Yezzy", "YZY")
        Ownable(initialOwner) {}

    function safeMint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        tokenCount++;
    }

    // The following functions are overrides required by Solidity.

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function createProposal(uint256 tokenId, uint256 price, address buyer) public {
        require(ownerOf(tokenId) == msg.sender, "Only the owner can create a proposal");
        proposals[proposalCount] = Proposal(tokenId, msg.sender, buyer, price, false, proposalCount);
        buyerProposals[buyer].push(proposalCount);
        approve(buyer, tokenId);
        proposalCount++;
    }

    function acceptProposal(uint256 proposalId) public payable {
        Proposal storage proposal = proposals[proposalId];
        require(!proposal.accepted, "Proposal already accepted");
        require(msg.sender == proposal.buyer, "Only the specified buyer can accept this proposal");
        require(msg.value == proposal.price, "Incorrect value sent");
        proposal.accepted = true;
        payable(proposal.proposer).transfer(msg.value);
        safeTransferFrom(proposal.proposer, msg.sender, proposal.tokenId);

        // Remove proposal from buyerProposals mapping
        _removeProposalFromBuyer(proposal.buyer, proposalId);
        // Remove proposal from proposals mapping
        delete proposals[proposalId];
    }

    function rejectProposal(uint256 proposalId) public {
        Proposal storage proposal = proposals[proposalId];
        require(msg.sender == proposal.buyer || msg.sender == proposal.proposer, "Only the proposer or the buyer can reject the proposal");
        require(!proposal.accepted, "Proposal already accepted");

        // Remove proposal from buyerProposals mapping
        _removeProposalFromBuyer(proposal.buyer, proposalId);
        // Remove proposal from proposals mapping
        delete proposals[proposalId];
    }

    function getProposalsIds(address buyer) public view returns (uint256[] memory) {
        return buyerProposals[buyer];
    }

    function _removeProposalFromBuyer(address buyer, uint256 proposalId) internal {
        uint256[] storage proposalsArray = buyerProposals[buyer];
        for (uint256 i = 0; i < proposalsArray.length; i++) {
            if (proposalsArray[i] == proposalId) {
                proposalsArray[i] = proposalsArray[proposalsArray.length - 1];
                proposalsArray.pop();
                break;
            }
        }
    }

    function getTokenIdsByOwner(address owner) public view returns (uint256[] memory) {
        uint256[] memory tokens = new uint256[](tokenCount);
        uint256 counter = 0;
        for (uint256 i = 0; i < tokenCount; i++) {
            if (ownerOf(i) == owner) {
                tokens[counter] = i;
                counter++;
            }
        }
        // Resize the array to fit the exact number of tokens found
        uint256[] memory result = new uint256[](counter);
        for (uint256 j = 0; j < counter; j++) {
            result[j] = tokens[j];
        }
        return result;
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}