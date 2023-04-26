// SPDX-License-Identifier: GPL-3.0-or-later
//Adam Yao aly3ye
pragma solidity ^0.8.17;
import "./IAuctioneer.sol";
import "./NFTManager.sol";

contract Auctioneer is IAuctioneer {

//     struct Auction {
//     uint id;            // the auction id
//     uint num_bids;      // how many bids have been placed
//     string data;        // a text description of the auction or NFT data
//     uint highestBid;    // the current highest bid, in wei
//     address winner;     // the current highest bidder
//     address initiator;  // who started the auction
//     uint nftid;         // the NFT token ID
//     uint endTime;       // when the auction ends
//     bool active;        // if the function is active
// }

    mapping(uint => Auction) public auctions; // i think this works?
    address public override deployer;
    address public override nftmanager;
    uint public override num_auctions;

    uint public override uncollectedFees;
    uint public override totalFees;


    // The deployer of the contract, and ONLY that address, can collect the
    // fees that this auction contract has accumulated; a call to this by any
    // other address should revert.  This causes the fees to be paid to the
    // deployer.
    function collectFees() public override  {
        require(msg.sender == deployer, "Only Deployer of contract can collect fees.");
        (bool success, ) = payable(deployer).call{value: uncollectedFees}(""); // uncollected fees
        require(success, "Failed to transfer ETH (fees)");

        
        uncollectedFees = 0;
    }


    function closeAuction(uint _id) public override {

        //fill in methods
        require(auctionTimeLeft(_id) == 0, "Auction has not ended and cannot be closed.");

    
        if (auctions[_id].num_bids == 0) {
            NFTManager(nftmanager).transferFrom(address(this),auctions[_id].initiator, _id);
        }
        else {
            NFTManager(nftmanager).transferFrom(address(this), auctions[_id].winner, _id);
            uint winnings = auctions[_id].highestBid - auctions[_id].highestBid / 100;
            (bool success, ) = payable(auctions[_id].initiator).call{value: winnings}(""); // WINNINGS
            require(success, "Failed to transfer ETH");

            uncollectedFees += auctions[_id].highestBid / 100;
            totalFees += auctions[_id].highestBid / 100;

        }
        auctions[_id].active = false;
        emit auctionCloseEvent(_id);
    }



    // The time left (in seconds) for the given auction, the ID of which is
    // passed in as a parameter.  This is a convenience function, since it's
    // much easier to call this rather than get the end time as a UNIX
    // timestamp.
    function auctionTimeLeft(uint id) public view override returns (uint) {
        if (auctions[id].endTime > block.timestamp) {
            return auctions[id].endTime - block.timestamp;
        }
        else {
            return 0;
        }
    }
    


    // When one wants to submit a bid on a NFT; the ID of the auction is
    // passed in as a parameter, and some amount of ETH is transferred with
    // this function call.  So many sanity checks here!  See the homework
    // description some of various cases where this function should revert;
    // you get to figure out the rest.  On a successful higher bid, it should
    // update the auction struct.  Be sure to refund the previous higher
    // bidder, since they have now been outbid.
    function placeBid(uint id) payable external {

        require(auctionTimeLeft(id) > 0, "Auction has ended already.");
        require(auctions[id].active == true, "Auction is inactive.");
        require(auctions[id].highestBid < msg.value, "Amount is not greater than highest bid currently.");
        
        if (auctions[id].num_bids > 0) { // if someone got outbid
            address prev_winner_addr = auctions[id].winner;
            uint refund_amount = auctions[id].highestBid;
            (bool success, ) = payable(prev_winner_addr).call{value: refund_amount}("");
            require(success, "Failed to transfer ETH back to prev bidder");
        }
        
        // uint oldHighest = auctions[id].highestBid;


        auctions[id].winner = msg.sender;
        auctions[id].highestBid = msg.value;
        auctions[id].num_bids++;

        // uncollectedFees += auctions[id].highestBid/100;
        // totalFees += auctions[id].highestBid/100;
        // if (auctions[id].num_bids > 0) // we don't wanna accumulate the fees between bids, only the highest winning bid but also from different auctions
        // {

        //     uncollectedFees -= oldHighest/100;
        //     totalFees -= oldHighest/100;
        // }
        
        emit higherBidEvent(id);

    }

    function startAuction(uint m, uint h, uint d, string memory data, uint reserve, uint nftid) public override returns (uint) {
        require(m > 0 || h > 0 || d > 0, "Invalid auction duration");
        require(bytes(data).length > 0, "Invalid data");
        require(nftmanager!= address(0), "Invalid NFT Manager address");

        // Verify that no auction with that NFT ID is running
        for (uint i = 0; i < num_auctions; i++) {
            require(auctions[i].nftid != nftid, "Auction already in progress");
        }

        // Transfer the NFT over to this contract
        // NFTManager nm = NFTManager(nftmanager);
        require(NFTManager(nftmanager).ownerOf(nftid) == msg.sender, "You don't own this NFT");
        NFTManager(nftmanager).transferFrom(msg.sender, address(this), nftid);

        // Create the Auction struct
        uint endTime = block.timestamp + (m * 60) + (h * 3600) + (d * 86400);

        auctions[num_auctions] = Auction(num_auctions, 0, data, reserve, msg.sender, msg.sender, nftid, endTime, true);
        num_auctions++;

        emit auctionStartEvent(nftid);

        return num_auctions-1;
    }


    constructor(){
        deployer = msg.sender;
        nftmanager = address(new NFTManager());

    }

    function supportsInterface(bytes4 interfaceID) public pure override returns (bool) {
        return interfaceID == type(IERC165).interfaceId
            || interfaceID == type(IAuctioneer).interfaceId;
    }
}