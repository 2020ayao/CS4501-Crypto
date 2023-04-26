// SPDX-License-Identifier: GPL-3.0-or-later

// This file is part of the http://github.com/aaronbloomfield/ccc repository,
// and is released under the GPL 3.0 license.

pragma solidity ^0.8.17;

import "./DEX.sol";
import "./TokenCC.sol";
import "./EtherPriceOracleConstant.sol";
import "./IERC20Receiver.sol";

// See the homework description for how to use this program

contract DEXtest is IERC20Receiver {

    TokenCC public tc;
    DEX public dex;

    constructor() {
        tc = new TokenCC();
        dex = new DEX();
    }

    function onERC20Received(address from, uint amount, address erc20) external returns (bool) {
        // implement as needed; you have to put code in here if you transfer
        // TCC to this contract
    }

    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len;
        while (_i != 0) {
            k = k-1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }

	function test() public payable {
 		require (msg.value == 13 ether, "Must call test() with 13 ether");

        // Step 1: deploy the ether price oracle
        IEtherPriceOracle pricer = new EtherPriceOracleConstant();

        // Step 1 tests: DEX is deployed
        require(dex.k() == 0, "k value not 0 after DEX creation()");
        require(dex.x() == 0, "x value not 0 after DEX creation()");
        require(dex.y() == 0, "y value not 0 after DEX creation()");

        // Step 2: createPool() is called with 10 (fake) ETH and 100 TC
        bool success = tc.approve(address(dex),100*10**tc.decimals());
        require (success,"Failed to approve TC before createPool()");
        try dex.createPool{value: 10 ether}(100*10**tc.decimals(), 0, 1000, address(tc), address(pricer)) {
            // do nothing
        } catch Error(string memory reason) {
            require (false, string.concat("createPool() call reverted: ",reason));
        }
        
        // Step 2 tests
        // require(dex.k() == 1e21 * 10**tc.decimals(), "k value not correct after createPool()");
        require(dex.k() == 1e21 * 10**tc.decimals(), string.concat("k value not correct after createPool()", uint2str(dex.k()), uint2str(dex.x()), uint2str(dex.y())));
        require(dex.x() == 10 * 1e18, string.concat("x value not correct after createPool() ", uint2str(dex.k()), uint2str(dex.x()), uint2str(dex.y())));
        require(dex.y() == 100 * 10**tc.decimals(), string.concat("y value not correct after createPool()", uint2str(dex.k()), uint2str(dex.x()), uint2str(dex.y())));

        // Step 3: transaction 1, where 2.5 ETH is provided to the DEX for exchange
        (success, ) = payable(dex).call{value: 2500000000000000000}("");
        // require(success, "Failed to transfer ETH.");

        // // Step 3 tests
        require(dex.k() == 1e21 * 10**tc.decimals(), string.concat("k value not correct after Transaction 1 ", uint2str(dex.k()), uint2str(dex.x()), uint2str(dex.y())));
        require(dex.x() == 125 * 1e17, string.concat("x value not correct after Transaction 1 ", uint2str(dex.x())));
        require(dex.y() == 80 * 10**tc.decimals(), string.concat("y value not correct after Transaction 1 ", uint2str(dex.y())));

        // // Step 4: transaction 2, where 120 TC is provided to the DEX for exchange
        success = tc.transfer(address(dex),120*10**tc.decimals());
        require (success,"Failed to send 120 TC in  Transaction 2");

        // Step 4 tests
        require(dex.k() == 1e21 * 10**tc.decimals(), string.concat("k value not correct after Transaction 2 ", uint2str(dex.k())));
        require(dex.x() == 5 * 10**18, string.concat("x value not correct after Transaction 2 ", uint2str(dex.x())));
        require(dex.y() == 2 * 10**12, string.concat("y value not correct after Transaction 2 ", uint2str(dex.y())));

        // Step 5: addLiquidity() is called with 1 (fake) ETH and 40 TC

        // Step 5 tests

        // finish up
        require(false,"end fail"); // huh?  see why in the homework description!
    }
 
    receive() external payable { } // see note in the HW description

}