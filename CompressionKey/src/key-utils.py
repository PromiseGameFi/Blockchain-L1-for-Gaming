



"""from bit import Key
from Crypto.Cipher import AES
from hashlib import sha256
import os
import hmac

def bip38_encrypt(private_key: bytes, passphrase: str) -> bytes:
    # Step 1: Generate a random salt
    salt = os.urandom(4)
    
    # Step 2: Derive AES encryption key from passphrase and salt
    passphrase_bytes = passphrase.encode('utf-8')
    scrypt_key = sha256(passphrase_bytes + salt).digest()
    aes_key = scrypt_key[:16]
    
    # Step 3: Encrypt the private key using AES
    cipher = AES.new(aes_key, AES.MODE_ECB)
    encrypted_key = cipher.encrypt(private_key)
    
    # Combine salt and encrypted key to form the BIP38 encrypted key
    bip38_encrypted_key = salt + encrypted_key
    return bip38_encrypted_key

def bip38_decrypt(bip38_encrypted_key: bytes, passphrase: str) -> bytes:
    # Extract salt and encrypted key from the BIP38 key
    salt = bip38_encrypted_key[:4]
    encrypted_key = bip38_encrypted_key[4:]
    
    # Derive AES decryption key from passphrase and salt
    passphrase_bytes = passphrase.encode('utf-8')
    scrypt_key = sha256(passphrase_bytes + salt).digest()
    aes_key = scrypt_key[:16]
    
    # Decrypt the private key using AES
    cipher = AES.new(aes_key, AES.MODE_ECB)
    private_key = cipher.decrypt(encrypted_key)
    return private_key

# Example Usage
# Generate a random private key using bit library
key = Key()
original_private_key = key.to_bytes()

# Define your passphrase
passphrase = "YourSecurePassphrase"

# Encrypt the private key using BIP38
bip38_key = bip38_encrypt(original_private_key, passphrase)
print("Encrypted BIP38 Key:", bip38_key.hex())

# Decrypt the private key using BIP38
decrypted_private_key = bip38_decrypt(bip38_key, passphrase)
print("Decrypted Private Key:", decrypted_private_key.hex())

# Check if the decryption was successful
assert decrypted_private_key == original_private_key
print("Decryption successful, keys match.")
"""
