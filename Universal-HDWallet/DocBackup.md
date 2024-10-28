# Project Structure
.
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── wallet.rs
│   ├── types.rs
│   └── error.rs

# Cargo.toml
[package]
name = "evm-wallet"
version = "0.1.0"
edition = "2021"

[dependencies]
tiny-bip39 = "1.0.0"
ethereum-types = "0.14.1"
web3 = "0.19.0"
secp256k1 = "0.27.0"
hex = "0.4.3"
tiny-keccak = "2.0.2"
anyhow = "1.0"
tokio = { version = "1.0", features = ["full"] }
eth-keystore = "0.5.0"
ethereum-tx-sign = "6.1.2"
primitive-types = "0.12.1"
thiserror = "1.0"

# src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum WalletError {
    #[error("Invalid mnemonic: {0}")]
    InvalidMnemonic(String),

    #[error("Web3 error: {0}")]
    Web3Error(#[from] web3::Error),

    #[error("Invalid private key: {0}")]
    InvalidPrivateKey(String),

    #[error("Transaction error: {0}")]
    TransactionError(String),

    #[error("Connection error: {0}")]
    ConnectionError(String),
}

pub type Result<T> = std::result::Result<T, WalletError>;

# src/types.rs
use ethereum_types::{Address, U256};
use web3::types::H256;

#[derive(Debug)]
pub struct TransactionInfo {
    pub hash: H256,
    pub from: Address,
    pub to: Address,
    pub value: U256,
    pub gas_used: U256,
    pub gas_price: U256,
}

#[derive(Debug)]
pub struct TokenInfo {
    pub address: Address,
    pub symbol: String,
    pub decimals: u8,
}

# src/wallet.rs
use crate::error::{Result, WalletError};
use crate::types::{TransactionInfo, TokenInfo};
use ethereum_types::{Address, U256};
use hex::ToHex;
use secp256k1::{SecretKey, PublicKey};
use tiny_bip39::{Mnemonic, Language, MnemonicType};
use tiny_keccak::{Keccak, Hasher};
use web3::{
    Web3,
    transports::Http,
    types::{TransactionParameters, H256},
};

pub struct EVMWallet {
    mnemonic: String,
    web3: Web3<Http>,
}

impl EVMWallet {
    pub fn new(node_url: &str) -> Result<Self> {
        let mnemonic = Mnemonic::new(MnemonicType::Words24, Language::English);
        Self::from_mnemonic(mnemonic.phrase(), node_url)
    }

    pub fn from_mnemonic(mnemonic_phrase: &str, node_url: &str) -> Result<Self> {
        let mnemonic = Mnemonic::from_phrase(mnemonic_phrase, Language::English)
            .map_err(|e| WalletError::InvalidMnemonic(e.to_string()))?;

        let transport = Http::new(node_url)
            .map_err(|e| WalletError::ConnectionError(e.to_string()))?;
        
        let web3 = Web3::new(transport);

        Ok(Self {
            mnemonic: mnemonic_phrase.to_string(),
            web3,
        })
    }

    pub fn mnemonic(&self) -> &str {
        &self.mnemonic
    }

    fn derive_private_key(&self, account_index: u32) -> Result<SecretKey> {
        let mnemonic = Mnemonic::from_phrase(&self.mnemonic, Language::English)
            .map_err(|e| WalletError::InvalidMnemonic(e.to_string()))?;
        let seed = mnemonic.to_seed("");
        
        let mut hasher = Keccak::v256();
        hasher.update(&seed);
        let mut result = [0u8; 32];
        hasher.finalize(&mut result);
        
        SecretKey::from_slice(&result)
            .map_err(|e| WalletError::InvalidPrivateKey(e.to_string()))
    }

    pub fn generate_address(&self, account_index: u32) -> Result<Address> {
        let secp = secp256k1::Secp256k1::new();
        let private_key = self.derive_private_key(account_index)?;
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        
        let public_key = &public_key.serialize_uncompressed()[1..];
        
        let mut hasher = Keccak::v256();
        hasher.update(public_key);
        let mut result = [0u8; 32];
        hasher.finalize(&mut result);
        
        Ok(Address::from_slice(&result[12..]))
    }

    pub fn generate_addresses(&self, count: u32) -> Result<Vec<Address>> {
        let mut addresses = Vec::with_capacity(count as usize);
        for i in 0..count {
            addresses.push(self.generate_address(i)?);
        }
        Ok(addresses)
    }

    pub async fn get_eth_balance(&self, address: Address) -> Result<U256> {
        self.web3.eth().balance(address, None)
            .await
            .map_err(WalletError::Web3Error)
    }

    pub async fn get_token_balance(&self, token: &TokenInfo, owner_address: Address) -> Result<U256> {
        let data = hex::decode("70a08231000000000000000000000000")
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;
        let mut full_data = data.clone();
        full_data.extend_from_slice(&owner_address.as_bytes()[..]);

        let result = self.web3.eth().call(
            web3::types::CallRequest {
                to: Some(token.address),
                data: Some(web3::types::Bytes(full_data)),
                ..Default::default()
            },
            None
        ).await.map_err(WalletError::Web3Error)?;

        Ok(U256::from_big_endian(&result.0))
    }

    pub async fn send_eth(
        &self,
        from_account_index: u32,
        to_address: Address,
        amount_wei: U256,
        gas_price: Option<U256>,
    ) -> Result<TransactionInfo> {
        let private_key = self.derive_private_key(from_account_index)?;
        let from_address = self.generate_address(from_account_index)?;
        
        let nonce = self.web3.eth().transaction_count(from_address, None)
            .await
            .map_err(WalletError::Web3Error)?;
        let gas_price = match gas_price {
            Some(price) => price,
            None => self.web3.eth().gas_price().await.map_err(WalletError::Web3Error)?,
        };

        let transaction = TransactionParameters {
            nonce: Some(nonce),
            to: Some(to_address),
            value: amount_wei,
            gas_price: Some(gas_price),
            gas: U256::from(21000),
            data: vec![].into(),
            ..Default::default()
        };

        let signed = self.web3.accounts()
            .sign_transaction(transaction.clone(), &private_key.to_string())
            .await
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;
        
        let tx_hash = self.web3.eth()
            .send_raw_transaction(signed.raw_transaction)
            .await
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;

        Ok(TransactionInfo {
            hash: tx_hash,
            from: from_address,
            to: to_address,
            value: amount_wei,
            gas_used: U256::from(21000),
            gas_price,
        })
    }

    pub async fn send_token(
        &self,
        token: &TokenInfo,
        from_account_index: u32,
        to_address: Address,
        amount: U256,
        gas_price: Option<U256>,
    ) -> Result<TransactionInfo> {
        let private_key = self.derive_private_key(from_account_index)?;
        let from_address = self.generate_address(from_account_index)?;

        let mut data = hex::decode("a9059cbb000000000000000000000000")
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;
        data.extend_from_slice(&to_address.as_bytes()[..]);
        data.extend_from_slice(&[0u8; 32]);
        let mut amount_bytes = [0u8; 32];
        amount.to_big_endian(&mut amount_bytes);
        data.extend_from_slice(&amount_bytes);

        let nonce = self.web3.eth().transaction_count(from_address, None)
            .await
            .map_err(WalletError::Web3Error)?;
        let gas_price = match gas_price {
            Some(price) => price,
            None => self.web3.eth().gas_price().await.map_err(WalletError::Web3Error)?,
        };

        let gas = self.web3.eth().estimate_gas(
            web3::types::CallRequest {
                from: Some(from_address),
                to: Some(token.address),
                data: Some(data.clone().into()),
                ..Default::default()
            },
            None
        ).await.map_err(WalletError::Web3Error)?;

        let transaction = TransactionParameters {
            nonce: Some(nonce),
            to: Some(token.address),
            value: U256::zero(),
            gas_price: Some(gas_price),
            gas,
            data: data.into(),
            ..Default::default()
        };

        let signed = self.web3.accounts()
            .sign_transaction(transaction.clone(), &private_key.to_string())
            .await
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;
        
        let tx_hash = self.web3.eth()
            .send_raw_transaction(signed.raw_transaction)
            .await
            .map_err(|e| WalletError::TransactionError(e.to_string()))?;

        Ok(TransactionInfo {
            hash: tx_hash,
            from: from_address,
            to: to_address,
            value: amount,
            gas_used: gas,
            gas_price,
        })
    }
}

# src/lib.rs
mod error;
mod types;
mod wallet;

pub use error::{Result, WalletError};
pub use types::{TransactionInfo, TokenInfo};
pub use wallet::EVMWallet;

# src/main.rs
use evm_wallet::{EVMWallet, TokenInfo, Result};
use ethereum_types::{Address, U256};
use std::str::FromStr;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize wallet with your Ethereum node URL
    let wallet = EVMWallet::new("https://mainnet.infura.io/v3/YOUR-PROJECT-ID")?;
    println!("Mnemonic: {}", wallet.mnemonic());

    // Generate 5 addresses
    let addresses = wallet.generate_addresses(5)?;
    println!("\nGenerated addresses:");
    for (i, address) in addresses.iter().enumerate() {
        println!("Address {}: {:#x}", i, address);
        
        // Get ETH balance
        let balance = wallet.get_eth_balance(*address).await?;
        println!("ETH Balance: {} wei", balance);
    }

    // Example token (USDC on Ethereum mainnet)
    let token = TokenInfo {
        address: Address::from_str("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48").unwrap(),
        symbol: "USDC".to_string(),
        decimals: 6,
    };
    
    // Get token balance
    let token_balance = wallet.get_token_balance(&token, addresses[0]).await?;
    println!("Token Balance: {}", token_balance);

    // Example: Send ETH
    let to_address = Address::from_str("0x742d35Cc6634C0532925a3b844Bc454e4438f44e").unwrap();
    let amount = U256::from(1000000000000000000u64); // 1 ETH
    let tx_info = wallet.send_eth(0, to_address, amount, None).await?;
    println!("ETH Transaction Hash: {:#x}", tx_info.hash);

    // Example: Send Tokens
    let token_amount = U256::from(1000000u64); // Amount depends on token decimals
    let token_tx_info = wallet.send_token(&token, 0, to_address, token_amount, None).await?;
    println!("Token Transaction Hash: {:#x}", token_tx_info.hash);

    Ok(())
}