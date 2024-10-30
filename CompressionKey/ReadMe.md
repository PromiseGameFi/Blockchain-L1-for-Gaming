# Ethereum BIP38 Key Compression Tool

This tool decrypts BIP38-encoded keys and outputs Ethereum-compatible addresses and keys in various formats, supporting both compressed and uncompressed keys.

## Features

- **Decryption**: Decrypts BIP38-encoded keys using a password.
- **Address Generation**: Generates Ethereum addresses for both compressed and uncompressed keys.
- **Key Formats**: Outputs public keys in hexadecimal, private keys in Wallet Import Format (WIF), and BIP38-encrypted private keys for both compressed and uncompressed keys.

---

## User Input

1. **BIP38-encoded key**: The encrypted private key in BIP38 format.
2. **BIP38 password**: Password to decrypt the BIP38-encoded key.

---

## Process Overview

### Decryption

1. **Decrypt the BIP38 Key**: Using the provided password, decrypt the BIP38-encoded private key.
2. **Generate Key Formats**: From the decrypted private key, derive both compressed and uncompressed key formats.

### Output

For each key format (compressed and uncompressed):

- **Address**: Ethereum address derived from the public key.
- **Public Key (hex)**: Public key in hexadecimal format.
- **Private Key (WIF)**: Private key in Wallet Import Format.
- **Private Key (BIP38)**: BIP38-encrypted private key.

---
## SetUp

-  python3 -m venv venv
-  source venv/bin/activate  # On Windows: venv\Scripts\activate
-  pip install -r src/requirements.txt
-  python src/main.py

pip install bip38


## Key Steps for Implementation

1. **Decrypting BIP38**:  
   - Use a library that supports BIP38 decryption, such as `bip38` in JavaScript or `pybitcointools` in Python.
   
2. **Generate Ethereum Address**:  
   - Derive the Ethereum address by taking the Keccak-256 hash of the public key, excluding the first byte if the key is uncompressed, and using the last 20 bytes of the hash.

3. **Public Key Compression**:  
   - Convert the public key from uncompressed format (65 bytes) to compressed format (33 bytes) or vice versa, as needed.

4. **BIP38 Encryption**:  
   - Encrypt the private key back into BIP38 format for both compressed and uncompressed versions.

---

## Example

After running the tool, you can expect output similar to the following for both key formats:

```plaintext
Uncompressed Address: 0x1234...abcd
Compressed Address: 0xabcd...1234
Public Key (Hex) Uncompressed: 04a1b2...1234
Public Key (Hex) Compressed: 02a1b2...abcd
Private Key (WIF) Uncompressed: 5HueC...abcdef
Private Key (WIF) Compressed: KwdMA...ghijk
Private Key (BIP38) Uncompressed: 6Pf...xyz
Private Key (BIP38) Compressed: 6Pf...uvw
