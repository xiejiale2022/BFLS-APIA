// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract FLManager {
    struct Organization {
        address server;
        address[] devices;
        bool registered;
    }
    
    struct GlobalModel {
        uint256 round;
        bytes parameters;
    }
    
    address public initiator;
    uint256 public currentRound;
    uint256 public totalRounds;
    uint256 public localEpochs;
    
    GlobalModel public globalModel;
    mapping(address => Organization) public organizations;
    mapping(uint256 => mapping(address => bytes)) public localModels;
    
    event TrainingStarted(uint256 totalRounds, uint256 localEpochs);
    event ModelUploaded(address indexed uploader, uint256 round);
    event GlobalModelUpdated(uint256 round, bytes parameters);
    
    modifier onlyInitiator() {
        require(msg.sender == initiator, "Only initiator can call");
        _;
    }
    
    modifier onlyServer() {
        require(organizations[msg.sender].registered, "Only edge server can call");
        _;
    }
    
    constructor(uint256 _totalRounds, uint256 _localEpochs) public {
        initiator = msg.sender;
        totalRounds = _totalRounds;
        localEpochs = _localEpochs;
        currentRound = 0;
        
        emit TrainingStarted(_totalRounds, _localEpochs);
    }
    
    function registerOrganization(
        address server,
        address[] memory devices
    ) public onlyInitiator {
        organizations[server] = Organization({
            server: server,
            devices: devices,
            registered: true
        });
    }
    
    function uploadLocalModel(bytes memory encryptedModel) public {
        require(organizations[msg.sender].registered, "Unregistered organization");
        localModels[currentRound][msg.sender] = encryptedModel;
        emit ModelUploaded(msg.sender, currentRound);
    }
    
    function updateGlobalModel(bytes memory parameters) public onlyServer {
        globalModel = GlobalModel({
            round: currentRound,
            parameters: parameters
        });
        currentRound++;
        emit GlobalModelUpdated(currentRound, parameters);
    }
    
    function getGlobalModel() public view returns (bytes memory) {
        return globalModel.parameters;
    }
}
