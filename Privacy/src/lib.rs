use ed25519_dalek::{Keypair, PublicKey, SecretKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;
use rsa::{PaddingScheme, PublicKey as RsaPublicKey, RsaPrivateKey, RsaPublicKey as _};
use std::collections::HashMap;
use eframe::egui;
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng as AesOsRng},
    Aes256Gcm,
    Nonce,
};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};



// Main application state
struct SignatureApp {
    users: HashMap<String, User>,
    current_user: Option<String>,
    recipient: String,
    message: String,
    encrypted_messages: Vec<(String, EncryptedMessage)>,
    decrypted_messages: Vec<(String, String)>,
    new_username: String,
    new_userCount: String,
}

impl Default for SignatureApp {
    fn default() -> Self {
        Self {
            users: HashMap::new(),
            current_user: None,
            recipient: String::new(),
            message: String::new(),
            encrypted_messages: Vec::new(),
            decrypted_messages: Vec::new(),
            new_username: String::new(),
            new_userCount: String::new(),
        }
    }
}

impl SignatureApp {
    // Create a new user with keypair
    
    
    // Encrypt and sign a message
    
    
    // Decrypt and verify a message
    

          


fn main() -> Result<(), eframe::Error> {
   