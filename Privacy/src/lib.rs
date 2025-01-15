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



   