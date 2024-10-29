from bip38_utils import decrypt_bip38, encrypt_bip38
from key_utils import private_key_to_wif, private_key_to_public_key, public_key_to_address

def main():
    # User input for BIP38-encoded key and password
    bip38_key = input("Enter BIP38-encoded private key: ")
    password = input("Enter BIP38 password: ")

    # Step 1: Decrypt the BIP38 key
    decrypted_private_key = decrypt_bip38(bip38_key, password)

    # Step 2: Generate and display output for both compressed and uncompressed formats
    formats = ["Uncompressed", "Compressed"]
    for compressed in [False, True]:
        # Public Key and Address
        public_key = private_key_to_public_key(decrypted_private_key, compressed=compressed)
        address = public_key_to_address(public_key)

        # Private Key in WIF format
        private_key_wif = private_key_to_wif(decrypted_private_key, compressed=compressed)

        # BIP38 Encryption of the private key
        bip38_reencrypted = encrypt_bip38(decrypted_private_key, password, compressed=compressed)

        # Display Results
        print(f"\n--- {formats[compressed]} Format ---")
        print("Address:", address)
        print("Public Key (Hex):", public_key.hex())
        print("Private Key (WIF):", private_key_wif)
        print("Private Key (BIP38):", bip38_reencrypted)

if __name__ == "__main__":
    main()
