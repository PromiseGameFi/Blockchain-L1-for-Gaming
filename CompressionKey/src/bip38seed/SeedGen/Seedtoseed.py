import tkinter as tk
from tkinter import messagebox, ttk
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

def bytes_to_24_word_mnemonic(data, force_length=None):
    """Convert bytes to a 24-word mnemonic phrase"""
    # Ensure data is at least 32 bytes
    if len(data) < 32:
        data = data + hashlib.sha256(data).digest()[:32-len(data)]
    
    # Convert to bits
    bits = bin(int.from_bytes(data, byteorder='big'))[2:].zfill(len(data) * 8)
    
    # Take appropriate number of bits (264 for 24 words)
    bits = bits[:264]
    
    # Split into 11-bit chunks
    chunks = [bits[i:i+11] for i in range(0, len(bits), 11)]
    
    # Convert chunks to indexes
    indexes = [int(chunk, 2) % 2048 for chunk in chunks]
    
    # Ensure we have exactly 24 words
    while len(indexes) < 24:
        indexes.append(0)
    
    # Convert indexes to words
    return ' '.join(BIP39_WORDLIST[index] for index in indexes[:24])

def encrypt_to_24_word_mnemonic(seed_phrase, password):
    """Encrypt a seed phrase and convert to a 24-word mnemonic"""
    try:
        # First convert the input seed phrase to bytes
        seed_bytes = mnemonic_to_bytes(seed_phrase)
        
        # Generate salt and IV
        salt = get_random_bytes(16)
        iv = get_random_bytes(16)
        
        # Generate encryption key
        key = PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=1000000)
        
        # Prepare cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad the data
        padded_seed = pad(seed_bytes, AES.block_size)
        
        # Encrypt
        encrypted_seed = cipher.encrypt(padded_seed)
        
        # Combine salt + iv + encrypted data
        combined_data = salt + iv + encrypted_seed
        
        # Convert to 24-word mnemonic
        return bytes_to_24_word_mnemonic(combined_data)
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

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
        key = PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=1000000)
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_seed)
        
        # Remove padding
        decrypted_bytes = unpad(decrypted_padded, AES.block_size)
        
        # Convert back to 24-word mnemonic
        return bytes_to_24_word_mnemonic(key)
    except Exception as e:
        print(f"Debug - Decryption error: {str(e)}")  # For debugging
        raise ValueError("Decryption failed. Wrong password or corrupted data.")

class SeedPhraseEncryptionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Seed Phrase Encryption Tool")
        self.root.geometry("800x800")
        
        # Create main frames
        self.create_encryption_frame()
        self.create_decryption_frame()
        
    def create_encryption_frame(self):
        # Encryption Frame
        encrypt_frame = ttk.LabelFrame(self.root, text="Encrypt Seed Phrase", padding="10")
        encrypt_frame.pack(fill="x", padx=10, pady=5)
        
        # Seed Phrase Entry
        ttk.Label(encrypt_frame, text="Original Seed Phrase:").pack(fill="x")
        self.seed_phrase_entry = tk.Text(encrypt_frame, height=3, width=70)
        self.seed_phrase_entry.pack(fill="x", pady=5)
        
        # Password Entry
        ttk.Label(encrypt_frame, text="Password:").pack(fill="x")
        self.encrypt_password_entry = ttk.Entry(encrypt_frame, show="*", width=70)
        self.encrypt_password_entry.pack(fill="x", pady=5)
        
        # Encrypt Button
        ttk.Button(encrypt_frame, text="Encrypt", command=self.encrypt_button_click).pack(pady=10)
        
        # Encrypted Output
        ttk.Label(encrypt_frame, text="Encrypted 24-Word Seed Phrase:").pack(fill="x")
        self.encrypted_seed_output = tk.StringVar()
        encrypted_output = ttk.Entry(encrypt_frame, textvariable=self.encrypted_seed_output, width=70, state="readonly")
        encrypted_output.pack(fill="x", pady=5)
        
        # Copy Button
        ttk.Button(encrypt_frame, text="Copy Encrypted Seed", command=self.copy_encrypted_seed).pack(pady=5)
        
    def create_decryption_frame(self):
        # Decryption Frame
        decrypt_frame = ttk.LabelFrame(self.root, text="Decrypt Seed Phrase", padding="10")
        decrypt_frame.pack(fill="x", padx=10, pady=5)
        
        # Encrypted Seed Entry
        ttk.Label(decrypt_frame, text="Encrypted 24-Word Seed Phrase:").pack(fill="x")
        self.encrypted_seed_entry = ttk.Entry(decrypt_frame, width=70)
        self.encrypted_seed_entry.pack(fill="x", pady=5)
        
        # Password Entry
        ttk.Label(decrypt_frame, text="Password:").pack(fill="x")
        self.decrypt_password_entry = ttk.Entry(decrypt_frame, show="*", width=70)
        self.decrypt_password_entry.pack(fill="x", pady=5)
        
        # Decrypt Button
        ttk.Button(decrypt_frame, text="Decrypt", command=self.decrypt_button_click).pack(pady=10)
        
        # Decrypted Output
        ttk.Label(decrypt_frame, text="Decrypted Seed Phrase:").pack(fill="x")
        self.decrypted_seed_output = tk.StringVar()
        decrypted_output = ttk.Entry(decrypt_frame, textvariable=self.decrypted_seed_output, width=70, state="readonly")
        decrypted_output.pack(fill="x", pady=5)
        
        # Copy Button
        ttk.Button(decrypt_frame, text="Copy Decrypted Seed", command=self.copy_decrypted_seed).pack(pady=5)
        
    def encrypt_button_click(self):
        seed_phrase = self.seed_phrase_entry.get("1.0", "end-1c").strip()
        password = self.encrypt_password_entry.get()
        
        if not seed_phrase or not password:
            messagebox.showerror("Error", "Please enter both a seed phrase and a password.")
            return
            
        try:
            encrypted_mnemonic = encrypt_to_24_word_mnemonic(seed_phrase, password)
            self.encrypted_seed_output.set(encrypted_mnemonic)
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))
            
    def decrypt_button_click(self):
        encrypted_mnemonic = self.encrypted_seed_entry.get().strip()
        password = self.decrypt_password_entry.get()
        
        if not encrypted_mnemonic or not password:
            messagebox.showerror("Error", "Please enter both an encrypted mnemonic and a password.")
            return
            
        try:
            decrypted_phrase = decrypt_from_24_word_mnemonic(encrypted_mnemonic, password)
            self.decrypted_seed_output.set(decrypted_phrase)
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))
            
    def copy_encrypted_seed(self):
        encrypted_seed = self.encrypted_seed_output.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(encrypted_seed)
        messagebox.showinfo("Success", "Encrypted seed phrase copied to clipboard!")
        
    def copy_decrypted_seed(self):
        decrypted_seed = self.decrypted_seed_output.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(decrypted_seed)
        messagebox.showinfo("Success", "Decrypted seed phrase copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SeedPhraseEncryptionTool(root)
    root.mainloop()