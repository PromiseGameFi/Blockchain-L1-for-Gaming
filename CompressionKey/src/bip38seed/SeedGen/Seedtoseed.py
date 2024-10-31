# seed_phrase_tool.py

import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import binascii
import random
from word_list import WORD_LIST  # Import the word list

# Function to generate a random seed phrase
def generate_seed_phrase(word_count=12):
    return ' '.join(random.choice(WORD_LIST) for _ in range(word_count))

# Function to convert a byte array to a seed phrase
def bytes_to_seed_phrase(encrypted_bytes):
    indices = [b % len(WORD_LIST) for b in encrypted_bytes]  # Convert bytes to indices
    return ' '.join(WORD_LIST[i] for i in indices)

# Function to convert a seed phrase back to a byte array
def seed_phrase_to_bytes(seed_phrase):
    indices = [WORD_LIST.index(word) for word in seed_phrase.split() if word in WORD_LIST]  # Get indices of words
    return bytes(indices)

# Encrypt function using AES-256-CBC
def encrypt_seed_phrase(seed_phrase, password):
    if not seed_phrase:
        raise ValueError("Seed phrase cannot be empty.")

    salt = get_random_bytes(16)  # Generate a 16-byte salt
    iv = get_random_bytes(16)    # Generate a 16-byte IV for AES
    key = PBKDF2(password, salt, dkLen=32, count=1000000)  # Derive a 32-byte key

    # Convert seed phrase to bytes
    seed_bytes = seed_phrase_to_bytes(seed_phrase)

    # Prepare AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the seed bytes to 32 bytes if necessary
    padded_seed = seed_bytes + b'\0' * (32 - len(seed_bytes) % 32)

    # Encrypt the seed phrase
    encrypted_seed = cipher.encrypt(padded_seed)

    # Return salt, IV, and encrypted seed as hex for storage
    return binascii.hexlify(salt + iv + encrypted_seed).decode()

# Decrypt function using AES-256-CBC
def decrypt_seed_phrase(encrypted_hex, password):
    encrypted_data = binascii.unhexlify(encrypted_hex)
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_seed = encrypted_data[32:]

    # Derive the key using the same password and salt
    key = PBKDF2(password, salt, dkLen=32, count=1000000)

    # Prepare AES cipher in CBC mode for decryption
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the seed phrase and strip padding
    decrypted_seed = cipher.decrypt(encrypted_seed).rstrip(b'\0')
    return bytes_to_seed_phrase(decrypted_seed)

# Function to handle encryption button click
def encrypt_button_click():
    seed_phrase = seed_phrase_entry.get("1.0", "end-1c").strip()
    password = encrypt_password_entry.get()

    if not seed_phrase or not password:
        messagebox.showerror("Error", "Please enter both a seed phrase and a password.")
        return

    try:
        encrypted_seed = encrypt_seed_phrase(seed_phrase, password)
        encrypted_seed_output.set(encrypted_seed)
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Encryption Error", f"An error occurred: {e}")

# Function to handle decryption button click
def decrypt_button_click():
    encrypted_seed = encrypted_seed_entry.get()
    password = decrypt_password_entry.get()

    if not encrypted_seed or not password:
        messagebox.showerror("Error", "Please enter both an encrypted seed and a password.")
        return

    try:
        decrypted_seed = decrypt_seed_phrase(encrypted_seed, password)
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

tk.Label(root, text="Encrypted Seed:").pack()
encrypted_seed_output = tk.StringVar()
encrypted_seed_label = tk.Entry(root, textvariable=encrypted_seed_output, width=70, state="readonly")
encrypted_seed_label.pack()

copy_encrypted_button = tk.Button(root, text="Copy Encrypted Seed", command=copy_encrypted_seed)
copy_encrypted_button.pack(pady=5)

# Decrypt Section
tk.Label(root, text="Decrypt Encrypted Seed", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="Encrypted Seed:").pack()
encrypted_seed_entry = tk.Entry(root, width=70)
encrypted_seed_entry.pack()

tk.Label(root, text="Password:").pack()
decrypt_password_entry = tk.Entry(root, show="*", width=70)
decrypt_password_entry.pack()

decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_button_click)
decrypt_button.pack(pady=10)

tk.Label(root, text="Decrypted Seed:").pack()
decrypted_seed_output = tk.StringVar()
decrypted_seed_label = tk.Entry(root, textvariable=decrypted_seed_output, width=70, state="readonly")
decrypted_seed_label.pack()

copy_decrypted_button = tk.Button(root, text="Copy Decrypted Seed", command=copy_decrypted_seed)
copy_decrypted_button.pack(pady=5)

# Generate Random Seed Phrase Button
generate_button = tk.Button(root, text="Generate Random Seed Phrase", command=lambda: seed_phrase_entry.insert("1.0", generate_seed_phrase(12)))
generate_button.pack(pady=10)

root.mainloop()
