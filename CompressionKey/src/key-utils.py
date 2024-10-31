





"""import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import binascii

# Encrypt function using AES-256-CBC
def encrypt_key(private_key_hex, password):
    # Validate that the private key is a 64-character hex string
    if len(private_key_hex) != 64 or not all(c in '0123456789abcdefABCDEF' for c in private_key_hex):
        raise ValueError("Private key must be a 64-character hex string.")
    
    salt = get_random_bytes(16)  # Generate a 16-byte salt
    iv = get_random_bytes(16)  # Generate a 16-byte IV for AES
    key = PBKDF2(password, salt, dkLen=32, count=1000000)  # Derive a 32-byte key
    
    # Convert private key to bytes
    private_key = binascii.unhexlify(private_key_hex)
    
    # Prepare AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the private key to 32 bytes if necessary
    padded_key = private_key + b'\0' * (32 - len(private_key))
    
    # Encrypt the private key
    encrypted_key = cipher.encrypt(padded_key)
    
    # Return salt, IV, and encrypted key as hex for storage
    return binascii.hexlify(salt + iv + encrypted_key).decode()

# Decrypt function using AES-256-CBC
def decrypt_key(encrypted_hex, password):
    encrypted_data = binascii.unhexlify(encrypted_hex)
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_key = encrypted_data[32:]
    
    # Derive the key using the same password and salt
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    
    # Prepare AES cipher in CBC mode for decryption
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt the key and strip padding
    decrypted_key = cipher.decrypt(encrypted_key).rstrip(b'\0')
    return binascii.hexlify(decrypted_key).decode()

# Function to handle encryption button click
def encrypt_button_click():
    private_key = private_key_entry.get()
    password = encrypt_password_entry.get()
    
    if not private_key or not password:
        messagebox.showerror("Error", "Please enter both a private key and a password.")
        return

    try:
        encrypted_key = encrypt_key(private_key, password)
        encrypted_key_output.set(encrypted_key)
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Encryption Error", f"An error occurred: {e}")

# Function to handle decryption button click
def decrypt_button_click():
    encrypted_key = bip38_key_entry.get()
    password = decrypt_password_entry.get()
    
    if not encrypted_key or not password:
        messagebox.showerror("Error", "Please enter both an encrypted key and a password.")
        return

    try:
        decrypted_key = decrypt_key(encrypted_key, password)
        decrypted_key_output.set(decrypted_key)
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Decryption Error", f"An error occurred: {e}")

# Set up the main UI
root = tk.Tk()
root.title("Ethereum Private Key Encrypt/Decrypt Tool")
root.geometry("600x500")

# Encrypt Section
tk.Label(root, text="Encrypt Ethereum Private Key", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Private Key (Hex, 64 characters):").pack()
private_key_entry = tk.Entry(root, width=70)
private_key_entry.pack()

tk.Label(root, text="Password:").pack()
encrypt_password_entry = tk.Entry(root, show="*", width=70)
encrypt_password_entry.pack()

encrypt_button = tk.Button(root, text="Encrypt", command=encrypt_button_click)
encrypt_button.pack(pady=10)

tk.Label(root, text="Encrypted Key:").pack()
encrypted_key_output = tk.StringVar()
encrypted_key_label = tk.Entry(root, textvariable=encrypted_key_output, width=70, state="readonly")
encrypted_key_label.pack()

# Decrypt Section
tk.Label(root, text="Decrypt Encrypted Key", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="Encrypted Key (Hex):").pack()
bip38_key_entry = tk.Entry(root, width=70)
bip38_key_entry.pack()

tk.Label(root, text="Password:").pack()
decrypt_password_entry = tk.Entry(root, show="*", width=70)
decrypt_password_entry.pack()

decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_button_click)
decrypt_button.pack(pady=10)

tk.Label(root, text="Decrypted Private Key:").pack()
decrypted_key_output = tk.StringVar()
decrypted_key_label = tk.Entry(root, textvariable=decrypted_key_output, width=70, state="readonly")
decrypted_key_label.pack()

# Start the main loop
root.mainloop()
  """