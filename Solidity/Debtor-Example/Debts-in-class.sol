// SPDX-License-Identifier : GPL-3.0-or-later
pragma solidity ^0.8.17;

contract Debts {

    struct Entry {
        uint id;
        string thealias;
        string name;
        address addr;
        int balance;
    }

    event paidEvent();

    event aliasAddedEvent();

    mapping (uint => Entry) public entries;

    uint public num_entries;

    mapping (string => uint) public findByAlias;

    mapping (address => uint) public findByAddress;

    mapping (address => bool) public addressHasEntry;

    mapping (string => bool) public aliasHasEntry;

    constructor() {

    }

    function addAlias (string memory _alias, string memory _name) public {
        require(!aliasHasEntry[_alias], "string entry name already exists");
        require(!addressHasEntry[msg.sender], "your address already has an alias");

        aliasHasEntry[_alias] = true;
        addressHasEntry[msg.sender] = true;

        findByAlias[_alias] = num_entries;

        findByAddress[msg.sender] = num_entries;

        entries[num_entries] = Entry(num_entries, _alias, _name, msg.sender,0);
        num_entries++;
        emit aliasAddedEvent();


    }

    function payToAlias (string memory _alias, int amount) public {

        require (amount >= -100 && amount <= 100, "Amounts must be between -100 and 100");
        require (amount != 0, "amount cannot be zero");
        require(addressHasEntry[msg.sender], "your address does not have an alias");
        require(aliasHasEntry[_alias], "string entry name does not exist");

        uint from = findByAddress[msg.sender];
        uint to = findByAlias[_alias];

        require(entries[to].addr != msg.sender, "you cannot enter a debt to yourself");

         entries[from].balance += amount;
         entries[to].balance -= amount;

         emit paidEvent();


    }

}