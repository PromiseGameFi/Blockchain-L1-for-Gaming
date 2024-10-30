import binascii

"""
Decrypts
"""

def decrypt_bip38(bip38_key, password):
    """
    Decrypts a BIP38-encoded private key using the provided password.
    """
    try:
        return bip38.decrypt(bip38_key, password)
    except ValueError:
        raise ValueError("Failed to decrypt BIP38 key. Check the password used and key format.")

def encrypt_bip38(private_key, password, compressed=False):
    """
    Encrypts a private key with a password in BIP38 format.
    """
    try:
        # Convert private key to hex and prepare for encryption
        private_key_hex = binascii.hexlify(private_key).decode()
        return bip38.encrypt(private_key_hex, password, compressed=compressed)
    except Exception as e:
        raise ValueError(f"BIP38 encryption failed: {e}")
