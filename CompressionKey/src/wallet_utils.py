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

# Derive public key and address
bip44_mst = Bip44.FromPrivateKey(private_key_wif, Bip44Coins.BITCOIN)
bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(False).AddressIndex(0)
address = bip44_acc.PublicKey().ToAddress()
public_key_hex = bip44_acc.PublicKey().RawCompressed().ToHex()
private_key_uncompressed_wif = bip44_acc.PrivateKey().RawUncompressed().ToWif()
private_key_compressed_wif = bip44_acc.PrivateKey().ToWif()

print(f"Address: {address}")
print(f"Public Key (HEX): {public_key_hex}")
print(f"Private Key (Uncompressed WIF): {private_key_uncompressed_wif}")
print(f"Private Key (Compressed WIF): {private_key_compressed_wif}")
