# Encrypted Storage Smart Contract

A Solidity smart contract that enables secure storage and retrieval of encrypted data on the Ethereum blockchain. This contract allows users to store encrypted information that can only be accessed by specifically designated wallet addresses.

## Features

- Store encrypted data with designated decrypter addresses
- Secure access control for data retrieval
- Gas-efficient data storage using bytes32
- Event tracking for data storage and access
- View functions for gas-free data checks
- Custom error messages for better gas efficiency

## Smart Contract Overview

### Storage Structure

```solidity
struct EncryptedData {
    bytes32 encryptedContent;    // The encrypted data
    address allowedDecrypter;    // Address allowed to decrypt
    bool exists;                 // Existence flag
}
```

### Main Functions

1. `storeEncryptedData(bytes32 dataId, bytes32 encryptedContent, address allowedDecrypter)`
   - Stores encrypted data with a specified decrypter address
   - Emits `DataStored` event

2. `retrieveEncryptedData(bytes32 dataId)`
   - Retrieves encrypted data (requires authorized address)
   - Emits `DataAccessed` event
   - Costs gas due to event emission

3. `viewEncryptedData(bytes32 dataId)`
   - Gas-free view function to read encrypted data
   - No event emission
   - Requires authorized address

4. `isAuthorizedForData(bytes32 dataId)`
   - Checks if caller is authorized to access data
   - View function (gas-free)

5. `dataExists(bytes32 dataId)`
   - Checks if data exists for given ID
   - View function (gas-free)

### Events

- `DataStored(bytes32 indexed dataId, address indexed owner, address indexed allowedDecrypter)`
- `DataAccessed(bytes32 indexed dataId, address indexed accessor)`

### Error Messages

- `Unauthorized()`: Caller not authorized to access data
- `DataNotFound()`: Requested data doesn't exist
- `InvalidInput()`: Invalid input parameters

## Usage

### Prerequisites

- Solidity ^0.8.0
- Ethereum development environment (Hardhat, Truffle, or similar)
- Web3.js or Ethers.js library

### Deployment

1. Deploy the contract to your chosen Ethereum network:
```bash
npx hardhat deploy --network <your-network>
```

### Integration Example

```javascript
// 1. Import necessary libraries and contract ABI
const { ethers } = require('ethers');
const EncryptedStorage = require('./artifacts/EncryptedStorage.json');

// 2. Connect to contract
const contract = new ethers.Contract(
    contractAddress,
    EncryptedStorage.abi,
    signer
);

// 3. Store encrypted data
const dataId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("uniqueIdentifier"));
const encryptedContent = "0x..."; // Your encrypted data in bytes32 format
const decrypterAddress = "0x..."; // Address allowed to decrypt

await contract.storeEncryptedData(dataId, encryptedContent, decrypterAddress);

// 4. Retrieve data (must be called from decrypter address)
const data = await contract.retrieveEncryptedData(dataId);

// 5. View data without emitting events (gas-free)
const viewedData = await contract.viewEncryptedData(dataId);
```

// 1. Using user address + timestamp
const dataId = ethers.utils.keccak256(
    ethers.utils.solidityPack(
        ['address', 'uint256'],
        [userAddress, Date.now()]
    )
);

// 2. Using user address + document type + counter
const dataId = ethers.utils.keccak256(
    ethers.utils.solidityPack(
        ['address', 'string', 'uint256'],
        [userAddress, 'medical_record', 1]
    )
);

// 3. Using multiple parameters
const dataId = ethers.utils.keccak256(
    ethers.utils.solidityPack(
        ['address', 'string', 'uint256', 'string'],
        [senderAddress, documentType, version, metadata]
    )
);

## Security Considerations

1. **Off-chain Encryption**: This contract only stores encrypted data. All encryption/decryption must be performed off-chain.
2. **Access Control**: Only the designated decrypter address can access the encrypted data.
3. **Data Privacy**: While the data is encrypted, it's still visible on the blockchain. Ensure sensitive data is properly encrypted before storage.
4. **Gas Costs**: Use `viewEncryptedData` instead of `retrieveEncryptedData` when event emission isn't needed to save gas.

## Testing

Run the test suite:
```bash
npx hardhat test
```

Example test cases should cover:
- Storing encrypted data
- Retrieving data with authorized address
- Attempting unauthorized access
- Checking data existence
- Event emission verification

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/Feature`)
3. Commit your changes (`git commit -m 'Add some Feature'`)
4. Push to the branch (`git push origin feature/Feature`)
5. Open a Pull Request
