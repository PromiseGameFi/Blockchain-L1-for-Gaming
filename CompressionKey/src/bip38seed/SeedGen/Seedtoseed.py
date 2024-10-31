import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from word_list import BIP39_WORDLIST
import binascii
import hashlib

def words_to_seed(words):
    """Convert a list of words to a seed."""
    return hashlib.sha256(' '.join(words).encode('utf-8')).digest()

def seed_to_words(seed, wordlist):
    """Convert a seed to a list of words."""
    # Use a standard wordlist (in this case, we'll use a predefined list)
    # In a real implementation, you'd use a full BIP39 wordlist
    return wordlist[:len(seed) // 4]

# Standard BIP39 word list (first 2048 words)
"""BIP39_WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", 
    # ... (you would include the full 2048 words here)
    "zone", "zoo", "zookeeper", "zoology"
]"""

def encrypt_seed_phrase(seed_phrase, password):
    # Validate seed phrase input
    if not seed_phrase:
        raise ValueError("Seed phrase cannot be empty.")
    
    # Generate salt and IV
    salt = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    # Derive key
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    
    # Convert seed phrase to bytes
    seed_bytes = seed_phrase.encode('utf-8')
    
    # Prepare AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the seed phrase
    padded_seed = seed_bytes + b'\0' * (32 - len(seed_bytes) % 32)

    # Encrypt the seed phrase
    encrypted_seed = cipher.encrypt(padded_seed)
    
    # Combine salt, IV, and encrypted seed
    combined = salt + iv + encrypted_seed
    
    # Convert to seed
    seed = words_to_seed(BIP39_WORDLIST[:len(combined) // 4])
    
    # Convert seed to words
    encrypted_seed_words = seed_to_words(seed, BIP39_WORDLIST)
    
    return ' '.join(encrypted_seed_words)

def decrypt_seed_phrase(encrypted_seed_words, password):
    # Convert encrypted seed words back to bytes
    encrypted_words = encrypted_seed_words.split()
    
    # Convert words back to seed
    seed = words_to_seed(encrypted_words)
    
    # Extract salt, IV, and encrypted data
    salt = seed[:16]
    iv = seed[16:32]
    encrypted_seed = seed[32:]
    
    # Derive key
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    
    # Prepare AES cipher for decryption
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt the seed phrase
    decrypted_seed = cipher.decrypt(encrypted_seed).rstrip(b'\0')
    return decrypted_seed.decode('utf-8')

# Function to handle encryption button click
def encrypt_button_click():
    seed_phrase = seed_phrase_entry.get("1.0", "end-1c")
    password = encrypt_password_entry.get()
    
    if not seed_phrase or not password:
        messagebox.showerror("Error", "Please enter both a seed phrase and a password.")
        return

    try:
        encrypted_seed_words = encrypt_seed_phrase(seed_phrase, password)
        encrypted_seed_output.set(encrypted_seed_words)
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Encryption Error", f"An error occurred: {e}")

# Function to handle decryption button click
def decrypt_button_click():
    encrypted_seed_words = encrypted_seed_entry.get()
    password = decrypt_password_entry.get()
    
    if not encrypted_seed_words or not password:
        messagebox.showerror("Error", "Please enter both an encrypted seed and a password.")
        return

    try:
        decrypted_seed = decrypt_seed_phrase(encrypted_seed_words, password)
        decrypted_seed_output.set(decrypted_seed)
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Decryption Error", f"An error occurred: {e}")

# Function to copy the encrypted seed to clipboard
def copy_encrypted_seed():
    encrypted_seed = encrypted_seed_output.get()
    root.clipboard_clear()
    root.clipboard_append(encrypted_seed)
    messagebox.showinfo("Copied", "Encrypted seed copied to clipboard!")

# Function to copy the decrypted seed to clipboard
def copy_decrypted_seed():
    decrypted_seed = decrypted_seed_output.get()
    root.clipboard_clear()
    root.clipboard_append(decrypted_seed)
    messagebox.showinfo("Copied", "Decrypted seed copied to clipboard!")

# Set up the main UI
root = tk.Tk()
root.title("Seed Phrase Encrypt/Decrypt Tool")
root.geometry("600x600")

# Encrypt Section
tk.Label(root, text="Encrypt Seed Phrase", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Seed Phrase:").pack()
seed_phrase_entry = tk.Text(root, height=5, width=70)
seed_phrase_entry.pack()

tk.Label(root, text="Password:").pack()
encrypt_password_entry = tk.Entry(root, show="*", width=70)
encrypt_password_entry.pack()

encrypt_button = tk.Button(root, text="Encrypt", command=encrypt_button_click)
encrypt_button.pack(pady=10)

tk.Label(root, text="Encrypted Seed Phrase:").pack()
encrypted_seed_output = tk.StringVar()
encrypted_seed_label = tk.Entry(root, textvariable=encrypted_seed_output, width=70, state="readonly")
encrypted_seed_label.pack()

copy_encrypted_button = tk.Button(root, text="Copy Encrypted Seed", command=copy_encrypted_seed)
copy_encrypted_button.pack(pady=5)

# Decrypt Section
tk.Label(root, text="Decrypt Encrypted Seed", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="Encrypted Seed Phrase:").pack()
encrypted_seed_entry = tk.Entry(root, width=70)
encrypted_seed_entry.pack()

tk.Label(root, text="Password:").pack()
decrypt_password_entry = tk.Entry(root, show="*", width=70)
decrypt_password_entry.pack()

decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_button_click)
decrypt_button.pack(pady=10)

tk.Label(root, text="Decrypted Seed Phrase:").pack()
decrypted_seed_output = tk.StringVar()
decrypted_seed_label = tk.Entry(root, textvariable=decrypted_seed_output, width=70, state="readonly")
decrypted_seed_label.pack()

copy_decrypted_button = tk.Button(root, text="Copy Decrypted Seed", command=copy_decrypted_seed)
copy_decrypted_button.pack(pady=5)

# Start the main loop
root.mainloop()