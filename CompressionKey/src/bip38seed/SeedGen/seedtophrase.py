import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import binascii
from word_list import BIP39_WORDLIST
# Word list for generating seed phrases (BIP39 word list)
 
def bytes_to_words(data):
    """Convert bytes to a 24-word seed phrase"""
    binary = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
    words = []
    for i in range(0, len(binary), 11):
        chunk = binary[i:i+11]
        if len(chunk) < 11:
            chunk = chunk.ljust(11, '0')
        index = int(chunk, 2)
        words.append(BIP39_WORDLIST[index % len(BIP39_WORDLIST)])
    return ' '.join(words[:24])  # Ensure exactly 24 words

def words_to_bytes(seed_phrase):
    """Convert a 24-word seed phrase back to bytes"""
    words = seed_phrase.strip().split()
    if len(words) != 24:
        raise ValueError("Seed phrase must be exactly 24 words")
    
    binary = ''
    for word in words:
        try:
            index = BIP39_WORDLIST.index(word.lower())
            binary += format(index, '011b')
        except ValueError:
            raise ValueError(f"Invalid word in seed phrase: {word}")
    
    # Convert binary string back to bytes
    byte_length = len(binary) // 8
    return int(binary[:byte_length * 8], 2).to_bytes(byte_length, 'big')

def encrypt_seed_phrase(seed_phrase, password):
    # Validate seed phrase input
    if not seed_phrase:
        raise ValueError("Seed phrase cannot be empty.")
    
    salt = get_random_bytes(16)  # Generate a 16-byte salt
    iv = get_random_bytes(16)    # Generate a 16-byte IV for AES
    key = PBKDF2(password, salt, dkLen=32, count=1000000)  # Derive a 32-byte key
    
    # Convert seed phrase to bytes
    seed_bytes = seed_phrase.encode('utf-8')
    
    # Prepare AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the seed phrase to 32 bytes if necessary
    padded_seed = seed_bytes + b'\0' * (32 - len(seed_bytes) % 32)
    
    # Encrypt the seed phrase
    encrypted_seed = cipher.encrypt(padded_seed)
    
    # Combine salt, IV, and encrypted seed
    combined_data = salt + iv + encrypted_seed
    
    # Convert to 24-word seed phrase
    return bytes_to_words(combined_data)

def decrypt_seed_phrase(encrypted_seed_phrase, password):
    try:
        # Convert 24-word seed phrase back to bytes
        encrypted_data = words_to_bytes(encrypted_seed_phrase)
        
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted_seed = encrypted_data[32:]
        
        # Derive the key using the same password and salt
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        
        # Prepare AES cipher in CBC mode for decryption
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt the seed phrase and strip padding
        decrypted_seed = cipher.decrypt(encrypted_seed).rstrip(b'\0')
        return decrypted_seed.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

# Function to handle encryption button click
def encrypt_button_click():
    seed_phrase = seed_phrase_entry.get("1.0", "end-1c")
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

tk.Label(root, text="Encrypted Seed (24 words):").pack()
encrypted_seed_output = tk.StringVar()
encrypted_seed_label = tk.Entry(root, textvariable=encrypted_seed_output, width=70, state="readonly")
encrypted_seed_label.pack()

copy_encrypted_button = tk.Button(root, text="Copy Encrypted Seed", command=copy_encrypted_seed)
copy_encrypted_button.pack(pady=5)

# Decrypt Section
tk.Label(root, text="Decrypt Encrypted Seed", font=("Arial", 14)).pack(pady=20)

tk.Label(root, text="Encrypted Seed (24 words):").pack()
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