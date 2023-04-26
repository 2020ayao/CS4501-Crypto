// SPDX-License-Identifier: GPL-3.0-or-later
//Name: Adam Yao UserID: aly3ye
pragma solidity ^0.8.17;

import "./INFTManager.sol";
import "./ERC721.sol";

contract NFTManager is INFTManager, ERC721 {

    mapping(uint256 => string) private _tokenToURI;
    uint256 public override count;
    string private baseURL = "https://andromeda.cs.virginia.edu/ccc/ipfs/files/";



    constructor() ERC721("Collections(TM)", "COLT") {
        // _safeMint(msg.sender, count);
        // count++;
    }

    function mintWithURI(address _to, string memory _uri) public override returns (uint) {
        for (uint256 key = 0; key < count; key++) {
            require(keccak256(bytes(_tokenToURI[key])) != keccak256(bytes(_uri)), "can't mint duplicate");
        }
        uint256 nft_id = count;
        _safeMint(_to,count);
        _tokenToURI[count] = _uri;
        count++;
        return nft_id;
    }

   function mintWithURI(string memory _uri) public override returns (uint) {
       return mintWithURI(msg.sender, _uri);
   }

    function tokenURI(uint256 tokenId) public view override(ERC721, IERC721Metadata) returns (string memory) {
        require(bytes(_tokenToURI[tokenId]).length > 0, "tokenID was not valid.");

        return concat(baseURL, _tokenToURI[tokenId]);

   }


    function supportsInterface(bytes4 interfaceId) public view virtual override(IERC165,ERC721) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(INFTManager).interfaceId;
    }

    function concat(string memory a, string memory b) public pure returns (string memory) {
        return string(abi.encodePacked(a, b));
    }
    
}
    