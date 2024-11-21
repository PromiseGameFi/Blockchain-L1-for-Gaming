use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

// Core types and errors
#[derive(Debug, Error)]
pub enum ChainError {
    #[error("Chain not supported: {0}")]
    UnsupportedChain(String),
    #[error("Transaction failed: {0}")]
    TransactionError(String),
    #[error("Bridge error: {0}")]
    BridgeError(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChainId(pub String);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub universal_id: String,
    pub chain_specific_addresses: HashMap<ChainId, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub from: String,
    pub to: String,
    pub amount: u128,
    pub data: Vec<u8>,
}

// Core traits defining chain interaction behavior
#[async_trait]
pub trait ChainAdapter {
    async fn send_transaction(&self, tx: Transaction) -> Result<String, ChainError>;
    async fn get_balance(&self, address: &str) -> Result<u128, ChainError>;
    async fn get_nonce(&self, address: &str) -> Result<u64, ChainError>;
}

#[async_trait]
pub trait Bridge {
    async fn transfer(
        &self,
        from_chain: &ChainId,
        to_chain: &ChainId,
        amount: u12,
        recipient: &str,
    ) -> Result<String, ChainError>;
    
    async fn verify_transfer(&self, tx_hash: &str) -> Result<bool, ChainError>;
}

// Universal account manager
pub struct UniversalAccount {
    account: Account,
    chain_adapters: HashMap<ChainId, Box<dyn ChainAdapter>>,
    bridges: Vec<Box<dyn Bridge>>,
}

impl UniversalAccount {
    pub fn new(universal_id: String) -> Self {
        Self {
            account: Account {
                universal_id,
                chain_specific_addresses: HashMap::new(),
            },
            chain_adapters: HashMap::new(),
            bridges: Vec::new(),
        }
    }

    pub fn register_chain_adapter(
        &mut self,
        chain_id: ChainId,
        adapter: Box<dyn ChainAdapter>,
        address: String,
    ) {
        self.account.chain_specific_addresses.insert(chain_id.clone(), address);
        self.chain_adapters.insert(chain_id, adapter);
    }

    pub fn register_bridge(&mut self, bridge: Box<dyn Bridge>) {
        self.bridges.push(bridge);
    }

    pub async fn cross_chain_transfer(
        &self,
        from_chain: &ChainId,
        to_chain: &ChainId,
        amount: u128,
        recipient: &str,
    ) -> Result<String, ChainError> {
        // Find suitable bridge
        let bridge = self.bridges.first().ok_or(ChainError::BridgeError(
            "No bridge available".to_string(),
        ))?;

        // Execute cross-chain transfer
        bridge.transfer(from_chain, to_chain, amount, recipient).await
    }
}

// Example implementation for Ethereum chain adapter
pub struct EthereumAdapter {
    provider_url: String,
}

#[async_trait]
impl ChainAdapter for EthereumAdapter {
    async fn send_transaction(&self, tx: Transaction) -> Result<String, ChainError> {
        // Implementation would use eth_provider to send transaction
        Ok("tx_hash".to_string())
    }

    async fn get_balance(&self, address: &str) -> Result<u128, ChainError> {
        // Implementation would fetch balance from eth_provider
        Ok(100)
    }

    async fn get_nonce(&self, address: &str) -> Result<u64, ChainError> {
        // Implementation would fetch nonce from eth_provider
        Ok(0)
    }
}

// Example implementation for a cross-chain bridge
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
    ) -> Result<String, ChainError> {
        // Implementation would interact with LayerZero contracts
        Ok("bridge_tx_hash".to_string())
    }

    async fn verify_transfer(&self, tx_hash: &str) -> Result<bool, ChainError> {
        // Implementation would verify the bridge transaction
        Ok(true)
    }
}

// Example usage
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

    match result {
        Ok(tx_hash) => println!("Cross-chain transfer successful: {}", tx_hash),
        Err(e) => println!("Cross-chain transfer failed: {}", e),
    }
}