use crate::error::{Result, WalletError};
use crate::types::{TransactionInfo, TokenInfo};
use bip39::{Mnemonic, Language, MnemonicType};
use ethereum_types::{Address, U256};
use secp256k1::{SecretKey, PublicKey, Secp256k1};
use tiny_keccak::{Keccak, Hasher};
use web3::{
    Web3,
    transports::Http,
    types::{TransactionParameters, H256},
};

pub struct EVMWallet {
    mnemonic: String,
    web3: Web3<Http>,
    secp: Secp256k1<secp256k1::All>,
}

impl EVMWallet {
    pub fn new(node_url: &str) -> Result<Self> {
        let mut rng = rand::thread_rng();
        let mnemonic = Mnemonic::new(MnemonicType::Words24, Language::English);
        Self::from_mnemonic(mnemonic.phrase(), node_url)
    }

    pub fn from_mnemonic(mnemonic_phrase: &str, node_url: &str) -> Result<Self> {
        let mnemonic = Mnemonic::from_phrase(mnemonic_phrase, Language::English)
            .map_err(|e| WalletError::InvalidMnemonic(e.to_string()))?;

        let transport = Http::new(node_url)
            .map_err(|e| WalletError::ConnectionError(e.to_string()))?;
        
        let web3 = Web3::new(transport);
        let secp = Secp256k1::new();

        Ok(Self {
            mnemonic: mnemonic_phrase.to_string(),
            web3,
            secp,
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
        let private_key = self.derive_private_key(account_index)?;
        let public_key = PublicKey::from_secret_key(&self.secp, &private_key);
        
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

        // Convert private key to bytes for signing
        let private_key_bytes = private_key.secret_bytes();
        let signed = self.web3.accounts()
            .sign_transaction(transaction.clone(), hex::encode(private_key_bytes))
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

        // Convert private key to bytes for signing
        let private_key_bytes = private_key.secret_bytes();
        let signed = self.web3.accounts()
            .sign_transaction(transaction.clone(), hex::encode(private_key_bytes))
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