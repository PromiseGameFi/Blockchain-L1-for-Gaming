use anyhow::{anyhow, Result};
use ethereum_types::{Address, U256};
use hex::ToHex;
use secp256k1::{SecretKey, PublicKey};
use tiny_bip39::{Mnemonic, Language, MnemonicType};
use tiny_keccak::{Keccak, Hasher};
use web3::{
    Web3,
    transports::Http,
    types::{TransactionParameters, H160, H256},
};
use std::str::FromStr;

pub struct EVMWallet {
    mnemonic: String,
    web3: Web3<Http>,
}

impl EVMWallet {
    /// Creates a new HD wallet with a randomly generated mnemonic
    pub fn new(node_url: &str) -> Result<Self> {
        let mnemonic = Mnemonic::new(MnemonicType::Words24, Language::English);
        Self::from_mnemonic(mnemonic.phrase(), node_url)
    }

    /// Creates an HD wallet from an existing mnemonic phrase
    pub fn from_mnemonic(mnemonic_phrase: &str, node_url: &str) -> Result<Self> {
        let mnemonic = Mnemonic::from_phrase(mnemonic_phrase, Language::English)
            .map_err(|e| anyhow!("Invalid mnemonic: {}", e))?;

        let transport = Http::new(node_url)
            .map_err(|e| anyhow!("Failed to connect to node: {}", e))?;
        
        let web3 = Web3::new(transport);

        Ok(Self {
            mnemonic: mnemonic_phrase.to_string(),
            web3,
        })
    }

    /// Returns the mnemonic phrase
    pub fn mnemonic(&self) -> &str {
        &self.mnemonic
    }

    /// Derives a private key for a given account index
    fn derive_private_key(&self, account_index: u32) -> Result<SecretKey> {
        let mnemonic = Mnemonic::from_phrase(&self.mnemonic, Language::English)?;
        let seed = mnemonic.to_seed("");
        
        // Derive path following BIP44 for Ethereum: m/44'/60'/0'/0/account_index
        let path = format!("m/44'/60'/0'/0/{}", account_index);
        
        // Note: You'll need to implement proper BIP32 derivation here
        // This is a simplified version for demonstration
        let mut hasher = Keccak::v256();
        hasher.update(&seed);
        let mut result = [0u8; 32];
        hasher.finalize(&mut result);
        
        SecretKey::from_slice(&result)
            .map_err(|e| anyhow!("Failed to derive private key: {}", e))
    }

    /// Generates an Ethereum address from account index
    pub fn generate_address(&self, account_index: u32) -> Result<Address> {
        let secp = secp256k1::Secp256k1::new();
        let private_key = self.derive_private_key(account_index)?;
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        
        // Get public key in uncompressed format and skip the first byte
        let public_key = &public_key.serialize_uncompressed()[1..];
        
        // Generate Keccak-256 hash
        let mut hasher = Keccak::v256();
        hasher.update(public_key);
        let mut result = [0u8; 32];
        hasher.finalize(&mut result);
        
        // Take last 20 bytes as Ethereum address
        let address = Address::from_slice(&result[12..]);
        Ok(address)
    }

    /// Generates multiple Ethereum addresses
    pub fn generate_addresses(&self, count: u32) -> Result<Vec<Address>> {
        let mut addresses = Vec::with_capacity(count as usize);
        for i in 0..count {
            addresses.push(self.generate_address(i)?);
        }
        Ok(addresses)
    }

    /// Get ETH balance for an address
    pub async fn get_eth_balance(&self, address: Address) -> Result<U256> {
        self.web3.eth().balance(address, None)
            .await
            .map_err(|e| anyhow!("Failed to get balance: {}", e))
    }

    /// Get ERC20 token balance
    pub async fn get_token_balance(&self, token_address: Address, owner_address: Address) -> Result<U256> {
        // ERC20 balanceOf function signature
        let data = hex::decode("70a08231000000000000000000000000")
            .unwrap_or_default();
        let mut full_data = data.clone();
        full_data.extend_from_slice(&owner_address.as_bytes()[..]);

        let result = self.web3.eth().call(
            web3::types::CallRequest {
                to: Some(token_address),
                data: Some(web3::types::Bytes(full_data)),
                ..Default::default()
            },
            None
        ).await?;

        Ok(U256::from_big_endian(&result.0))
    }

    /// Send ETH to an address
    pub async fn send_eth(
        &self,
        from_account_index: u32,
        to_address: Address,
        amount_wei: U256,
        gas_price: Option<U256>,
    ) -> Result<H256> {
        let private_key = self.derive_private_key(from_account_index)?;
        let from_address = self.generate_address(from_account_index)?;
        
        let nonce = self.web3.eth().transaction_count(from_address, None).await?;
        let gas_price = match gas_price {
            Some(price) => price,
            None => self.web3.eth().gas_price().await?,
        };

        let transaction = TransactionParameters {
            nonce: Some(nonce),
            to: Some(to_address),
            value: amount_wei,
            gas_price: Some(gas_price),
            gas: U256::from(21000), // Standard ETH transfer gas
            data: vec![].into(),
            ..Default::default()
        };

        // Sign and send transaction
        let signed = self.web3.accounts().sign_transaction(transaction, &private_key.to_string())
            .await?;
        
        self.web3.eth().send_raw_transaction(signed.raw_transaction)
            .await
            .map_err(|e| anyhow!("Failed to send transaction: {}", e))
    }

    /// Send ERC20 tokens
    pub async fn send_token(
        &self,
        token_address: Address,
        from_account_index: u32,
        to_address: Address,
        amount: U256,
        gas_price: Option<U256>,
    ) -> Result<H256> {
        let private_key = self.derive_private_key(from_account_index)?;
        let from_address = self.generate_address(from_account_index)?;

        // Create ERC20 transfer function call data
        let mut data = hex::decode("a9059cbb000000000000000000000000")?; // transfer(address,uint256)
        data.extend_from_slice(&to_address.as_bytes()[..]);
        data.extend_from_slice(&[0u8; 32]); // Padding for amount
        let mut amount_bytes = [0u8; 32];
        amount.to_big_endian(&mut amount_bytes);
        data.extend_from_slice(&amount_bytes);

        let nonce = self.web3.eth().transaction_count(from_address, None).await?;
        let gas_price = match gas_price {
            Some(price) => price,
            None => self.web3.eth().gas_price().await?,
        };

        // Estimate gas for token transfer
        let gas = self.web3.eth().estimate_gas(
            web3::types::CallRequest {
                from: Some(from_address),
                to: Some(token_address),
                data: Some(data.clone().into()),
                ..Default::default()
            },
            None
        ).await?;

        let transaction = TransactionParameters {
            nonce: Some(nonce),
            to: Some(token_address),
            value: U256::zero(),
            gas_price: Some(gas_price),
            gas,
            data: data.into(),
            ..Default::default()
        };

        // Sign and send transaction
        let signed = self.web3.accounts().sign_transaction(transaction, &private_key.to_string())
            .await?;
        
        self.web3.eth().send_raw_transaction(signed.raw_transaction)
            .await
            .map_err(|e| anyhow!("Failed to send token transaction: {}", e))
    }
}

// Example usage
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

    // Example token address (e.g., USDC on Ethereum mainnet)
    let token_address = Address::from_str("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")?;
    
    // Get token balance
    let token_balance = wallet.get_token_balance(token_address, addresses[0]).await?;
    println!("Token Balance: {}", token_balance);

    // Example: Send ETH
    let to_address = Address::from_str("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")?;
    let amount = U256::from(1000000000000000000u64); // 1 ETH
    let tx_hash = wallet.send_eth(0, to_address, amount, None).await?;
    println!("ETH Transaction Hash: {:#x}", tx_hash);

    // Example: Send Tokens
    let token_amount = U256::from(1000000u64); // Amount depends on token decimals
    let token_tx_hash = wallet.send_token(token_address, 0, to_address, token_amount, None).await?;
    println!("Token Transaction Hash: {:#x}", token_tx_hash);

    Ok(())
}