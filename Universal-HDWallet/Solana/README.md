## Usage

Import crate:

```rust
use hdwallet_rs;
```

Note: This crate uses the [bip0039](https://github.com/koushiro/bip0039) crate for mnemonic and seed phrase generation; you can choose to generate your mnemonic from English, Japanese, Korean, Italian, French, Czech, Chinese, and Portuguese.

Generate extended key:

```
use hdwallet_rs::{
  extended_key::SolanaExPrivateKey,
  mnemonic
}

let seed_phrase = mnemonic::new_mnemonic(24, "English");
let seed = mnemonic::new_seed(seed_phrase.unwrap(), "".to_string());
let master_key = SolanaExPrivateKey::new_master_key(&seed).expect("master key");
```

Derive private key with it's derivation and public key:

```
use hdwallet_rs::{
    extended_key::SolanaExPrivateKey,
    mnemonic,
    solana::{
        key_chain::DefaultKeyChain,
        PrivKey, PubKey,
    },
    traits::{Deserialize, Serialize},
    SolanaExPrivateKey,
};

let new_mnemonic = mnemonic::new_mnemonic(24, "English");
let seed = mnemonic::new_seed(new_mnemonic.unwrap(), "".to_string());
let master_key = SolanaExPrivateKey::new_master_key(&seed).expect("master key");

// A default key chain on which others are based on.
let key_chain = DefaultKeyChain::new(master_key);

// Chain path.
let chain_path = "m/0H/1H";

// Get extended key and derivation from the chain path.
let (extended_key, derivation) = key_chain.derive_private_key(chain_path.into()).expect("fetch key");

// Private Key.
let private_key = PrivKey {
  derivation,
  extended_key,
};

// Public Key.
let public_key = PubKey::from_private_key(&private_key);

// Convert to Base58 address.
let serialized_key: String = public_key.serialize();

let deserialized_key = PubKey::deserialize((serialized_key, &key_chain, "m/0H/1H".into())).expect("deserialize");

assert_eq!(public_key, deserialized_key);
```

Note: In Solana, all key derivations are always in the hardened form, meaning each derivation path is suffixed with (H or ').
