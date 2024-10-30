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

def private_key_to_public_key(private_key, compressed=False):
    """
    Generates a public key from a private key, optionally compressing it.
    """
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.verifying_key
    if compressed:
        return b'\x02' + vk.to_string()[:32] if vk.to_string()[32] % 2 == 0 else b'\x03' + vk.to_string()[:32]
    else:
        return b'\x04' + vk.to_string()


