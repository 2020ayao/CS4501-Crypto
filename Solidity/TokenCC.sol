// SPDX-License-Identifier: GPL-3.0-or-later
//Name: Adam Yao UserID: aly3ye
pragma solidity ^0.8.17;

import "./ITokenCC.sol";
import "./ERC20.sol";
import "./IERC20Receiver.sol";


contract TokenCC is ITokenCC, ERC20 {

    constructor() ERC20("AugustaCoin(TM)", "AUG") {
        _mint(msg.sender, 1000 * (10 ** 10));
    }

    function requestFunds() public pure override {
        revert();
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(IERC20).interfaceId ||
            interfaceId == type(IERC20Metadata).interfaceId ||
            interfaceId == type(ITokenCC).interfaceId;
    }

    function decimals() public pure override (ERC20, IERC20Metadata) returns(uint8) {
        return 10;
    }

    function _afterTokenTransfer(address from, address to, uint256 amount) internal override {
    if ( to.code.length > 0  && from != address(0) && to != address(0) ) {
        // token recipient is a contract, notify them
        try IERC20Receiver(to).onERC20Received(from, amount, address(this)) returns (bool success) {
            require(success,"ERC-20 receipt rejected by destination of transfer");
        } catch {
            // the notification failed (maybe they don't implement the `IERC20Receiver` interface?)
            // we choose to ignore this case
        }
    }
}
}


