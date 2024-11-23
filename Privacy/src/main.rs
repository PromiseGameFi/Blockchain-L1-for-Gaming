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
    fn create_user(&mut self, username: String) {
        let mut csprng = OsRng;
        
        // Generate Ed25519 keypair for signatures
        let keypair = Keypair::generate(&mut csprng);
        
        // Generate RSA keypair for encryption
        let rsa_private = RsaPrivateKey::new(&mut csprng, 2048).expect("Failed to generate RSA key");
        let rsa_public = rsa_private.to_public_key();
        
        let user = User {
            username: username.clone(),
            keypair,
            rsa_private,
            rsa_public,
        };
        
        self.users.insert(username, user);
    }
    
    // Encrypt and sign a message
    fn encrypt_message(&self, sender: &User, recipient: &User, message: &str) -> EncryptedMessage {
        // Generate a random symmetric key
        let symmetric_key = Aes256Gcm::generate_key(&mut AesOsRng);
        
        // Create cipher
        let cipher = Aes256Gcm::new(&symmetric_key);
        let nonce = Aes256Gcm::generate_nonce(&mut AesOsRng);
        
        // Encrypt the message using AES-GCM
        let encrypted_data = cipher
            .encrypt(&nonce, message.as_bytes().as_ref())
            .expect("Encryption failed");
        
        // Sign the original message
        let signature = sender.keypair.sign(message.as_bytes());
        
        // Encrypt the symmetric key with recipient's RSA public key
        let padding = PaddingScheme::new_pkcs1v15_encrypt();
        let encrypted_symmetric_key = recipient
            .rsa_public
            .encrypt(&mut OsRng, padding, &symmetric_key)
            .expect("Failed to encrypt symmetric key");
        
        EncryptedMessage {
            encrypted_data,
            signature,
            sender_public: sender.keypair.public,
            symmetric_key: encrypted_symmetric_key,
            nonce: nonce.to_vec(),
        }
    }
    
    // Decrypt and verify a message
    fn decrypt_message(&self, recipient: &User, message: &EncryptedMessage) -> Option<String> {
        // Decrypt the symmetric key using recipient's private key
        let padding = PaddingScheme::new_pkcs1v15_encrypt();
        let symmetric_key = recipient
            .rsa_private
            .decrypt(padding, &message.symmetric_key)
            .ok()?;
        
        // Create cipher
        let cipher = Aes256Gcm::new_from_slice(&symmetric_key).ok()?;
        let nonce = Nonce::from_slice(&message.nonce);
        
        // Decrypt the message
        let decrypted_data = cipher
            .decrypt(nonce, message.encrypted_data.as_ref())
            .ok()?;
        
        let decrypted_message = String::from_utf8(decrypted_data).ok()?;
        
        // Verify the signature
        message
            .sender_public
            .verify(
                decrypted_message.as_bytes(),
                &message.signature,
            )
            .ok()?;
        
        Some(decrypted_message)
    }
}

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

            ui.separator();

            // User Selection
            ui.heading("Select User");
            egui::ComboBox::from_label("Current User")
                .selected_text(self.current_user.as_deref().unwrap_or("None"))
                .show_ui(ui, |ui| {
                    for username in self.users.keys() {
                        ui.selectable_value(&mut self.current_user, Some(username.clone()), username);
                    }
                });

            // Message Sending Section
            if let Some(current_user) = &self.current_user {
               

                ui.text_edit_multiline(&mut self.message);

                if ui.button("Send Encrypted Message").clicked() && !self.message.is_empty() {
                    if let (Some(sender), Some(recipient)) = (
                        self.users.get(current_user),
                        self.users.get(&self.recipient),
                    ) {
                        let encrypted = self.encrypt_message(sender, recipient, &self.message);
                        self.encrypted_messages.push((self.recipient.clone(), encrypted));
                        self.message.clear();
                    }
                }

                // Display received messages
                ui.separator();
                ui.heading("Received Messages");
                let current_user_clone = current_user.clone();
                self.encrypted_messages.retain(|(recipient, encrypted_msg)| {
                    if recipient == &current_user_clone {
                        if let Some(recipient_user) = self.users.get(&current_user_clone) {
                            if let Some(decrypted) = self.decrypt_message(recipient_user, encrypted_msg) {
                                self.decrypted_messages.push((
                                    BASE64.encode(&encrypted_msg.sender_public.as_bytes()),
                                    decrypted,
                                ));
                            }
                        }
                        false
                    } else {
                        true
                    }
                });

                // Display decrypted messages
                for (sender, message) in &self.decrypted_messages {
                    ui.label(format!("From {}: {}", sender, message));
                }
            }
        });
    }
}

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions {
        initial_window_size: Some(egui::vec2(800.0, 600.0)),
        ..Default::default()
    };
    eframe::run_native(
        "Digital Signature System",
        options,
        Box::new(|_cc| Box::<SignatureApp>::default()),
    )
}