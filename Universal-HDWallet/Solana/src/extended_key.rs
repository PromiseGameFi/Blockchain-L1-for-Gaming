pub mod key_index;

use curve25519_dalek::edwards::CompressedEdwardsY;

use crate::{
    error::Error,
    traits::{Deserialize, Serialize},
};


/// Random entropy, part of extended key.
///
type ChainCode = Vec<u8>;

/// Extended Private Key implementation based on the EdDSA Curve

#[derive(Debug, Clone)]
pub struct SolanaExPrivateKey {
    pub private_key: Rc<Sk>,
    pub chain_code: ChainCode,
}

impl Eq for SolanaExPrivateKey {}

impl PartialEq for SolanaExPrivateKey {
    fn eq(&self, other: &Self) -> bool {
        self.private_key.as_bytes() == other.private_key.as_bytes()
            && self.chain_code == other.chain_code
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SolanaExPublicKey(pub Pk);

impl SolanaExPrivateKey {
    pub fn new_master_key(seed: &[u8]) -> Result<SolanaExPrivateKey, Error> {
        let signature = {
            let signing_key = Key::new(HMAC_SHA512, b"ed25519 seed");
            let mut h = Context::with_key(&signing_key);
            h.update(seed);
            h.sign()
        };
        let sig_bytes = signature.as_ref();
        let (key, chain_code) = sig_bytes.split_at(sig_bytes.len() / 2);
        let private_key = Rc::new(Sk::from_bytes(key)?);

        Ok(SolanaExPrivateKey {
            private_key,
            chain_code: chain_code.to_vec(),
        })
    }

    

    
}

impl SolanaExPublicKey {
    
}

impl Serialize<Vec<u8>> for SolanaExPrivateKey {
    fn serialize(&self) -> Vec<u8> {
        let mut buf = self.private_key.to_bytes().to_vec();
        buf.extend(&self.chain_code);
        buf
    }
}

impl Deserialize<&[u8], Error> for SolanaExPrivateKey {
    
}

impl Serialize<Vec<u8>> for SolanaExPublicKey {
    fn serialize(&self) -> Vec<u8> {
        self.0.to_bytes().to_vec()
    }
}

impl Deserialize<&[u8], Error> for SolanaExPublicKey {
    fn deserialize(data: &[u8]) -> Result<Self, Error> {
        let public_key = Pk::from_bytes(&data[..32]).unwrap();

        Ok(SolanaExPublicKey(public_key))
    }
}

#[cfg(test)]
mod tests {
    use crate::error::Error;
    use crate::traits::{Deserialize, Serialize};
    use crate::{mnemonic, KeyIndex, SolanaExPrivateKey, SolanaExPublicKey};

    fn get_solana_extended_key() -> Result<SolanaExPrivateKey, Error> {
        let seed_phrase = mnemonic::new_mnemonic(24, "English");
        let seed = mnemonic::new_seed(seed_phrase.unwrap(), "".to_string());

        Ok(SolanaExPrivateKey::new_master_key(&seed).expect("master key"))
    }

    #[test]
    fn derive_child_private_key() {
        let master_key = get_solana_extended_key().unwrap();
        // Solana keys are always hardended
        master_key
            .derive_private_key(KeyIndex::hardened_from_normalize_index(0).unwrap())
            .expect("hardended_key");
    }

    #[test]
    fn derive_child_public_key_from_child_private_key() {
        let master_key = get_solana_extended_key().unwrap();

        let child_private_key = master_key
            .derive_private_key(KeyIndex::hardened_from_normalize_index(1).unwrap())
            .unwrap();

        SolanaExPublicKey::from_private_key(&child_private_key).expect("public key");
    }

    #[test]
    fn priv_key_serialize_deserialize() {
        let master_key = get_solana_extended_key().unwrap();
        let buf = master_key.serialize();
        assert_eq!(
            SolanaExPrivateKey::deserialize(&buf).expect("deserialized"),
            master_key
        );
    }

    #[test]
    fn pub_key_serialize_deserialize() {
        let master_key =
            SolanaExPublicKey::from_private_key(&get_solana_extended_key().unwrap()).unwrap();
        let buf = master_key.serialize();
        assert_eq!(
            SolanaExPublicKey::deserialize(&buf).expect("deserialized"),
            master_key
        );
    }
}
