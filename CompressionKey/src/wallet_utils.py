from bip_utils import Bip38KeyEncoder, Bip38KeyDecoder, Bip44, Bip44Coins

# Encrypt a private key with a password
private_key_wif = "your_private_key_wif"  # Your WIF private key
password = "your_password"
bip38_key = Bip38KeyEncoder.Encode(private_key_wif, password)
print(f"BIP38 Encrypted Key: {bip38_key}")

# Decrypt a BIP38 encoded key with a password
bip38_key = "your_bip38_key"  # Your BIP38 encoded key
password = "your_password"
private_key_wif = Bip38KeyDecoder.Decode(bip38_key, password)
print(f"Private Key (WIF): {private_key_wif}")

# Derive public key and address (compressed and uncompressed)
bip44_mst = Bip44.FromPrivateKey(private_key_wif, Bip44Coins.BITCOIN)
bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(False).AddressIndex(0)

# Compressed
compressed_address = bip44_acc.PublicKey().ToAddress()
compressed_public_key_hex = bip44_acc.PublicKey().RawCompressed().ToHex()
compressed_private_key_wif = bip44_acc.PrivateKey().ToWif()

print(f"Compressed Address: {compressed_address}")
print(f"Compressed Public Key (HEX): {compressed_public_key_hex}")
print(f"Compressed Private Key (WIF): {compressed_private_key_wif}")

# Uncompressed
uncompressed_public_key_hex = bip44_acc.PublicKey().RawUncompressed().ToHex()
uncompressed_private_key_wif = bip44_acc.PrivateKey().RawUncompressed().ToWif()

print(f"Uncompressed Public Key (HEX): {uncompressed_public_key_hex}")
print(f"Uncompressed Private Key (WIF): {uncompressed_private_key_wif}")
