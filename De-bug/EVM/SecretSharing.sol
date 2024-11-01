// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EncryptedDataStorage {
    // Mapping of user address to encrypted data
    mapping(address => string) private encryptedData;
    
    // Mapping of user address to permitted viewer
    mapping(address => address) private permittedViewer;

    // Event to emit when data is stored
    event DataStored(address indexed user, address indexed viewer);

    // Function to store encrypted data and specify the viewer address
    function storeEncryptedData(string memory _encryptedData, address _viewer) external {
        require(_viewer != address(0), "Invalid viewer address");

        // Store the encrypted data for the sender
        encryptedData[msg.sender] = _encryptedData;

        // Set the specified viewer who can access this data
        permittedViewer[msg.sender] = _viewer;

        emit DataStored(msg.sender, _viewer);
    }

    // Function to retrieve the encrypted data if caller is the permitted viewer
    function retrieveEncryptedData(address _dataOwner) external view returns (string memory) {
        require(permittedViewer[_dataOwner] == msg.sender, "Not authorized to view this data");

        return encryptedData[_dataOwner];
    }
}
