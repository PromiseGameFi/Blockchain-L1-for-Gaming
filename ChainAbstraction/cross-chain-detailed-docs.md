# Cross-Chain Protocol: Detailed Technical Documentation

## 1. Core Types and Structures

### ChainError
```rust
#[derive(Debug, Error)]
pub enum ChainError {
    #[error("Chain not supported: {0}")]
    UnsupportedChain(String),
    #[error("Transaction failed: {0}")]
    TransactionError(String),
    #[error("Bridge error: {0}")]
    BridgeError(String),
}

```
- Custom error type for handling chain-specific errors
- Provides detailed error messages for debugging
- Implements standard error traits

### ChainId and Account
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChainId(pub String);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub universal_id: String,
    pub chain_specific_addresses: HashMap<ChainId, String>,
}
```
- `ChainId`: Type-safe identifier for different blockchain networks
- `Account`: Universal account structure that maps chain IDs to addresses
- Uses serialization for data persistence and transfer

### Transaction
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub from: String,
    pub to: String,
    pub amount: u128,
    pub data: Vec<u8>,
}
```
- Generic transaction structure
- Supports both value transfers and contract interactions
- Uses u128 for maximum precision in amount handling

## 2. Core Traits

### ChainAdapter
```rust

```
**Purpose**: 
- Defines standard interface for chain interactions
- Enables pluggable support for different blockchains
- Handles basic blockchain operations

**Methods**:
- `send_transaction`: Submits transactions to the blockchain
- `get_balance`: Retrieves account balance
- `get_nonce`: Gets account nonce for transaction ordering

### Bridge
```rust
#[async_trait]
pub trait Bridge {
    async fn transfer(
        &self,
        from_chain: &ChainId,
        to_chain: &ChainId,
        amount: u128,
        recipient: &str,
    ) -> Result<String, ChainError>;
    
    async fn verify_transfer(&self, tx_hash: &str) -> Result<bool, ChainError>;
}
```
**Purpose**:
- Defines interface for cross-chain bridges
- Handles asset transfers between chains
- Provides transfer verification

**Methods**:
- `transfer`: Initiates cross-chain transfers
- `verify_transfer`: Confirms transfer completion

## 3. Universal Account Implementation

### UniversalAccount Structure
```rust
pub struct UniversalAccount {
    account: Account,
    chain_adapters: HashMap<ChainId, Box<dyn ChainAdapter>>,
    bridges: Vec<Box<dyn Bridge>>,
}
```
**Components**:
- `account`: Core account information
- `chain_adapters`: Map of supported chains and their adapters
- `bridges`: Available bridge implementations

### Core Methods
```rust
impl UniversalAccount {
    pub fn new(universal_id: String) -> Self { ... }
    
    pub fn register_chain_adapter(
        &mut self,
        chain_id: ChainId,
        adapter: Box<dyn ChainAdapter>,
        address: String,
    ) { ... }
    
    pub fn register_bridge(&mut self, bridge: Box<dyn Bridge>) { ... }
    
    pub async fn cross_chain_transfer(
        &self,
        from_chain: &ChainId,
        to_chain: &ChainId,
        amount: u128,
        recipient: &str,
    ) -> Result<String, ChainError> { ... }
}
```
**Functionality**:
- Account creation and management
- Chain adapter registration
- Bridge registration
- Cross-chain transfer execution
- Asset management across

## 4. Chain Adapter Implementations

### Ethereum Adapter
```rust
pub struct EthereumAdapter {
    provider_url: String,
}

#[async_trait]
impl ChainAdapter for EthereumAdapter {
    async fn send_transaction(&self, tx: Transaction) -> Result<String, ChainError> { ... }
    async fn get_balance(&self, address: &str) -> Result<u128, ChainError> { ... }
    async fn get_nonce(&self, address: &str) -> Result<u64, ChainError> { ... }
}
```
**Features**:
- Ethereum RPC integration
- Transaction signing and submission
- Balance and nonce management
- Gas estimation and optimization

## 5. Bridge Implementations

### LayerZero Bridge
```rust
pub struct LayerZeroBridge {
    endpoint: String,
}

#[async_trait]
impl Bridge for LayerZeroBridge {
    async fn transfer(
        &self,
        from_chain: &ChainId,
        to_chain: &ChainId,
        amount: u128,
        recipient: &str,
    ) -> Result<String, ChainError> { ... }
    
    async fn verify_transfer(&self, tx_hash: &str) -> Result<bool, ChainError> { ... }
}
```
**Features**:
- LayerZero protocol integration
- Cross-chain message passing
- Transfer verification
- Error handling

## 6. Usage Examples

### Basic Transfer
```rust
pub async fn example_usage() {
    // Create universal account
    let mut universal_account = UniversalAccount::new("user123".to_string());

    // Register Ethereum chain adapter
    let eth_adapter = Box::new(EthereumAdapter {
        provider_url: "https://ethereum.rpc.com".to_string(),
    });
    universal_account.register_chain_adapter(
        ChainId("ethereum".to_string()),
        eth_adapter,
        "0x123...".to_string(),
    );

    // Register bridge
    let bridge = Box::new(LayerZeroBridge {
        endpoint: "https://layerzero.endpoint.com".to_string(),
    });
    universal_account.register_bridge(bridge);

    // Perform cross-chain transfer
    let result = universal_account
        .cross_chain_transfer(
            &ChainId("ethereum".to_string()),
            &ChainId("polygon".to_string()),
            1000000,
            "0x456...",
        )
        .await;
}
```

## 7. Feature Flags

The protocol uses Cargo features for optional functionality:

```toml
[features]
default = ["ethereum", "polygon"]
ethereum = []
polygon = []
solana = []
avalanche = []
binance = []

# Optional features
metrics = ["dep:prometheus"]
monitoring = ["dep:opentelemetry"]
```

**Feature Categories**:
1. **Chain Support**:
   - Ethereum (default)
   - Polygon (default)
   - Solana (optional)
   - Avalanche (optional)
   - Binance Smart Chain (optional)

2. **Monitoring**:
   - Prometheus metrics
   - OpenTelemetry integration

## 8. Dependencies Explained

### Core Dependencies
- `tokio`: Async runtime for non-blocking operations
- `async-trait`: Enables async trait methods
- `serde`: Serialization/deserialization
- `thiserror`: Custom error types
- `web3`: Ethereum interaction
- `ethers`: Ethereum toolkit

### Storage Dependencies
- `sqlx`: SQL database interaction
- `redis`: Caching and temporary storage

### Development Dependencies
- `mockall`: Mocking for unit tests
- `wiremock`: HTTP mocking
- `test-log`: Test logging

## 9. Extension Points for New chains

### Adding New Chains
1. Implement `ChainAdapter` trait
2. Add feature flag
3. Create chain-specific types
4. Implement error handling

### Adding New Bridges
1. Implement `Bridge` trait
2. Add bridge-specific configuration
3. Implement verification logic
4. Add error handling

### Custom Features
1. Add feature flag in Cargo.toml
2. Implement conditional compilation
3. Add feature-specific dependencies
4. Update documentation

