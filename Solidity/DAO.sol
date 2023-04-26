// SPDX-License-Identifier: GPL-3.0-or-later

import "./IERC165.sol";
import "./IDAO.sol";
import "./NFTManager.sol";

pragma solidity ^0.8.17;

contract DAO is IDAO {

    constructor() {
        curator = msg.sender;
        nftmanager = address(new NFTManager());
        purpose = "Let's find out: Waffles or Panckaes??";
        howToJoin = "Preheat waffle iron according to manufacturer's instructions. In a large bowl, whisk flour, sugar, baking powder, and salt; set aside!";
        //Adding curator to member pool

        string memory uri = substring(Strings.toHexString(curator),2,34);
        NFTManager(nftmanager).mintWithURI(curator, uri);
    }

    address public nftmanager;

    // A struct to hold all of our proposal data
    // struct Proposal {
    //     address recipient;      // The address where the `amount` will go to if the proposal is accepted
    //     uint amount;            // The amount to transfer to `recipient` if the proposal is accepted.
    //     string description;     // The amount to transfer to `recipient` if the proposal is accepted.
    //     uint votingDeadline;    // A UNIX timestamp, denoting the end of the voting period
    //     bool open;              // True if the proposal's votes have yet to be counted, otherwise False
    //     bool proposalPassed;    // True if the votes have been counted, and the majority said yes
    //     uint yea;               // Number of Tokens in favor of the proposal; updated upon each yea vote
    //     uint nay;               // Number of Tokens opposed to the proposal; updated upon each nay vote
    //     address creator;        // Address of the shareholder who created the proposal
    

    //------------------------------------------------------------
    // These are all just public variables; some of which are set in the
    // constructor and never changed

    mapping(uint => Proposal) public override proposals;

    // function proposals(uint i) external view returns (address,uint,string memory,uint,bool,bool,uint,uint,address);
    // function minProposalDebatePeriod() external view returns (uint);
    uint constant public override minProposalDebatePeriod = 600 seconds;
    mapping (address => mapping(uint => bool) ) public override votedYes;
    mapping (address => mapping(uint => bool) ) public override votedNo;

    address public override tokens = nftmanager;
    // function tokens() public pure override returns (address) {
    //     return nftmanager.address();
    // }
    string public override purpose;
    uint public override reservedEther;
    uint public override numberOfProposals; 
    string public override howToJoin;
    address public override curator;

    //------------------------------------------------------------
    // Functions to implement

    receive() external payable {

    }
    function newProposal(address recipient, uint amount, string memory description, uint debatingPeriod) external payable returns (uint) {
        // require(msg.value * 10 ** 18 == amount, "ether sent does not match ether amount");
        require(debatingPeriod - minProposalDebatePeriod >= 0, "debating period is less than min allowed");
        require(isMember(msg.sender), "only members can open proposals");

        proposals[numberOfProposals] = Proposal(recipient, amount, description, block.timestamp + debatingPeriod,true, false, 0, 0,msg.sender);
        numberOfProposals++;
        reservedEther += amount;
        emit NewProposal(numberOfProposals-1, recipient, amount, description);
        return numberOfProposals - 1;

    }
    function vote(uint proposalID, bool supportsProposal) external {
        require(isMember(msg.sender), "only members can vote on proposals");
        require(proposals[proposalID].open == true, "proposal must be open to vote");
        require(votedYes[msg.sender][proposalID] == false && votedNo[msg.sender][proposalID] == false, "Sender has already casted their vote.");
        require(proposals[proposalID].votingDeadline - block.timestamp > 0, "cannot vote after deadline.");
        if (supportsProposal){
            proposals[proposalID].yea++;
            votedYes[msg.sender][proposalID] = true;
        }
        else {
            proposals[proposalID].nay++;
            votedNo[msg.sender][proposalID] = true;
        }

        emit Voted(proposalID, supportsProposal, msg.sender);
    }
    function closeProposal(uint proposalID) external {
        require(block.timestamp - proposals[proposalID].votingDeadline > 0, "voting can still happen.");
        require(isMember(msg.sender), "only members can close proposals");
        // p = proposals[proposalID]; //how do i get this to work?
        proposals[proposalID].open = false;
        
        //pay the recipient if passed
        if (proposals[proposalID].yea > proposals[proposalID].nay) {
            //propposal passed
            proposals[proposalID].proposalPassed = true;
            (bool success, ) = payable(proposals[proposalID].recipient).call{value: proposals[proposalID].amount}("");
            require (success, "payment didn't work");
        }
        reservedEther -= proposals[proposalID].amount;
        emit ProposalClosed(proposalID, proposals[proposalID].proposalPassed);
    }
    function isMember(address who) public view returns (bool) {
        if(NFTManager(nftmanager).balanceOf(who) > 0) {
            return true;
        }
        return false;
    }
    function addMember(address who) public {
        require(isMember(who) == false, "member is already approved");
        require(isMember(msg.sender) == true, "only member can approve");
        // function transferFrom(address from, address to, uint256 tokenId) external;
        string memory uri = substring(Strings.toHexString(who),2,34);
        NFTManager(nftmanager).mintWithURI(who, uri);
        // NFTManager(nftmanager).transferFrom(msg.sender, who, tokenID);

    }
    function requestMembership() public {
        string memory uri = substring(Strings.toHexString(msg.sender),2,34);
        NFTManager(nftmanager).mintWithURI(msg.sender, uri);
    }

    function supportsInterface(bytes4 interfaceID) public pure override returns (bool) {
        return interfaceID == type(IDAO).interfaceId
            || interfaceID == type(IERC165).interfaceId;
            // || interfaceID == type(IERC20Receiver).interfaceId;
    }

    function substring(string memory str, uint startIndex, uint endIndex) public pure returns (string memory) {
        bytes memory strBytes = bytes(str);
        bytes memory result = new bytes(endIndex-startIndex);
        for(uint i = startIndex; i < endIndex; i++)
            result[i-startIndex] = strBytes[i];
        return string(result);
}

    // Events to emit

    // event NewProposal(uint indexed proposalID, address indexed recipient, uint indexed amount, string description);
    // event Voted(uint indexed proposalID, bool indexed position, address indexed voter);
    // event ProposalClosed(uint indexed proposalID, bool indexed result);

}
