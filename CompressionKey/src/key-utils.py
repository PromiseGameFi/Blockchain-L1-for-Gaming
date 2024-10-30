import binascii
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58


def private_key_to_wif(private_key, compressed=False):
    """
    Converts a private key to Wallet Import Format (WIF).
    """
    prefix = b'\x80'  # Prefix for mainnet
    extended_key = prefix + private_key + (b'\x01' if compressed else b'')
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    return base58.b58encode(extended_key + checksum).decode()




