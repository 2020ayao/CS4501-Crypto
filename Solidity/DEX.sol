// SPDX-License-Identifier: GPL-3.0-or-later
//Name: Adam Yao UserID: aly3ye
pragma solidity ^0.8.17;

import "./IDEX.sol";
import "./ERC20.sol";
import "./IERC20Receiver.sol";
import "./ITokenCC.sol";



contract DEX is IDEX {

    constructor() {
        _deployer = msg.sender;
    }
    address internal _deployer;
    bool internal _adjustingLiquidity = false;
    bool internal _poolIsCreated = false;

    // function decimals() external view returns (uint);
    uint public override decimals;

    uint internal limit = 0;

    // function symbol() external view returns (string memory);
    string public override symbol;

    // function getEtherPrice() external view returns (uint);
    function getEtherPrice() external view returns (uint) {
        return IEtherPriceOracle(etherPricer).price();
    }

    // function k() external view returns (uint);
    uint public override k;

    // function x() external view returns (uint);
    uint public override x;

    // function y() external view returns (uint);
    uint public override y;

    function getPoolLiquidityInUSDCents() external view returns (uint) {
        return x * IEtherPriceOracle(etherPricer).price() * 2;
    }

    address public override etherPricer;

    address public override erc20Address;

    // function etherLiquidityForAddress(address who) external view returns (uint);
    mapping(address => uint) public etherLiquidityForAddress;

    // function tokenLiquidityForAddress(address who) external view returns (uint);
    mapping(address => uint) public tokenLiquidityForAddress;

    // function feeNumerator() external view returns (uint);
    uint public override feeNumerator;

    // function feeDenominator() external view returns (uint);
    uint public override feeDenominator;

    // function feesEther() external view returns (uint);
    uint public override feesEther;

    // function feesToken() external view returns (uint);
    uint public override feesToken;

    
    function setEtherPricer(address p) external {
        etherPricer = p;
    }

    function getTokenPrice() external view returns (uint) {
        return this.getEtherPrice() * y/x;
    }

    // 0: the address of *this* DEX contract (address)
    // 1: token cryptocurrency abbreviation (string memory)
    // 2: token cryptocurrency name (string memory)
    // 3: ERC-20 token cryptocurrency address (address)
    // 4: k (uint)
    // 5: ether liquidity (uint)
    // 6: token liquidity (uint)
    // 7: fee numerator (uint)
    // 8: fee denominator (uint)
    // 9: token decimals (uint)
    // 10: fees collected in ether (uint)
    // 11: fees collected in the token CC (uint)
    function getDEXinfo() public view returns (address, string memory, string memory, 
                            address, uint, uint, uint, uint, uint, uint, uint, uint) {
                                return (address(this), symbol, ERC20(erc20Address).name(),erc20Address, k, x, y, feeNumerator, feeDenominator,decimals, feesEther, feesToken);
                            }


    function reset() public pure { 
        revert();
    }

    

    

    function supportsInterface(bytes4 interfaceID) public pure override returns (bool) {
        return interfaceID == type(IDEX).interfaceId
            || interfaceID == type(IERC165).interfaceId
            || interfaceID == type(IERC20Receiver).interfaceId;
    }


    // This can be called exactly once, and creates the pool; only the
    // deployer of the contract call this.  Some amount of ETH is passed in
    // along with this call.  For purposes of this assignment, the ratio is
    // then defined based on the amount of ETH paid with this call and the
    // amount of the token cryptocurrency stated in the first parameter.  The
    // first parameter is how many of the token cryptocurrency (with all the
    // decimals) to add to the pool; the ERC-20 contract that manages that
    // token cryptocurrency is the fourth parameter (the caller needs to
    // approve this contract for that much of the token cryptocurrency before
    // the call).  The second and third parameters define the fraction --
    // 0.1% would be 1 and 1000, for example.  The last parameter is the
    // contract address of the EtherPricer contract being used, and can be
    // updated later via the setEtherPricer() function.


    function createPool(uint _tokenAmount, uint _feeNumerator, uint _feeDenominator, 
        address _erc20token, address _etherPricer) external payable override {
            require(_poolIsCreated == false, "DEX can only be created once");
            require(_deployer == msg.sender, "Only deployer can createPool");
            erc20Address = _erc20token;
            decimals = ERC20(_erc20token).decimals();
            
            x = msg.value;
            y = _tokenAmount;
            
            feeNumerator = _feeNumerator;
            feeDenominator = _feeDenominator;
            symbol = ERC20(_erc20token).symbol();
            feesEther = 0;
            feesToken = 0;


            k = x * y;

            IERC20(erc20Address).transferFrom(msg.sender, address(this), _tokenAmount);
            etherPricer = _etherPricer;
            

            etherLiquidityForAddress[msg.sender] += x;
            tokenLiquidityForAddress[msg.sender] += y;

            emit liquidityChangeEvent();

            _poolIsCreated = true;

  
        }

    function addLiquidity() external payable {
        uint tokenAmount = msg.value * y/x;

        x += msg.value; 
        y += tokenAmount;
        k = x * y;
        _adjustingLiquidity = true;
        ERC20(erc20Address).transferFrom(msg.sender, address(this), tokenAmount);
        _adjustingLiquidity = false;

        etherLiquidityForAddress[msg.sender] += msg.value;
        tokenLiquidityForAddress[msg.sender] += tokenAmount;
        

        emit liquidityChangeEvent();
    }


    function removeLiquidity(uint amountEther) external {
        uint tokenAmount = amountEther * y/x;

        require(amountEther >= etherLiquidityForAddress[msg.sender], "not enought ether to withdraw");

        x -= amountEther;
        y -= tokenAmount;
        k = x * y;
        _adjustingLiquidity = true;
        ERC20(erc20Address).transfer(erc20Address, tokenAmount);
        _adjustingLiquidity = false;

        etherLiquidityForAddress[msg.sender] -= amountEther;
        tokenLiquidityForAddress[msg.sender] -= tokenAmount;


        emit liquidityChangeEvent();
    }

    receive() external payable {   
        require(_poolIsCreated == true, "pool hasn't been created yet");
        require(_adjustingLiquidity == false, "Selective stopping.");

        uint old_y = y;
        x += msg.value;
        y = k/x;
        uint payout = old_y - y;
        feesToken += payout * feeNumerator/feeDenominator;
        // ERC20(erc20Address).transfer(msg.sender, payout-feeNumerator/feeDenominator * payout);
        // (bool success, ) = payable(msg.sender).call{value: payout-feesToken}("");
        // require (success, "payment didn't work");
        emit liquidityChangeEvent();
    }

    function onERC20Received(address from, uint amount, address erc20) external returns (bool) {
        require(_poolIsCreated == true, "pool hasn't been created yet");
        require(_adjustingLiquidity == false, "Selective stopping.");
        require(erc20==erc20Address,"no scams today");
        
        uint old_x = x;
        y += amount;
        x = k/y;
        uint payout = old_x - x;
        feesEther += payout * feeNumerator/feeDenominator;

        (bool success, ) = payable(from).call{value: payout - feeNumerator/feeDenominator * payout}("");
        require (success, "payment didn't work");
        emit liquidityChangeEvent();
        return success;
    }


}