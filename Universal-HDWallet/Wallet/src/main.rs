use ethers::core::k256::ecdsa::SigningKey;
use ethers::prelude::*;
use bip39::{Mnemonic, Language, Seed};
use std::str::FromStr;
use std::error::Error;

#[derive(Debug, Clone)]
struct NetworkConfig {
    name: String,
    rpc_url: String,
}

// Function to generate wallet from mnemonic seed phrase
fn generate_wallet_from_mnemonic(mnemonic_phrase: &str) -> Result<Wallet<SigningKey>, Box<dyn Error>> {
    let mnemonic = Mnemonic::from_phrase(mnemonic_phrase, Language::English)?;
    let seed = Seed::new(&mnemonic, "");
    let wallet = Wallet::from_seed(seed.as_bytes())?;
    println!("Wallet Address: {:?}", wallet.address());
    Ok(wallet)
}

// Function to get the network configuration

}

// Function to get the ETH balance of the wallet
async fn get_balance(wallet: &Wallet<SigningKey>, provider_url: &str) -> Result<U256, Box<dyn Error>> {
    let provider = Provider::<Http>::try_from(provider_url)?;
    let balance = provider.get_balance(wallet.address(), None).await?;
    Ok(balance)
}

// Function to send ETH to a specified address
async fn send_eth(wallet: Wallet<SigningKey>, to: Address, amount: U256, provider_url: &str) -> Result<TxHash, Box<dyn Error>> {
    let provider = Provider::<Http>::try_from(provider_url)?.with_sender(wallet);
    let tx = TransactionRequest::pay(to, amount);
    let pending_tx = provider.send_transaction(tx, None).await?;
    println!("Transaction sent with hash: {:?}", *pending_tx);
    Ok(*pending_tx)
}

// Helper function to parse an amount in ETH to Wei (U256 format)
fn parse_eth_amount(amount_in_eth: &str) -> Result<U256, Box<dyn Error>> {
    let amount_eth = amount_in_eth.parse::<f64>()?;
    let wei_value = amount_eth * 1e18;
    Ok(U256::from(wei_value as u128))
}

// Main function to run the wallet application
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Step 1: User enters their seed phrase
    let mnemonic_phrase = "your seed phrase here";
    let wallet = generate_wallet_from_mnemonic(mnemonic_phrase)?;

    // Step 2: Select the network (e.g., "mainnet" or "rinkeby")
    let network = get_network("rinkeby");

    // Step 3: Fetch and display the wallet balance
    let balance = get_balance(&wallet, &network.rpc_url).await?;
    println!("Balance: {} ETH", balance);

    // Step 4: Send a transaction (example usage)
    let recipient_address = Address::from_str("0xRecipientAddressHere")?;
    let amount = parse_eth_amount("0.01")?; // sending 0.01 ETH
    send_eth(wallet.clone(), recipient_address, amount, &network.rpc_url).await?;

    Ok(())
}
