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

// Structure to hold user information
#[derive(Clone)]
struct User {
    username: String,
    keypair: Keypair,                    // For signatures
    rsa_private: RsaPrivateKey,          // For encryption
    rsa_public: RsaPublicKey,            // For encryption
}

// Structure to hold an encrypted message
#[derive(Clone)]
struct EncryptedMessage {
    encrypted_data: Vec<u8>,             // The encrypted message
    signature: Signature,                // Signature of the original message
    sender_public: PublicKey,            // Sender's public key for verification
    symmetric_key: Vec<u8>,              // Encrypted symmetric key
    nonce: Vec<u8>,                      // Nonce for AES-GCM
}

// Main application state
struct SignatureApp {
    users: HashMap<String, User>,
    current_user: Option<String>,
    recipient: String,
    message: String,
    encrypted_messages: Vec<(String, EncryptedMessage)>,
    decrypted_messages: Vec<(String, String)>,
    new_username: String,
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
        }
    }
}

impl SignatureApp {
    // Create a new user with keypair
    
    
    // Encrypt and sign a message
    
    
    // Decrypt and verify a message
    
impl eframe::App for SignatureApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            // User Creation Section
            ui.heading("Create New User");
            ui.horizontal(|ui| {
                ui.text_edit_singleline(&mut self.new_username);
                if ui.button("Create User").clicked() && !self.new_username.is_empty() {
                    self.create_user(self.new_username.clone());
                    self.new_username.clear();
                }
            });

          


fn main() -> Result<(), eframe::Error> {
   