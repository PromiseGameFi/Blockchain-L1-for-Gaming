import tkinter as tk
from tkinter import messagebox
from bit import Key
from Crypto.Cipher import AES
from hashlib import sha256
import os

# Encrypt function for BIP38
def bip38_encrypt(private_key: bytes, passphrase: str) -> bytes:
    salt = os.urandom(4)
    passphrase_bytes = passphrase.encode('utf-8')
    scrypt_key = sha256(passphrase_bytes + salt).digest()
    aes_key = scrypt_key[:16]
    cipher = AES.new(aes_key, AES.MODE_ECB)
    encrypted_key = cipher.encrypt(private_key.ljust(32, b'\0'))
    bip38_encrypted_key = salt + encrypted_key
    return bip38_encrypted_key

# Decrypt function for BIP38
def bip38_decrypt(bip38_encrypted_key: bytes, passphrase: str) -> bytes:
    salt = bip38_encrypted_key[:4]
    encrypted_key = bip38_encrypted_key[4:]
    passphrase_bytes = passphrase.encode('utf-8')
    scrypt_key = sha256(passphrase_bytes + salt).digest()
    aes_key = scrypt_key[:16]
    cipher = AES.new(aes_key, AES.MODE_ECB)
    private_key = cipher.decrypt(encrypted_key).strip(b'\0')
    return private_key

# Function to handle encryption button click
def encrypt_key():
    private_key_input = private_key_entry.get()
    passphrase = encrypt_password_entry.get()
    if not private_key_input or not passphrase:
        messagebox.showerror("Error", "Please enter both a private key and a password.")
        return
    try:
        private_key_bytes = bytes.fromhex(private_key_input)
        bip38_key = bip38_encrypt(private_key_bytes, passphrase)
        encrypted_key_output.set(bip38_key.hex())
    except Exception as e:
        messagebox.showerror("Encryption Error", f"An error occurred: {e}")

# Function to handle decryption button click
def decrypt_key():
    bip38_key_input = bip38_key_entry.get()
    passphrase = decrypt_password_entry.get()
    if not bip38_key_input or not passphrase:
        messagebox.showerror("Error", "Please enter both a BIP38 encrypted key and a password.")
        return
    try:
        bip38_key_bytes = bytes.fromhex(bip38_key_input)
        private_key = bip38_decrypt(bip38_key_bytes, passphrase)
        decrypted_key_output.set(private_key.hex())
    except Exception as e:
        messagebox.showerror("Decryption Error", f"An error occurred: {e}")

# Set up the main UI
root = tk.Tk()
root.title("BIP38 Encrypt/Decrypt Tool")
root.geometry("500x500")

# Encrypt Section
tk.Label(root, text="Encrypt Private Key", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Private Key (Hex):").pack()
private_key_entry = tk.Entry(root, width=50)
private_key_entry.pack()

tk.Label(root, text="Password:").pack()
encrypt_password_entry = tk.Entry(root, show="*", width=50)
encrypt_password_entry.pack()

encrypt_button = tk.Button(root, text="Encrypt", command=encrypt_key)
encrypt_button.pack(pady=10)

tk.Label(root, text="BIP38 Encrypted Key:").pack()
encrypted_key_output = tk.StringVar()
encrypted_key_label = tk.Entry(root, textvariable=encrypted_key_output, width=50, state="readonly")
encrypted_key_label.pack()

# Decrypt Section
tk.Label(root, text="Decrypt BIP38 Key", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="BIP38 Encrypted Key (Hex):").pack()
bip38_key_entry = tk.Entry(root, width=50)
bip38_key_entry.pack()

tk.Label(root, text="Password:").pack()
decrypt_password_entry = tk.Entry(root, show="*", width=50)
decrypt_password_entry.pack()

decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_key)
decrypt_button.pack(pady=10)

tk.Label(root, text="Decrypted Private Key:").pack()
decrypted_key_output = tk.StringVar()
decrypted_key_label = tk.Entry(root, textvariable=decrypted_key_output, width=50, state="readonly")
decrypted_key_label.pack()

# Start the main loop
root.mainloop()




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
