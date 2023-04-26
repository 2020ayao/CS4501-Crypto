// SPDX-License-Identifier: GPL-3.0-or-later
//Adam Yao aly3ye
pragma solidity ^0.8.17;
import "./IAuctioneer.sol";

contract Auctioneer is IAuctioneer {
    mapping(uint => uint) public override functionTimeLeft;
    // uint256 public override functionTimeLeft;
    // mapping (address => bool) public override tas;

    


    constructor(){

    }
}