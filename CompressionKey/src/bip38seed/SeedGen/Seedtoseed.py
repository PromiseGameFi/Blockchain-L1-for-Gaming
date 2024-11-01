import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from word_list import BIP39_WORDLIST
import hashlib
import hmac

def mnemonic_to_bytes(mnemonic):
    """Convert a mnemonic phrase to bytes"""
    if not mnemonic:
        raise ValueError("Mnemonic is required")
    
    words = mnemonic.strip().lower().split()
    if len(words) == 0:
        raise ValueError("Empty mnemonic provided")
    
    # Convert words to indexes
    try:
        indexes = [BIP39_WORDLIST.index(word) for word in words]
    except ValueError as e:
        raise ValueError(f"Invalid word in mnemonic: {e}")
    
    # Convert to bits
    bits = ''.join(bin(index)[2:].zfill(11) for index in indexes)
    
    # Convert bits to bytes
    byte_length = len(bits) // 8
    return int(bits[:byte_length * 8], 2).to_bytes(byte_length, byteorder='big')

def bytes_to_24_word_mnemonic(data):
    """Convert bytes to a 24-word mnemonic phrase"""
    # Ensure we have enough entropy (32 bytes for 24 words)
    if len(data) < 32:
        # Pad data to 32 bytes if needed
        data = data + hashlib.sha256(data).digest()[:32-len(data)]
    elif len(data) > 32:
        # Take first 32 bytes if data is too long
        data = data[:32]
    
    # Convert bytes to bits
    bits = bin(int.from_bytes(data, byteorder='big'))[2:].zfill(256)
    
    # Split into 11-bit chunks (24 words = 264 bits)
    chunks = [bits[i:i+11] for i in range(0, 256, 11)]
    
    # Convert chunks to indexes
    indexes = [int(chunk, 2) % 2048 for chunk in chunks]
    
    # Add extra words if needed to reach 24 words
    while len(indexes) < 24:
        random_bytes = get_random_bytes(2)
        indexes.append(int.from_bytes(random_bytes, 'big') % 2048)
    
    # Convert indexes to words
    return ' '.join(BIP39_WORDLIST[index] for index in indexes[:24])

def encrypt_to_24_word_mnemonic(seed_phrase, password):
    """Encrypt a seed phrase and convert to a 24-word mnemonic"""
    # Convert input seed phrase to bytes
    seed_bytes = mnemonic_to_bytes(seed_phrase)
    
    # Generate salt and IV
    salt = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    # Generate encryption key
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    
    # Prepare cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the data properly using PKCS7
    padded_seed = pad(seed_bytes, AES.block_size)
    
    # Encrypt
    encrypted_seed = cipher.encrypt(padded_seed)
    
    # Combine salt + iv + encrypted data
    combined_data = salt + iv + encrypted_seed
    
    # Convert to 24-word mnemonic
    return bytes_to_24_word_mnemonic(combined_data)

def decrypt_from_24_word_mnemonic(encrypted_mnemonic, password):
    """Decrypt a 24-word mnemonic back to original seed phrase"""
    try:
        # Convert encrypted mnemonic to bytes
        encrypted_bytes = mnemonic_to_bytes(encrypted_mnemonic)
         
        
        # Extract components
        salt = encrypted_bytes[:16]
        iv = encrypted_bytes[16:32]
        encrypted_seed = encrypted_bytes[32:]
        
        # Generate decryption key
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_seed)
        
        # Remove padding
        decrypted_bytes = unpad(decrypted_padded, AES.block_size)
        
        # Convert to mnemonic
        return bytes_to_24_word_mnemonic(decrypted_bytes)
    except ValueError as e:
        raise ValueError("Decryption failed. Wrong password or corrupted data.")

# GUI Functions remain the same
def encrypt_button_click():
    seed_phrase = seed_phrase_entry.get("1.0", "end-1c").strip()
    password = encrypt_password_entry.get()
    
    if not seed_phrase or not password:
        messagebox.showerror("Error", "Please enter both a seed phrase and a password.")
        return

    try:
        encrypted_mnemonic = encrypt_to_24_word_mnemonic(seed_phrase, password)
        encrypted_seed_output.set(encrypted_mnemonic)
    except Exception as e:
        messagebox.showerror("Encryption Error", f"An error occurred: {str(e)}")

def decrypt_button_click():
    encrypted_mnemonic = encrypted_seed_entry.get().strip()
    password = decrypt_password_entry.get()
    
    if not encrypted_mnemonic or not password:
        messagebox.showerror("Error", "Please enter both an encrypted mnemonic and a password.")
        return

    try:
        original_phrase = decrypt_from_24_word_mnemonic(encrypted_mnemonic, password)
        decrypted_seed_output.set(original_phrase)
    except Exception as e:
        messagebox.showerror("Decryption Error", f"An error occurred: {str(e)}")

def copy_encrypted_seed():
    encrypted_seed = encrypted_seed_output.get()
    root.clipboard_clear()
    root.clipboard_append(encrypted_seed)
    messagebox.showinfo("Copied", "Encrypted seed phrase copied to clipboard!")

def copy_decrypted_seed():
    decrypted_seed = decrypted_seed_output.get()
    root.clipboard_clear()
    root.clipboard_append(decrypted_seed)
    messagebox.showinfo("Copied", "Decrypted seed phrase copied to clipboard!")

# GUI Setup
root = tk.Tk()
root.title("24-Word Seed Phrase Encryption Tool")
root.geometry("800x700")

# GUI elements remain the same as in original code...
tk.Label(root, text="Encrypt Seed Phrase", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Original Seed Phrase:").pack()
seed_phrase_entry = tk.Text(root, height=5, width=70)
seed_phrase_entry.pack()

tk.Label(root, text="Password:").pack()
encrypt_password_entry = tk.Entry(root, show="*", width=70)
encrypt_password_entry.pack()

encrypt_button = tk.Button(root, text="Encrypt", command=encrypt_button_click)
encrypt_button.pack(pady=10)

tk.Label(root, text="Encrypted 24-Word Seed Phrase:").pack()
encrypted_seed_output = tk.StringVar()
encrypted_seed_label = tk.Entry(root, textvariable=encrypted_seed_output, width=70, state="readonly")
encrypted_seed_label.pack()

copy_encrypted_button = tk.Button(root, text="Copy Encrypted Seed", command=copy_encrypted_seed)
copy_encrypted_button.pack(pady=5)

tk.Label(root, text="Decrypt Seed Phrase", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="Encrypted 24-Word Seed Phrase:").pack()
encrypted_seed_entry = tk.Entry(root, width=70)
encrypted_seed_entry.pack()

tk.Label(root, text="Password:").pack()
decrypt_password_entry = tk.Entry(root, show="*", width=70)
decrypt_password_entry.pack()

decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_button_click)
decrypt_button.pack(pady=10)

tk.Label(root, text="Original Seed Phrase:").pack()
decrypted_seed_output = tk.StringVar()
decrypted_seed_label = tk.Entry(root, textvariable=decrypted_seed_output, width=70, state="readonly")
decrypted_seed_label.pack()

copy_decrypted_button = tk.Button(root, text="Copy Decrypted Seed", command=copy_decrypted_seed)
copy_decrypted_button.pack(pady=5)

root.mainloop()