// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract KeyManager {
    struct PublicKey {
        bytes32 x;
        bytes32 y;
    }
    
    mapping(address => PublicKey) public publicKeys;
    mapping(address => mapping(address => bytes)) public encryptedKeyShares;
    
    event PublicKeyRegistered(address indexed owner, bytes32 x, bytes32 y);
    event KeyShareUploaded(address indexed owner, address indexed device, bytes encryptedShare);
    
    function registerPublicKey(bytes32 x, bytes32 y) public {
        publicKeys[msg.sender] = PublicKey(x, y);
        emit PublicKeyRegistered(msg.sender, x, y);
    }
    
    function uploadKeyShare(address device, bytes memory encryptedShare) public {
        encryptedKeyShares[msg.sender][device] = encryptedShare;
        emit KeyShareUploaded(msg.sender, device, encryptedShare);
    }
    
    function getPublicKey(address owner) public view returns (bytes32, bytes32) {
        PublicKey memory pk = publicKeys[owner];
        return (pk.x, pk.y);
    }
    
    function getKeyShare(address owner, address device) public view returns (bytes memory) {
        return encryptedKeyShares[owner][device];
    }
}
