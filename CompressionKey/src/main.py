import binascii
import hashlib
from ecdsa import SigningKey, SECP256k1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import base58
import scrypt

class Bip38:
    @staticmethod
    def encrypt(private_key, passphrase, compressed=False):
        # Basic BIP38 encryption implementation
        salt = os.urandom(8)
        key = scrypt.hash(passphrase.encode(), salt, 16384, 8, 8, 64)
        
        half1 = key[:32]
        half2 = key[32:]
        
        # Ensure the private key is padded correctly for AES
        if len(private_key) < 32:
            private_key = private_key.rjust(32, b'\x00')
        
        
        
        result = b'\x01\x42' + (b'\xe0' if compressed else b'\xc0') + salt + encrypted
        checksum = hashlib.sha256(hashlib.sha256(result).digest()).digest()[:4]
        
        return base58.b58encode(result + checksum).decode()

    @staticmethod
    def decrypt(encrypted_key, passphrase):
        try:
            # Decode the BIP38 key
            data = base58.b58decode(encrypted_key)
            
            # Verify checksum
            if hashlib.sha256(hashlib.sha256(data[:-4]).digest()).digest()[:4] != data[-4:]:
                raise ValueError("Invalid checksum")
            
            # Extract components
            if data[0] != 0x01 or data[1] != 0x42:
                raise ValueError("Invalid BIP38 key format")
            
            flag = data[2]
            salt = data[3:11]
            encrypted = data[11:-4]
            
            # Derive key using scrypt
            key = scrypt.hash(passphrase.encode(), salt, 16384, 8, 8, 64)
            half1 = key[:32]
            half2 = key[32:]
            
            # Decrypt
            aes = AES.new(half2, AES.MODE_ECB)
            decrypted = aes.decrypt(encrypted)
            
            try:
                decrypted = unpad(decrypted, AES.block_size)
            except ValueError:
                # If unpadding fails, try without unpadding
                pass
            
            # Check if compressed flag is present
            is_compressed = bool(flag & 0x20)
            if is_compressed and decrypted[-1] == 0x01:
                decrypted = decrypted[:-1]
            
            # Ensure we have a 32-byte private key
            if len(decrypted) > 32:
                decrypted = decrypted[:32]
            elif len(decrypted) < 32:
                decrypted = decrypted.rjust(32, b'\x00')
            
            return decrypted, is_compressed
            
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None, None

def private_key_to_wif(private_key, compressed=False):
    if private_key is None:
        raise ValueError("Invalid private key. Decryption might have failed.")
        
    prefix = b'\x80'  # Mainnet prefix
    key_data = private_key
    if compressed:
        key_data += b'\x01'  # Add compressed byte
    extended_key = prefix + key_data
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    return base58.b58encode(extended_key + checksum).decode()

def private_key_to_public_key(private_key, compressed=False):
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.verifying_key
    if compressed:
        return b'\x02' + vk.to_string()[:32] if vk.to_string()[32] % 2 == 0 else b'\x03' + vk.to_string()[:32]
    return b'\x04' + vk.to_string()

def public_key_to_address(public_key):
    keccak = hashlib.new('keccak256')
    keccak.update(public_key[1:] if public_key[0] == 0x04 else public_key)
    return '0x' + keccak.hexdigest()[-40:]

def main():
    print("Ethereum BIP38 Key Compression Tool")
    print("-" * 50)
    
    # Get user input
    bip38_key = input("Enter BIP38-encoded key: ").strip()
    password = input("Enter BIP38 password: ").strip()
    
    # Initialize BIP38 handler
    bip38_handler = Bip38()
    
    # Decrypt BIP38 Key
    decrypted_private_key, is_compressed = bip38_handler.decrypt(bip38_key, password)
    
    if decrypted_private_key is not None:
        try:
            # Generate keys and addresses for both formats
            results = {}
            for compressed in [False, True]:
                format_type = "Compressed" if compressed else "Uncompressed"
                results[format_type] = {
                    "public_key": private_key_to_public_key(decrypted_private_key, compressed),
                    "wif": private_key_to_wif(decrypted_private_key, compressed),
                    "bip38": bip38_handler.encrypt(decrypted_private_key, password, compressed)
                }
                results[format_type]["address"] = public_key_to_address(results[format_type]["public_key"])
            
            # Output results
            print("\nResults:")
            print("-" * 50)
            for format_type, data in results.items():
                print(f"\n{format_type} Format:")
                print(f"Address: {data['address']}")
                print(f"Public Key (Hex): {binascii.hexlify(data['public_key']).decode()}")
                print(f"Private Key (WIF): {data['wif']}")
                print(f"Private Key (BIP38): {data['bip38']}")
        except Exception as e:
            print(f"Error processing keys: {e}")
    else:
        print("Decryption failed; unable to continue.")

if __name__ == "__main__":
    main()