# Ethereum Wallet in Rust with UI

This project is a simple Ethereum wallet built in Rust with an optional user interface (UI). It supports importing a BIP-39 seed phrase (12 or 24 words), fetching balance, sending ETH, and switching between Ethereum mainnet and testnet networks.

The UI can be configured to run as a web application using **Yew** or as a cross-platform desktop application using **Tauri**.

## Features

- **Import Seed Phrase**: Users can import a BIP-39 mnemonic phrase (12 or 24 words).
- **Network Configuration**: Supports Ethereum mainnet and testnet (Rinkeby) networks.
- **Check Balance**: Retrieves and displays the ETH balance of the wallet.
- **Send ETH**: Send ETH to another address.
- **View Wallet Address**: Display the wallet address for receiving funds.
- **User Interface**: Choose between a web-based UI (using Yew) or a desktop app (using Tauri).

## Dependencies

- [ethers-rs](https://crates.io/crates/ethers): Ethereum library for Rust.
- [bip39](https://crates.io/crates/bip39): For BIP-39 mnemonic phrase handling.
- [tokio](https://crates.io/crates/tokio): Async runtime for Rust.
- [hex](https://crates.io/crates/hex): Hexadecimal encoding and decoding.
- [yew](https://crates.io/crates/yew) (optional): For a web-based UI.
- [tauri](https://tauri.app/) (optional): For a cross-platform desktop UI.

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/ethereum-wallet-rust.git
    cd ethereum-wallet-rust
    ```

2. **Install Dependencies**: Add dependencies in `Cargo.toml` if they aren’t already.

    ```toml
    [dependencies]
    ethers = "1.0"         # Ethereum client for Rust
    bip39 = "1.1"          # BIP-39 support for seed phrases
    hex = "0.4"            # Hexadecimal encoding/decoding
    tokio = { version = "1", features = ["full"] } # Async runtime
    yew = "0.19"           # Web-based UI (optional)
    ```

3. **Set Up an RPC Provider**:
   - Obtain an Infura Project ID or use another Ethereum node provider.
   - Replace `"YOUR_INFURA_PROJECT_ID"` in the `get_network` function with your actual Infura Project ID or another provider’s URL.

4. **Compile the Project**

    ```bash
    cargo build
    ```

## Setting Up the User Interface

### Web-Based UI with Yew

1. **Install Trunk**:
   - [Trunk](https://trunkrs.dev/) is required to build and serve Yew applications.
   
    ```bash
    cargo install trunk
    ```

2. **Launch the Yew Application**:
   - With `trunk serve`, the Yew application will start a local server, allowing you to interact with the wallet in your browser.

    ```bash
    trunk serve
    ```

3. **Add UI Components**:
   - You can add components to interact with wallet features, such as:
     - **WalletAddress**: Display and copy the wallet address.
     - **BalanceDisplay**: Display the ETH balance.
     - **TransactionForm**: Form for sending ETH.

### Desktop UI with Tauri

1. **Install Tauri CLI**:
   - [Tauri](https://tauri.app/) provides a framework for building cross-platform desktop applications with Rust.

    ```bash
    cargo install tauri-cli
    ```

2. **Initialize Tauri in the Project**:
   - Run `cargo tauri init` in the project directory to set up Tauri files for a desktop application.

3. **Launch the Tauri Application**:
   - To start the application, run the following command:

    ```bash
    cargo tauri dev
    ```

4. **UI Components for Tauri**:
   - Use HTML, CSS, and JavaScript for the Tauri frontend and connect with Rust backend functions like `generate_wallet_from_mnemonic`, `get_balance`, and `send_eth`.

## Usage

1. **Run the Application**

    ```bash
    cargo run
    ```

2. **Using the Wallet**:
   - **Import a Seed Phrase**: Modify the `mnemonic_phrase` variable in `main.rs` to your seed phrase.
   - **Choose a Network**: Update the `network` variable to select the desired network (e.g., `"mainnet"` or `"rinkeby"`).
   - **Check Balance**: The wallet balance is displayed after launching.
   - **Send ETH**: Example code for sending ETH to another address is included.

## Example Configuration

In `main.rs`, update the following variables:

```rust
// Replace this with your 12 or 24-word seed phrase
let mnemonic_phrase = "your seed phrase here";

// Choose the network: "mainnet" or "rinkeby"
let network = get_network("rinkeby");

// Example recipient and amount (in ETH)
let recipient_address = Address::from_str("0xRecipientAddressHere")?;
let amount = parse_eth_amount("0.01")?; // Amount in ETH
